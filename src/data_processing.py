"""Carga, validación, limpieza y construcción de la variable objetivo.

El archivo Excel original nunca se modifica: todas las transformaciones se
hacen en memoria y, si se desea, se guardan en ``data/processed``.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from src import config

EXPECTED_COLUMNS = [
    "id_negocio", "donde_funciona", "como_lleva_cuentas", "tiene_ayudantes",
    "meses_abierto", "acepta_transferencias", "tiene_nombre_comercial",
    "registrado_camara_comercio", "tiene_RUT", "visible_desde_la_calle",
    "usa_internet", "tiene_redes_sociales", "zona", "edad_propietario",
    "le_deja_al_mes_COP", "riesgo_financiero",
]


class DataValidationError(ValueError):
    """Error que indica que la base no cumple la estructura esperada."""


# --------------------------------------------------------------------------
# Carga
# --------------------------------------------------------------------------
def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_raw_data(path: Path = config.DATA_RAW, verify_hash: bool = True) -> pd.DataFrame:
    """Lee la hoja ``Datos`` del Excel original sin modificarlo."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró la base de datos en {path}")
    if verify_hash and file_sha256(path) != config.RAW_SHA256:
        raise DataValidationError(
            "La huella SHA-256 del Excel no coincide con la registrada: "
            "la base original pudo haber sido modificada."
        )
    return pd.read_excel(path, sheet_name=config.DATA_SHEET)


def load_sheet(sheet: str, path: Path = config.DATA_RAW) -> pd.DataFrame:
    """Lee una hoja auxiliar (LEEME, Resumen, Diccionario)."""
    return pd.read_excel(path, sheet_name=sheet)


# --------------------------------------------------------------------------
# Validación y limpieza
# --------------------------------------------------------------------------
def validate_schema(df: pd.DataFrame) -> None:
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise DataValidationError(f"Faltan columnas esperadas: {missing}")
    if df[config.ID_COLUMN].duplicated().any():
        raise DataValidationError("Hay identificadores de negocio duplicados.")


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Limpieza mínima y documentada.

    * Quita espacios sobrantes en textos.
    * Convierte las columnas numéricas a número (valores no numéricos -> NaN).
    * Marca como NaN valores imposibles (meses <= 0, edad fuera de rango,
      ingreso negativo). En la base actual no existe ninguno; la regla se
      deja para que el proceso sea robusto ante nuevas versiones.
    No se elimina ningún registro en esta etapa.
    """
    validate_schema(df)
    out = df.copy()
    text_cols = config.CATEGORICAL_FEATURES + config.BINARY_FEATURES + ["riesgo_financiero"]
    for col in text_cols:
        out[col] = out[col].astype("string").str.strip().astype(object)
        out.loc[out[col].isin(["", "nan", "<NA>"]), col] = np.nan

    for col in ["meses_abierto", "edad_propietario", "le_deja_al_mes_COP"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    out.loc[out["meses_abierto"] <= 0, "meses_abierto"] = np.nan
    edad_ok = out["edad_propietario"].between(config.EDAD_MIN, config.EDAD_MAX)
    out.loc[~edad_ok, "edad_propietario"] = np.nan
    out.loc[out["le_deja_al_mes_COP"] < 0, "le_deja_al_mes_COP"] = np.nan
    return out


# --------------------------------------------------------------------------
# Variable objetivo
# --------------------------------------------------------------------------
def assign_risk_level(meses: pd.Series) -> pd.Series:
    """Transforma meses_abierto en nivel_riesgo (Alto / Medio / Bajo).

    Alto : 1 a 11 meses   | Medio : 12 a 42 meses | Bajo : 43 meses o más.
    Los valores nulos o inválidos quedan como NaN (sin etiqueta).
    """
    meses = pd.to_numeric(meses, errors="coerce")
    valid = meses.notna() & (meses > 0)
    labels = pd.Series(np.nan, index=meses.index, dtype=object)
    labels[valid & (meses <= config.LIMITE_ALTO_MAX)] = "Alto"
    labels[valid & (meses > config.LIMITE_ALTO_MAX) & (meses <= config.LIMITE_MEDIO_MAX)] = "Medio"
    labels[valid & (meses > config.LIMITE_MEDIO_MAX)] = "Bajo"
    return labels


def build_target(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega ``nivel_riesgo`` y descarta solo los registros sin etiqueta válida."""
    out = df.copy()
    out[config.TARGET] = assign_risk_level(out[config.TARGET_SOURCE])
    n_invalid = out[config.TARGET].isna().sum()
    if n_invalid:
        # Sin meses_abierto válido no es posible definir la etiqueta.
        out = out[out[config.TARGET].notna()].copy()
    out.attrs["registros_sin_etiqueta"] = int(n_invalid)
    return out


def target_distribution(df: pd.DataFrame) -> pd.DataFrame:
    counts = df[config.TARGET].value_counts().reindex(config.CLASS_ORDER)
    meses = df.groupby(config.TARGET)[config.TARGET_SOURCE].agg(["min", "max", "median"])
    table = pd.DataFrame({
        "regla": [
            f"1 <= meses_abierto <= {config.LIMITE_ALTO_MAX}",
            f"{config.LIMITE_ALTO_MAX + 1} <= meses_abierto <= {config.LIMITE_MEDIO_MAX}",
            f"meses_abierto >= {config.LIMITE_MEDIO_MAX + 1}",
        ],
        "registros": counts.values,
        "porcentaje": (counts / counts.sum() * 100).round(2).values,
    }, index=config.CLASS_ORDER)
    return table.join(meses.reindex(config.CLASS_ORDER))


def check_target_integrity(df: pd.DataFrame) -> None:
    """Comprueba que las clases no se solapen y cubran todos los registros válidos."""
    ranges = df.groupby(config.TARGET)[config.TARGET_SOURCE].agg(["min", "max"]).reindex(config.CLASS_ORDER)
    if not (ranges.loc["Alto", "max"] < ranges.loc["Medio", "min"]
            and ranges.loc["Medio", "max"] < ranges.loc["Bajo", "min"]):
        raise DataValidationError(f"Las clases se solapan: {ranges.to_dict()}")
    if df[config.TARGET].isna().any() or not set(df[config.TARGET]) <= set(config.CLASS_ORDER):
        raise DataValidationError("Hay registros sin etiqueta o con etiquetas inesperadas.")


# --------------------------------------------------------------------------
# Calidad de datos y auditoría
# --------------------------------------------------------------------------
def data_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        s = df[col]
        rows.append({
            "columna": col,
            "tipo": str(s.dtype),
            "nulos": int(s.isna().sum()),
            "valores_unicos": int(s.nunique()),
            "ejemplo": s.dropna().iloc[0] if s.notna().any() else None,
        })
    return pd.DataFrame(rows)


def iqr_outliers(series: pd.Series) -> dict:
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return {
        "q1": q1, "q3": q3, "limite_inferior": low, "limite_superior": high,
        "atipicos": int(((series < low) | (series > high)).sum()),
    }


def leakage_audit_table() -> pd.DataFrame:
    """Tabla de decisiones por variable (etiqueta vs. predictoras)."""
    desc = {
        "id_negocio": ("entero", "Número de fila (no es dato del DANE)"),
        "meses_abierto": ("entero", "Edad del negocio en meses (P3034)"),
        "nivel_riesgo": ("categórica", "Alto / Medio / Bajo construida desde meses_abierto"),
        "donde_funciona": ("categórica", "Dónde funciona principalmente el negocio (P3053)"),
        "como_lleva_cuentas": ("categórica", "Principal forma de llevar las cuentas (P640)"),
        "tiene_ayudantes": ("binaria", "Si alguien le ayuda en el negocio (P3031)"),
        "acepta_transferencias": ("binaria", "Acepta transferencias o pagos por internet (P1764_3)"),
        "tiene_nombre_comercial": ("binaria", "Tiene nombre comercial (P3035)"),
        "registrado_camara_comercio": ("binaria", "Registro en Cámara de Comercio (P1055)"),
        "tiene_RUT": ("binaria", "Tiene RUT ante la DIAN (P1633)"),
        "visible_desde_la_calle": ("categórica", "Visible desde la calle: Sí / No / No aplica (P469)"),
        "usa_internet": ("binaria", "El negocio usa internet (P2524)"),
        "tiene_redes_sociales": ("binaria", "Tiene redes sociales (P1559)"),
        "zona": ("categórica", "Cabecera (urbana) o Rural (CLASE_TE)"),
        "edad_propietario": ("entero", "Edad del dueño en años (P241)"),
        "le_deja_al_mes_COP": ("entero", "Lo que el negocio le deja al dueño al mes, en COP (P3072)"),
        "riesgo_financiero": ("categórica", "Sí si le_deja_al_mes_COP < 650.000; calculada por el equipo"),
    }
    just_pred = {
        "edad_propietario": (
            "Conocida al momento de predecir y no derivada de meses_abierto. Tiene "
            "correlación moderada con la antigüedad (r = 0,42): es señal legítima, "
            "no una reconstrucción de la etiqueta. Uso descriptivo; ver nota ética."
        ),
        "le_deja_al_mes_COP": (
            "Reportada por el dueño en la encuesta, disponible al predecir y no "
            "derivada de meses_abierto (Spearman 0,18). La advertencia de fuga del "
            "diccionario aplicaba al objetivo anterior (riesgo_financiero), no a nivel_riesgo."
        ),
    }
    rows = []
    for col, (tipo, d) in desc.items():
        if col == "meses_abierto":
            uso, incl, just = "Construcción de la etiqueta", "Excluida de X", config.EXCLUDED_COLUMNS[col]
        elif col == "nivel_riesgo":
            uso, incl, just = "Variable objetivo (y)", "Excluida de X", config.EXCLUDED_COLUMNS[col]
        elif col in config.EXCLUDED_COLUMNS:
            uso, incl, just = "Ninguno", "Excluida de X", config.EXCLUDED_COLUMNS[col]
        else:
            uso, incl = "Predictora (X)", "Incluida"
            just = just_pred.get(col, "Característica observable del negocio, conocida al predecir; no deriva de la etiqueta.")
        rows.append({"variable": col, "tipo": tipo, "descripcion": d,
                     "uso_previsto": uso, "decision": incl, "justificacion": just})
    return pd.DataFrame(rows)


def assert_no_leakage(X: pd.DataFrame) -> None:
    """Falla si alguna columna prohibida aparece en la matriz de predictoras."""
    forbidden = set(config.EXCLUDED_COLUMNS)
    present = forbidden.intersection(X.columns)
    if present:
        raise DataValidationError(f"Fuga de información: columnas prohibidas en X: {sorted(present)}")
    if list(X.columns) != config.FEATURES:
        raise DataValidationError("Las columnas de X no coinciden con las variables aprobadas.")


# --------------------------------------------------------------------------
# Preparación final
# --------------------------------------------------------------------------
def prepare_dataset(path: Path = config.DATA_RAW) -> pd.DataFrame:
    """Carga + limpieza + objetivo. Devuelve el DataFrame modelable."""
    df = build_target(clean_data(load_raw_data(path)))
    check_target_integrity(df)
    return df


def get_X_y(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    X = df[config.FEATURES].copy()
    assert_no_leakage(X)
    y = df[config.TARGET].map(config.CLASS_TO_CODE).astype(int)
    return X, y


def split_data(X: pd.DataFrame, y: pd.Series):
    """División 80/20 estratificada por nivel_riesgo con semilla fija."""
    return train_test_split(
        X, y, test_size=config.TEST_SIZE, stratify=y, random_state=config.RANDOM_STATE
    )


def save_processed(df: pd.DataFrame) -> Path:
    config.DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = config.DATA_PROCESSED_DIR / "emicron_comida_con_nivel_riesgo.csv"
    df.to_csv(out, index=False, encoding="utf-8")
    return out
