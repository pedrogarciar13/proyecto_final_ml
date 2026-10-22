"""Estabilidad de las métricas, costo del error y umbral de decisión.

Uso:  python -m src.robustness   (requiere haber ejecutado src.train)

1. Validación cruzada repetida (5 pliegues x 5 repeticiones) de la mejor
   configuración de cada modelo: qué tanto varía el F1 macro con la partición.
2. Bootstrap del conjunto de prueba (1.000 remuestreos): intervalos de
   confianza del 95 % y diferencias pareadas entre modelos.
3. Umbral para la alerta «Alto»: se elige con predicciones fuera de pliegue
   del ENTRENAMIENTO (no con el test) y luego se reporta una vez en prueba.
"""
from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import confusion_matrix, f1_score, make_scorer, precision_score, recall_score
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_predict, cross_validate
from sklearn.utils.class_weight import compute_sample_weight

from src import config
from src.data_processing import get_X_y, prepare_dataset, split_data
from src.modeling import get_model_specs
from src.train import CANDIDATES_PATH, cv_splitter

ALTO = config.CLASS_TO_CODE["Alto"]
BAJO = config.CLASS_TO_CODE["Bajo"]
N_BOOT = 1000


def _fit_params(spec, y):
    return {"modelo__sample_weight": compute_sample_weight("balanced", y)} if spec.uses_sample_weight else {}


def repeated_cv(candidates, specs, X_train, y_train) -> pd.DataFrame:
    scoring = {"f1_macro": "f1_macro", "balanced_accuracy": "balanced_accuracy"}
    for cls, code in config.CLASS_TO_CODE.items():
        scoring[f"f1_{cls}"] = make_scorer(f1_score, labels=[code], average="macro")
    rkf = RepeatedStratifiedKFold(n_splits=config.CV_FOLDS, n_repeats=5, random_state=config.RANDOM_STATE)
    rows = []
    for spec in specs:
        res = cross_validate(clone(candidates[spec.name]), X_train, y_train, cv=rkf, scoring=scoring,
                             n_jobs=-1, params=_fit_params(spec, y_train))
        row = {"modelo": spec.name, "nombre": spec.nombre_es, "evaluaciones": len(res["test_f1_macro"])}
        for key in scoring:
            v = res[f"test_{key}"]
            row[f"{key}_media"], row[f"{key}_desv"] = v.mean(), v.std()
        row["f1_macro_min"], row["f1_macro_max"] = res["test_f1_macro"].min(), res["test_f1_macro"].max()
        rows.append(row)
    return pd.DataFrame(rows)


def bootstrap_test(preds: dict, y_test: np.ndarray, reference: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(config.RANDOM_STATE)
    n = len(y_test)
    idx = rng.integers(0, n, size=(N_BOOT, n))
    scores = {k: np.array([f1_score(y_test[i], p[i], average="macro") for i in idx]) for k, p in preds.items()}
    ci = pd.DataFrame([{"modelo": k, "f1_macro": f1_score(y_test, preds[k], average="macro"),
                        "ic95_inf": np.percentile(s, 2.5), "ic95_sup": np.percentile(s, 97.5)}
                       for k, s in scores.items()])
    diffs = []
    for k, s in scores.items():
        if k == reference:
            continue
        d = s - scores[reference]
        diffs.append({"comparacion": f"{k} - {reference}", "diferencia": d.mean(),
                      "ic95_inf": np.percentile(d, 2.5), "ic95_sup": np.percentile(d, 97.5),
                      "prop_remuestreos_mayor": (d > 0).mean()})
    return ci, pd.DataFrame(diffs)


def error_costs(preds: dict, y_test: np.ndarray) -> pd.DataFrame:
    """Errores según su gravedad: entre clases vecinas o extremos (Alto <-> Bajo)."""
    rows = []
    for k, p in preds.items():
        cm = confusion_matrix(y_test, p, labels=[0, 1, 2])
        n = cm.sum()
        rows.append({
            "modelo": k,
            "aciertos_pct": np.trace(cm) / n * 100,
            "error_vecino_pct": (cm[0, 1] + cm[1, 0] + cm[1, 2] + cm[2, 1]) / n * 100,
            "error_extremo_pct": (cm[0, 2] + cm[2, 0]) / n * 100,
            "alto_no_detectado_pct": (cm[0, 1] + cm[0, 2]) / cm[0].sum() * 100,
            "alto_clasificado_bajo_pct": cm[0, 2] / cm[0].sum() * 100,
            "bajo_clasificado_alto_pct": cm[2, 0] / cm[2].sum() * 100,
        })
    return pd.DataFrame(rows)


def alto_threshold(pipe, spec, X_train, y_train, X_test, y_test) -> tuple[pd.DataFrame, dict]:
    """Curva de umbral para la alerta «Alto» (uno contra el resto).

    El umbral se elige con probabilidades fuera de pliegue del entrenamiento
    maximizando F2 (el recall pesa el doble que la precisión, porque no
    detectar un negocio de riesgo alto cuesta más que una alerta de más).
    """
    oof = cross_val_predict(clone(pipe), X_train, y_train, cv=cv_splitter(), method="predict_proba",
                            params=_fit_params(spec, y_train))[:, ALTO]
    y_bin = (np.asarray(y_train) == ALTO).astype(int)
    thresholds = np.unique(np.round(oof, 4))
    rows = []
    for t in thresholds:
        pred = (oof >= t).astype(int)
        p = precision_score(y_bin, pred, zero_division=0)
        r = recall_score(y_bin, pred, zero_division=0)
        f2 = 5 * p * r / (4 * p + r) if (p + r) else 0.0
        f1 = 2 * p * r / (p + r) if (p + r) else 0.0
        rows.append({"umbral": float(t), "precision": p, "recall": r, "f1": f1, "f2": f2,
                     "alertas_pct": pred.mean() * 100})
    curve = pd.DataFrame(rows)
    best = curve.loc[curve["f2"].idxmax()]

    proba_test = pipe.predict_proba(X_test)[:, ALTO]
    yt = (np.asarray(y_test) == ALTO).astype(int)
    argmax_pred = (pipe.predict(X_test) == ALTO).astype(int)
    out = {"umbral_elegido": float(best["umbral"]), "criterio": "max F2 en predicciones fuera de pliegue (train)",
           "oof": best.to_dict()}
    for label, pred in (("prueba_umbral_elegido", (proba_test >= best["umbral"]).astype(int)),
                        ("prueba_regla_por_defecto", argmax_pred)):
        p = precision_score(yt, pred, zero_division=0)
        r = recall_score(yt, pred, zero_division=0)
        out[label] = {"precision": p, "recall": r, "f2": 5 * p * r / (4 * p + r) if (p + r) else 0.0,
                      "alertas_pct": pred.mean() * 100}
    return curve, out


def main() -> None:
    cand = joblib.load(CANDIDATES_PATH)["modelos"]
    final = joblib.load(config.MODEL_PATH)["nombre_modelo"]
    specs = get_model_specs()
    X, y = get_X_y(prepare_dataset())
    X_train, X_test, y_train, y_test = split_data(X, y)

    rcv = repeated_cv(cand, specs, X_train, y_train)
    rcv.to_csv(config.TABLES_DIR / "cv_repetida.csv", index=False)
    print(rcv.round(4).to_string(index=False))

    yt = np.asarray(y_test)
    preds = {k: np.asarray(p.predict(X_test)) for k, p in cand.items()}
    rng = np.random.default_rng(config.RANDOM_STATE)
    preds["azar_estratificado"] = rng.choice([0, 1, 2], size=len(yt), p=np.bincount(y_train) / len(y_train))
    preds["siempre_bajo"] = np.full(len(yt), BAJO)
    ci, diffs = bootstrap_test(preds, yt, final)
    ci.to_csv(config.TABLES_DIR / "bootstrap_prueba.csv", index=False)
    diffs.to_csv(config.TABLES_DIR / "bootstrap_diferencias.csv", index=False)
    print(ci.round(4).to_string(index=False)); print(diffs.round(4).to_string(index=False))

    costs = error_costs({k: v for k, v in preds.items()}, yt)
    costs.to_csv(config.TABLES_DIR / "costo_errores_prueba.csv", index=False)
    print(costs.round(2).to_string(index=False))

    spec = next(s for s in specs if s.name == final)
    curve, chosen = alto_threshold(cand[final], spec, X_train, y_train, X_test, y_test)
    curve.to_csv(config.TABLES_DIR / "umbral_alto_curva.csv", index=False)
    with open(config.TABLES_DIR / "umbral_alto.json", "w", encoding="utf-8") as fh:
        json.dump(chosen, fh, ensure_ascii=False, indent=2, default=float)
    print(curve.round(3).to_string(index=False)); print(json.dumps(chosen, indent=1, default=float))


if __name__ == "__main__":
    main()
