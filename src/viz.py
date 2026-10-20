"""Estilo gráfico común para todas las figuras del proyecto."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from src import config  # noqa: E402

# Colores por rol (paleta validada; el riesgo usa la paleta de estado y
# siempre va acompañado de su etiqueta de texto).
CLASS_COLORS = {"Alto": "#d03b3b", "Medio": "#fab219", "Bajo": "#0ca30c"}
MODEL_COLORS = {
    "logistic_regression": "#2a78d6",
    "decision_tree": "#eb6834",
    "random_forest": "#1baf7a",
    "xgboost": "#eda100",
}
SEQ_CMAP = matplotlib.colors.LinearSegmentedColormap.from_list(
    "azul", ["#fcfcfb", "#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
INK, INK_2, MUTED, GRID, BASE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
ACCENT = "#2a78d6"


def apply_style() -> None:
    plt.rcParams.update({
        "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
        "savefig.facecolor": "#fcfcfb", "figure.dpi": 110, "savefig.dpi": 160,
        "font.family": "DejaVu Sans", "font.size": 10,
        "axes.edgecolor": BASE, "axes.labelcolor": INK_2, "axes.titlecolor": INK,
        "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
        "xtick.color": MUTED, "ytick.color": MUTED, "legend.frameon": False,
    })


def save(fig, name: str) -> str:
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = config.FIGURES_DIR / name
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return str(path.relative_to(config.ROOT_DIR))
