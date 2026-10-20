"""Entrenamiento y comparación de los cuatro modelos con validación cruzada.

Uso:  python -m src.train

* El conjunto de prueba (20 %) se separa al inicio y NO se usa aquí.
* Cada modelo se ajusta con búsqueda de hiperparámetros sobre CV estratificada
  de 5 pliegues usando solo el 80 % de entrenamiento. Métrica principal: F1 macro.
* El modelo final se elige con los resultados de CV (no con el test).
"""
from __future__ import annotations

import json
import platform
import time
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
import sklearn
import xgboost
from sklearn.model_selection import (GridSearchCV, RandomizedSearchCV,
                                     StratifiedKFold, cross_validate)
from sklearn.utils.class_weight import compute_sample_weight

from src import config
from src.data_processing import (get_X_y, leakage_audit_table, prepare_dataset,
                                 split_data, target_distribution)
from src.modeling import ModelSpec, get_model_specs

SCORING = {
    "f1_macro": "f1_macro",
    "balanced_accuracy": "balanced_accuracy",
    "accuracy": "accuracy",
    "f1_weighted": "f1_weighted",
}
CANDIDATES_PATH = config.MODELS_DIR / "candidatos.joblib"


def cv_splitter() -> StratifiedKFold:
    return StratifiedKFold(n_splits=config.CV_FOLDS, shuffle=True, random_state=config.RANDOM_STATE)


def tune_model(spec: ModelSpec, X_train: pd.DataFrame, y_train: pd.Series):
    """Busca hiperparámetros con CV y devuelve el buscador ajustado."""
    common = dict(scoring=SCORING, refit=config.PRIMARY_METRIC, cv=cv_splitter(),
                  n_jobs=-1, return_train_score=True)
    if spec.search == "grid":
        search = GridSearchCV(spec.pipeline(), spec.param_space, **common)
    else:
        search = RandomizedSearchCV(spec.pipeline(), spec.param_space, n_iter=spec.n_iter,
                                    random_state=config.RANDOM_STATE, **common)
    fit_params = {}
    if spec.uses_sample_weight:
        # Los pesos se pasan por muestra; GridSearch los recorta en cada pliegue,
        # por lo que solo se usan pesos del pliegue de entrenamiento.
        fit_params["modelo__sample_weight"] = compute_sample_weight("balanced", y_train)
    search.fit(X_train, y_train, **fit_params)
    return search


def summarize_search(spec: ModelSpec, search) -> dict:
    res = pd.DataFrame(search.cv_results_)
    best = res.loc[search.best_index_]
    summary = {
        "modelo": spec.name,
        "nombre": spec.nombre_es,
        "combinaciones_evaluadas": int(len(res)),
        "mejores_hiperparametros": {k.replace("modelo__", ""): (v.item() if hasattr(v, "item") else v)
                                    for k, v in search.best_params_.items()},
    }
    for m in SCORING:
        summary[f"cv_{m}_media"] = float(best[f"mean_test_{m}"])
        summary[f"cv_{m}_desv"] = float(best[f"std_test_{m}"])
    summary["train_f1_macro_media"] = float(best["mean_train_f1_macro"])
    return summary


def select_final_model(summaries: list[dict], specs: list[ModelSpec]) -> str:
    """Regla de una desviación estándar (aplicada solo con resultados de CV).

    1. Se toma el modelo con mejor F1 macro medio de CV.
    2. Se consideran estadísticamente equivalentes los modelos cuya media está
       a menos de una desviación estándar (entre pliegues) del mejor.
    3. Entre los equivalentes se elige el más simple e interpretable
       (regresión logística < árbol < random forest < XGBoost).
    """
    rank = {s.name: s.complexity_rank for s in specs}
    best = max(summaries, key=lambda s: s["cv_f1_macro_media"])
    threshold = best["cv_f1_macro_media"] - best["cv_f1_macro_desv"]
    tied = [s for s in summaries if s["cv_f1_macro_media"] >= threshold]
    return min(tied, key=lambda s: rank[s["modelo"]])["modelo"]


def sensitivity_analysis(spec: ModelSpec, best_params: dict, X_train, y_train) -> pd.DataFrame:
    """F1 macro de CV del modelo elegido quitando variables sensibles.

    Sirve para documentar cuánto depende el modelo de le_deja_al_mes_COP y de
    edad_propietario. Solo usa datos de entrenamiento.
    """
    scenarios = {
        "Todas las variables aprobadas": config.FEATURES,
        "Sin le_deja_al_mes_COP": [f for f in config.FEATURES if f != "le_deja_al_mes_COP"],
        "Sin edad_propietario": [f for f in config.FEATURES if f != "edad_propietario"],
        "Sin ingreso ni edad": [f for f in config.FEATURES if f not in ("le_deja_al_mes_COP", "edad_propietario")],
    }
    rows = []
    for label, feats in scenarios.items():
        pipe = spec.pipeline(feats).set_params(**{f"modelo__{k}": v for k, v in best_params.items()})
        params = {}
        if spec.uses_sample_weight:
            params["modelo__sample_weight"] = compute_sample_weight("balanced", y_train)
        cv = cross_validate(pipe, X_train[feats], y_train, cv=cv_splitter(),
                            scoring=["f1_macro", "balanced_accuracy"], n_jobs=-1, params=params)
        rows.append({"escenario": label, "n_variables": len(feats),
                     "cv_f1_macro": cv["test_f1_macro"].mean(),
                     "cv_f1_macro_desv": cv["test_f1_macro"].std(),
                     "cv_balanced_accuracy": cv["test_balanced_accuracy"].mean()})
    return pd.DataFrame(rows)


def form_options(X_train: pd.DataFrame) -> dict:
    """Opciones del formulario tomadas de las categorías reales de entrenamiento."""
    cats = {}
    for col in config.CATEGORICAL_FEATURES + config.BINARY_FEATURES:
        counts = X_train[col].value_counts()
        cats[col] = [{"valor": k, "n_entrenamiento": int(v)} for k, v in counts.items()]
    nums = {col: {"min": float(X_train[col].min()), "max": float(X_train[col].max()),
                  "mediana": float(X_train[col].median())} for col in config.NUMERIC_FEATURES}
    return {"categoricas": cats, "numericas": nums}


def main() -> None:
    t0 = time.time()
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)

    df = prepare_dataset()
    X, y = get_X_y(df)
    X_train, X_test, y_train, y_test = split_data(X, y)
    for forbidden in ("meses_abierto", "nivel_riesgo", "riesgo_financiero", "id_negocio"):
        assert forbidden not in X_train.columns, f"{forbidden} no puede estar en X"
    print(f"Registros: {len(df)} | train: {len(X_train)} | test: {len(X_test)}")
    print("Predictoras:", list(X_train.columns))

    target_distribution(df).to_csv(config.TABLES_DIR / "distribucion_nivel_riesgo.csv")
    leakage_audit_table().to_csv(config.TABLES_DIR / "auditoria_variables.csv", index=False)

    specs = get_model_specs()
    summaries, fitted = [], {}
    for spec in specs:
        t = time.time()
        search = tune_model(spec, X_train, y_train)
        s = summarize_search(spec, search)
        s["segundos"] = round(time.time() - t, 1)
        summaries.append(s)
        fitted[spec.name] = search.best_estimator_
        pd.DataFrame(search.cv_results_).to_csv(config.TABLES_DIR / f"cv_resultados_{spec.name}.csv", index=False)
        print(f"{spec.nombre_es:22s} CV F1 macro = {s['cv_f1_macro_media']:.4f} ± {s['cv_f1_macro_desv']:.4f} "
              f"| bal.acc = {s['cv_balanced_accuracy_media']:.4f} | {s['mejores_hiperparametros']}")

    cv_table = pd.DataFrame(summaries)
    cv_table.to_csv(config.TABLES_DIR / "comparacion_cv.csv", index=False)

    final_name = select_final_model(summaries, specs)
    final_spec = next(s for s in specs if s.name == final_name)
    final_summary = next(s for s in summaries if s["modelo"] == final_name)
    print(f"\nModelo seleccionado por CV: {final_spec.nombre_es}")

    sens = sensitivity_analysis(final_spec, final_summary["mejores_hiperparametros"], X_train, y_train)
    sens.to_csv(config.TABLES_DIR / "sensibilidad_variables.csv", index=False)
    print(sens.round(4).to_string(index=False))

    joblib.dump({"modelos": fitted, "resumen_cv": summaries}, CANDIDATES_PATH, compress=3)

    artifact = {
        "pipeline": fitted[final_name],
        "nombre_modelo": final_name,
        "nombre_modelo_es": final_spec.nombre_es,
        "variables": config.FEATURES,
        "clases": config.CLASS_ORDER,
        "regla_objetivo": {
            "fuente": config.TARGET_SOURCE,
            "Alto": f"1 a {config.LIMITE_ALTO_MAX} meses",
            "Medio": f"{config.LIMITE_ALTO_MAX + 1} a {config.LIMITE_MEDIO_MAX} meses",
            "Bajo": f"{config.LIMITE_MEDIO_MAX + 1} meses o más",
        },
        "opciones_formulario": form_options(X_train),
        "resumen_cv": final_summary,
        "semilla": config.RANDOM_STATE,
        "entrenado_en": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "versiones": {"python": platform.python_version(), "scikit-learn": sklearn.__version__,
                      "xgboost": xgboost.__version__, "pandas": pd.__version__, "numpy": np.__version__},
    }
    joblib.dump(artifact, config.MODEL_PATH, compress=3)
    with open(config.TABLES_DIR / "seleccion_modelo.json", "w", encoding="utf-8") as fh:
        json.dump({"modelo_final": final_name, "criterio": select_final_model.__doc__.strip(),
                   "resumen_cv": summaries}, fh, ensure_ascii=False, indent=2, default=str)
    print(f"\nModelo guardado en {config.MODEL_PATH.relative_to(config.ROOT_DIR)} "
          f"({time.time() - t0:.0f} s)")


if __name__ == "__main__":
    main()
