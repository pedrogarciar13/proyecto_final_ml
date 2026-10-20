"""Análisis exploratorio: tablas y figuras en ``reports/``.

Uso:  python -m src.eda
Se ejecuta sobre la base completa con fines descriptivos; ninguna estadística
de aquí se usa para ajustar el preprocesamiento del modelo.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src import config
from src.data_processing import (clean_data, data_quality_report, iqr_outliers,
                                 load_raw_data, prepare_dataset, target_distribution)
from src.viz import (ACCENT, CLASS_COLORS, INK_2, MUTED, apply_style, plt, save)


def plot_meses_distribution(df: pd.DataFrame) -> str:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    m = df["meses_abierto"]
    ax = axes[0]
    bins = np.arange(0, 505, 6)
    for cls in config.CLASS_ORDER:
        ax.hist(m[df[config.TARGET] == cls], bins=bins, color=CLASS_COLORS[cls],
                label=cls, edgecolor="#fcfcfb", linewidth=0.4)
    for lim in (config.LIMITE_ALTO_MAX + 0.5, config.LIMITE_MEDIO_MAX + 0.5):
        ax.axvline(lim, color=INK_2, lw=1, ls="--")
    ax.set_title("Antigüedad del negocio (meses_abierto)")
    ax.set_xlabel("Meses abierto")
    ax.set_ylabel("Negocios")
    ax.legend(title="nivel_riesgo")
    ax = axes[1]
    sub = m[m <= 72]
    ax.hist(sub, bins=np.arange(0.5, 73.5, 1), color=ACCENT, edgecolor="#fcfcfb", linewidth=0.3)
    for lim, lbl in ((11.5, "12"), (42.5, "43")):
        ax.axvline(lim, color=INK_2, lw=1, ls="--")
        ax.text(lim + 0.8, ax.get_ylim()[1] * 0.92, f"corte {lbl}", color=INK_2, fontsize=8)
    ax.set_title("Detalle 1–72 meses: acumulación en años completos")
    ax.set_xlabel("Meses abierto")
    fig.tight_layout()
    return save(fig, "01_distribucion_meses_abierto.png")


def plot_class_balance(df: pd.DataFrame) -> str:
    dist = target_distribution(df)
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    ax.barh(dist.index[::-1], dist["registros"][::-1],
            color=[CLASS_COLORS[c] for c in dist.index[::-1]], height=0.6)
    for i, cls in enumerate(dist.index[::-1]):
        r = dist.loc[cls]
        ax.text(r["registros"] + 40, i, f"{int(r['registros']):,} ({r['porcentaje']:.1f} %)".replace(",", "."),
                va="center", color=INK_2, fontsize=9)
    ax.set_xlim(0, dist["registros"].max() * 1.3)
    ax.set_title("Distribución de nivel_riesgo")
    ax.set_xlabel("Negocios")
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    return save(fig, "02_distribucion_nivel_riesgo.png")


def plot_categorical_vs_target(df: pd.DataFrame) -> str:
    cols = config.CATEGORICAL_FEATURES + config.BINARY_FEATURES
    fig, axes = plt.subplots(4, 3, figsize=(14, 13))
    for ax, col in zip(axes.flat, cols):
        tab = pd.crosstab(df[col], df[config.TARGET], normalize="index")[config.CLASS_ORDER] * 100
        n = df[col].value_counts()
        tab = tab.loc[n.index]
        left = np.zeros(len(tab))
        for cls in config.CLASS_ORDER:
            ax.barh(range(len(tab)), tab[cls], left=left, color=CLASS_COLORS[cls],
                    edgecolor="#fcfcfb", linewidth=1.5, label=cls, height=0.65)
            left += tab[cls].values
        ax.set_yticks(range(len(tab)))
        ax.set_yticklabels([f"{k} (n={n[k]})" for k in tab.index], fontsize=8)
        ax.invert_yaxis()
        ax.set_xlim(0, 100)
        ax.set_title(col, fontsize=10)
        ax.grid(axis="y", visible=False)
    for ax in axes.flat[len(cols):]:
        ax.axis("off")
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower right", bbox_to_anchor=(0.95, 0.08), title="nivel_riesgo", fontsize=10)
    fig.suptitle("Composición de nivel_riesgo (%) según cada variable categórica", x=0.01, ha="left",
                 fontweight="bold", fontsize=13)
    fig.tight_layout()
    return save(fig, "03_categoricas_vs_nivel_riesgo.png")


def plot_numeric_vs_target(df: pd.DataFrame) -> str:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for ax, col, transform, xlabel in (
        (axes[0], "edad_propietario", lambda s: s, "Edad del propietario (años)"),
        (axes[1], "le_deja_al_mes_COP", np.log10, "log10(1 + COP al mes)"),
    ):
        data = [transform(df.loc[df[config.TARGET] == c, col] + (1 if col != "edad_propietario" else 0))
                for c in config.CLASS_ORDER]
        bp = ax.boxplot(data, orientation="horizontal", patch_artist=True, widths=0.55,
                        medianprops={"color": "#0b0b0b"}, flierprops={"markersize": 2, "alpha": 0.3})
        for patch, c in zip(bp["boxes"], config.CLASS_ORDER):
            patch.set_facecolor(CLASS_COLORS[c])
            patch.set_alpha(0.85)
        ax.set_yticks([1, 2, 3])
        ax.set_yticklabels(config.CLASS_ORDER)
        ax.set_xlabel(xlabel)
        ax.set_title(col)
    fig.tight_layout()
    return save(fig, "04_numericas_vs_nivel_riesgo.png")


def numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = {}
    for col in ["meses_abierto", "edad_propietario", "le_deja_al_mes_COP"]:
        s = df[col]
        rows[col] = {**s.describe().to_dict(), **iqr_outliers(s), "asimetria": s.skew()}
    return pd.DataFrame(rows).T


def main() -> dict:
    apply_style()
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    raw = load_raw_data()
    clean = clean_data(raw)
    df = prepare_dataset()

    data_quality_report(raw).to_csv(config.TABLES_DIR / "calidad_datos.csv", index=False)
    numeric_summary(clean).to_csv(config.TABLES_DIR / "resumen_numericas.csv")
    target_distribution(df).to_csv(config.TABLES_DIR / "distribucion_nivel_riesgo.csv")
    pd.Series({
        "registros": len(raw), "columnas": raw.shape[1],
        "filas_duplicadas": int(raw.duplicated().sum()),
        "duplicados_sin_id": int(raw.drop(columns="id_negocio").duplicated().sum()),
        "nulos_totales": int(raw.isna().sum().sum()),
        "meses_abierto_igual_500": int((raw["meses_abierto"] == 500).sum()),
        "ingreso_cero": int((raw["le_deja_al_mes_COP"] == 0).sum()),
        "riesgo_financiero_igual_ingreso_lt_650k": bool(
            ((raw["le_deja_al_mes_COP"] < 650_000) == raw["riesgo_financiero"].str.startswith("Sí")).all()),
        "corr_pearson_meses_edad": round(raw["meses_abierto"].corr(raw["edad_propietario"]), 4),
        "corr_spearman_meses_ingreso": round(raw["meses_abierto"].corr(raw["le_deja_al_mes_COP"], method="spearman"), 4),
        "registros_sin_etiqueta": df.attrs.get("registros_sin_etiqueta", 0),
    }).to_csv(config.TABLES_DIR / "hallazgos_datos.csv", header=["valor"])

    figs = [plot_meses_distribution(df), plot_class_balance(df),
            plot_categorical_vs_target(df), plot_numeric_vs_target(df)]
    print("Figuras EDA:", *figs, sep="\n  ")
    return {"figuras": figs}


if __name__ == "__main__":
    main()
