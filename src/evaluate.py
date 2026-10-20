"""Evaluación final en el conjunto de prueba e interpretabilidad.

Uso:  python -m src.evaluate   (requiere haber ejecutado antes ``python -m src.train``)

El conjunto de prueba se reconstruye con la misma semilla y se usa una sola
vez, después de haber elegido el modelo con validación cruzada.
"""
from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import (accuracy_score, balanced_accuracy_score, brier_score_loss,
                             classification_report, confusion_matrix, f1_score, log_loss,
                             precision_score, recall_score)
from sklearn.tree import export_text, plot_tree

from src import config
from src.data_processing import get_X_y, prepare_dataset, split_data
from src.modeling import get_model_specs
from src.train import CANDIDATES_PATH
from src.viz import (ACCENT, CLASS_COLORS, INK_2, MODEL_COLORS, SEQ_CMAP, apply_style,
                     plt, save)

LABELS = list(range(len(config.CLASS_ORDER)))


def compute_metrics(y_true, y_pred, y_proba=None) -> dict:
    out = {
        "accuracy": accuracy_score(y_true, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "precision_macro": precision_score(y_true, y_pred, average="macro", zero_division=0),
        "recall_macro": recall_score(y_true, y_pred, average="macro", zero_division=0),
        "f1_macro": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "f1_weighted": f1_score(y_true, y_pred, average="weighted", zero_division=0),
    }
    if y_proba is not None:
        onehot = np.eye(len(LABELS))[np.asarray(y_true)]
        out["log_loss"] = log_loss(y_true, y_proba, labels=LABELS)
        out["brier_medio"] = float(np.mean([brier_score_loss(onehot[:, k], y_proba[:, k]) for k in LABELS]))
    return out


def per_class_table(name: str, y_true, y_pred) -> pd.DataFrame:
    rep = classification_report(y_true, y_pred, labels=LABELS, target_names=config.CLASS_ORDER,
                                output_dict=True, zero_division=0)
    rows = [{"modelo": name, "clase": c, "precision": rep[c]["precision"], "recall": rep[c]["recall"],
             "f1": rep[c]["f1-score"], "soporte": int(rep[c]["support"])} for c in config.CLASS_ORDER]
    return pd.DataFrame(rows)


def plot_confusion_matrices(cms: dict, names: dict, final: str) -> str:
    fig, axes = plt.subplots(1, len(cms), figsize=(4.2 * len(cms), 4.1))
    for ax, (key, cm) in zip(axes, cms.items()):
        pct = cm / cm.sum(axis=1, keepdims=True) * 100
        ax.imshow(pct, cmap=SEQ_CMAP, vmin=0, vmax=100)
        for i in range(3):
            for j in range(3):
                ax.text(j, i, f"{cm[i, j]}\n{pct[i, j]:.0f} %", ha="center", va="center", fontsize=9,
                        color="#fcfcfb" if pct[i, j] > 55 else "#0b0b0b")
        ax.set_xticks(range(3), config.CLASS_ORDER)
        ax.set_yticks(range(3), config.CLASS_ORDER)
        ax.set_xlabel("Predicho")
        ax.set_ylabel("Real" if ax is axes[0] else "")
        ax.grid(False)
        ax.set_title(names[key] + ("  ★ final" if key == final else ""), fontsize=10)
    fig.suptitle(f"Matrices de confusión en prueba (n = {cm.sum()}) · % por fila = recall",
                 x=0.01, ha="left", fontweight="bold")
    fig.tight_layout()
    return save(fig, "05_matrices_confusion.png")


def plot_model_comparison(table: pd.DataFrame) -> str:
    metrics = ["f1_macro", "balanced_accuracy", "accuracy"]
    labels = {"f1_macro": "F1 macro", "balanced_accuracy": "Balanced accuracy", "accuracy": "Accuracy"}
    fig, ax = plt.subplots(figsize=(9, 4))
    models = [m for m in table.index if m != "baseline_estratificado"]
    width = 0.8 / len(models)
    for k, m in enumerate(models):
        vals = table.loc[m, metrics].values
        xs = np.arange(len(metrics)) + (k - (len(models) - 1) / 2) * width
        ax.bar(xs, vals, width=width * 0.9, color=MODEL_COLORS.get(m, "#898781"), label=table.loc[m, "nombre"])
        for x, v in zip(xs, vals):
            ax.text(x, v + 0.008, f"{v:.2f}", ha="center", fontsize=7.5, color=INK_2)
    base = table.loc["baseline_estratificado", metrics].values
    for i, v in enumerate(base):
        ax.hlines(v, i - 0.45, i + 0.45, colors="#0b0b0b", linestyles=":", lw=1.2,
                  label="Azar estratificado" if i == 0 else None)
    ax.set_xticks(range(len(metrics)), [labels[m] for m in metrics])
    ax.set_ylim(0, max(0.75, table[metrics].values.max() + 0.08))
    ax.set_title("Comparación de modelos en el conjunto de prueba")
    ax.legend(ncol=3, fontsize=8, loc="upper left")
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return save(fig, "06_comparacion_modelos.png")


def plot_per_class_f1(pc: pd.DataFrame, names: dict) -> str:
    fig, ax = plt.subplots(figsize=(9, 3.8))
    models = list(names)
    width = 0.8 / len(models)
    for k, m in enumerate(models):
        sub = pc[pc["modelo"] == m].set_index("clase").loc[config.CLASS_ORDER]
        xs = np.arange(3) + (k - (len(models) - 1) / 2) * width
        ax.bar(xs, sub["f1"], width=width * 0.9, color=MODEL_COLORS[m], label=names[m])
        for x, v in zip(xs, sub["f1"]):
            ax.text(x, v + 0.01, f"{v:.2f}", ha="center", fontsize=7.5, color=INK_2)
    ax.set_xticks(range(3), config.CLASS_ORDER)
    ax.set_ylabel("F1 en prueba")
    ax.set_ylim(0, 0.9)
    ax.set_title("F1 por clase: la clase Medio es la más difícil")
    ax.legend(ncol=4, fontsize=8, loc="upper left")
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return save(fig, "07_f1_por_clase.png")


def plot_permutation_importance(imp: pd.DataFrame, title: str, fname: str) -> str:
    imp = imp.sort_values("importancia_media")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(imp["variable"], imp["importancia_media"], xerr=imp["importancia_desv"],
            color=ACCENT, height=0.6, error_kw={"ecolor": INK_2, "lw": 1})
    ax.axvline(0, color="#c3c2b7", lw=1)
    ax.set_xlabel("Caída del F1 macro al permutar la variable")
    ax.set_title(title)
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    return save(fig, fname)


def plot_tree_figure(pipe) -> str:
    pre, model = pipe.named_steps["preprocesamiento"], pipe.named_steps["modelo"]
    names = [n.split("__", 1)[1] for n in pre.get_feature_names_out()]
    fig, ax = plt.subplots(figsize=(26, 11))
    plot_tree(model, feature_names=names, class_names=config.CLASS_ORDER, filled=False,
              impurity=False, proportion=True, rounded=True, fontsize=7, ax=ax)
    ax.set_title("Árbol de decisión final (proporciones de clase por nodo; ingreso en log1p)")
    return save(fig, "09_arbol_decision.png")


def shap_summary(pipe, X_test: pd.DataFrame) -> tuple[pd.DataFrame | None, str | None]:
    """|SHAP| medio por variable original (suma de sus columnas one-hot)."""
    try:
        import shap
    except ImportError:
        return None, None
    pre, model = pipe.named_steps["preprocesamiento"], pipe.named_steps["modelo"]
    Xt = pre.transform(X_test)
    names = pre.get_feature_names_out()
    try:
        explainer = shap.TreeExplainer(model) if hasattr(model, "tree_") or hasattr(model, "estimators_") \
            or model.__class__.__name__ == "XGBClassifier" else shap.LinearExplainer(model, Xt)
        values = np.asarray(explainer.shap_values(Xt))
    except Exception as exc:  # SHAP es opcional: se documenta si falla
        print(f"SHAP no disponible para este modelo: {exc}")
        return None, None
    if values.ndim == 3 and values.shape[0] == Xt.shape[0]:   # (n, features, clases)
        values = np.transpose(values, (2, 0, 1))
    mean_abs = np.abs(values).mean(axis=1)                     # (clases, features)
    orig = [next(f for f in config.FEATURES if n.split("__", 1)[1].startswith(f)) for n in names]
    df = pd.DataFrame(mean_abs.T, columns=config.CLASS_ORDER)
    df["variable"] = orig
    df = df.groupby("variable")[config.CLASS_ORDER].sum()
    df = df.loc[df.sum(axis=1).sort_values().index]
    fig, ax = plt.subplots(figsize=(8, 5))
    left = np.zeros(len(df))
    for cls in config.CLASS_ORDER:
        ax.barh(df.index, df[cls], left=left, color=CLASS_COLORS[cls], label=cls,
                edgecolor="#fcfcfb", linewidth=1.5, height=0.6)
        left += df[cls].values
    ax.set_xlabel("|SHAP| medio (contribución a la estimación de cada clase)")
    ax.set_title("SHAP: contribución media por variable y clase")
    ax.legend(title="Clase")
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    return df, save(fig, "10_shap_modelo_final.png")


def error_analysis(y_test, y_pred, meses_test: pd.Series) -> pd.DataFrame:
    """Errores según la distancia de meses_abierto a los cortes (solo análisis posterior)."""
    df = pd.DataFrame({"real": pd.Series(y_test).map(dict(enumerate(config.CLASS_ORDER))).values,
                       "predicho": pd.Series(y_pred).map(dict(enumerate(config.CLASS_ORDER))).values,
                       "meses": meses_test.values})
    df["error"] = df["real"] != df["predicho"]
    df["tramo_meses"] = pd.cut(df["meses"], [0, 6, 11, 24, 42, 60, 120, 600],
                               labels=["1-6", "7-11", "12-24", "25-42", "43-60", "61-120", ">120"])
    return df.groupby("tramo_meses", observed=True).agg(
        registros=("error", "size"), tasa_error=("error", "mean"),
        clase_real=("real", lambda s: s.mode().iat[0])).reset_index()


def main() -> dict:
    apply_style()
    if not CANDIDATES_PATH.exists() or not config.MODEL_PATH.exists():
        raise FileNotFoundError("Primero ejecute: python -m src.train")
    candidates = joblib.load(CANDIDATES_PATH)["modelos"]
    artifact = joblib.load(config.MODEL_PATH)
    final = artifact["nombre_modelo"]
    names = {s.name: s.nombre_es for s in get_model_specs()}

    df = prepare_dataset()
    X, y = get_X_y(df)
    X_train, X_test, y_train, y_test = split_data(X, y)
    meses_test = df.loc[X_test.index, "meses_abierto"]

    rows, per_class, cms, reports = [], [], {}, {}
    for key, pipe in candidates.items():
        y_pred = pipe.predict(X_test)
        y_proba = pipe.predict_proba(X_test)
        assert np.allclose(y_proba.sum(axis=1), 1), "Las probabilidades de clase no suman 1"
        rows.append({"modelo": key, "nombre": names[key], **compute_metrics(y_test, y_pred, y_proba)})
        per_class.append(per_class_table(key, y_test, y_pred))
        cms[key] = confusion_matrix(y_test, y_pred, labels=LABELS)
        reports[key] = classification_report(y_test, y_pred, labels=LABELS,
                                             target_names=config.CLASS_ORDER, digits=3, zero_division=0)
    for strategy in ("stratified", "most_frequent"):
        dummy = DummyClassifier(strategy=strategy, random_state=config.RANDOM_STATE).fit(X_train, y_train)
        key = "baseline_estratificado" if strategy == "stratified" else "baseline_clase_mayoritaria"
        rows.append({"modelo": key, "nombre": "Línea base: " + ("azar estratificado" if strategy == "stratified"
                                                                   else "siempre «Bajo»"),
                     **compute_metrics(y_test, dummy.predict(X_test), dummy.predict_proba(X_test))})

    table = pd.DataFrame(rows).set_index("modelo")
    pc = pd.concat(per_class)
    table.to_csv(config.TABLES_DIR / "metricas_prueba.csv")
    pc.to_csv(config.TABLES_DIR / "metricas_por_clase_prueba.csv", index=False)
    with open(config.TABLES_DIR / "classification_reports.txt", "w", encoding="utf-8") as fh:
        for key, rep in reports.items():
            fh.write(f"=== {names[key]} ===\n{rep}\nMatriz de confusión (filas=real, columnas=predicho; "
                     f"orden {config.CLASS_ORDER}):\n{cms[key]}\n\n")

    figs = [plot_confusion_matrices(cms, names, final), plot_model_comparison(table),
            plot_per_class_f1(pc, names)]

    # ---------------- Interpretabilidad del modelo final ----------------
    pipe = candidates[final]
    perm = permutation_importance(pipe, X_test, y_test, scoring="f1_macro", n_repeats=20,
                                  random_state=config.RANDOM_STATE, n_jobs=-1)
    imp = pd.DataFrame({"variable": X_test.columns, "importancia_media": perm.importances_mean,
                        "importancia_desv": perm.importances_std}).sort_values("importancia_media", ascending=False)
    imp.to_csv(config.TABLES_DIR / "importancia_permutacion_final.csv", index=False)
    figs.append(plot_permutation_importance(
        imp, f"Importancia por permutación · {names[final]} (prueba)", "08_importancia_permutacion.png"))

    model = pipe.named_steps["modelo"]
    pre = pipe.named_steps["preprocesamiento"]
    feat_names = [n.split("__", 1)[1] for n in pre.get_feature_names_out()]
    if hasattr(model, "feature_importances_"):
        pd.DataFrame({"columna_transformada": feat_names, "importancia": model.feature_importances_}) \
            .sort_values("importancia", ascending=False) \
            .to_csv(config.TABLES_DIR / "importancia_modelo_final.csv", index=False)
    if hasattr(model, "tree_"):
        figs.append(plot_tree_figure(pipe))
        with open(config.TABLES_DIR / "reglas_arbol.txt", "w", encoding="utf-8") as fh:
            fh.write("# Reglas del árbol final. le_deja_al_mes_COP está en escala log1p:\n"
                     "# pesos = exp(umbral) - 1 (p. ej. 13,31 -> $603.000 aprox.).\n\n")
            fh.write(export_text(model, feature_names=feat_names, class_names=config.CLASS_ORDER))
    shap_df, shap_fig = shap_summary(pipe, X_test)
    if shap_fig:
        figs.append(shap_fig)
        shap_df.to_csv(config.TABLES_DIR / "shap_modelo_final.csv")

    # Coeficientes de la regresión logística (comparación interpretativa).
    lr = candidates.get("logistic_regression")
    if lr is not None:
        lr_names = [n.split("__", 1)[1] for n in lr.named_steps["preprocesamiento"].get_feature_names_out()]
        coefs = pd.DataFrame(lr.named_steps["modelo"].coef_.T, index=lr_names, columns=config.CLASS_ORDER)
        coefs.to_csv(config.TABLES_DIR / "coeficientes_regresion_logistica.csv")

    errors = error_analysis(y_test, pipe.predict(X_test), meses_test)
    errors.to_csv(config.TABLES_DIR / "errores_por_tramo_meses.csv", index=False)

    summary = {"modelo_final": final, "metricas_prueba": table.round(4).reset_index().to_dict("records"),
               "figuras": figs}
    with open(config.TABLES_DIR / "resumen_evaluacion.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2, default=float)

    print(table.drop(columns="nombre").round(4).to_string())
    print("\n" + reports[final])
    print(errors.round(3).to_string(index=False))
    print(imp.round(4).to_string(index=False))
    print("Figuras:", *figs, sep="\n  ")
    return summary


if __name__ == "__main__":
    main()
