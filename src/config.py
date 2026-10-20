"""Configuración central del proyecto.

Todas las rutas son relativas a la raíz del repositorio, de modo que el
proyecto funciona en cualquier equipo sin rutas absolutas.
"""
from __future__ import annotations

from pathlib import Path

# --------------------------------------------------------------------------
# Rutas
# --------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT_DIR / "data" / "raw" / "BASE_1_EMICRON_2024_comida_DANE.xlsx"
DATA_PROCESSED_DIR = ROOT_DIR / "data" / "processed"
MODELS_DIR = ROOT_DIR / "models"
MODEL_PATH = MODELS_DIR / "modelo_final.joblib"
REPORTS_DIR = ROOT_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
TABLES_DIR = REPORTS_DIR / "tables"

# Huella SHA-256 del Excel original: permite comprobar que la base no cambió.
RAW_SHA256 = "0edbc84c9db645c8d843ca9ec855fdaa07cef64eea488419970a222d14e4054e"
DATA_SHEET = "Datos"

# --------------------------------------------------------------------------
# Reproducibilidad
# --------------------------------------------------------------------------
RANDOM_STATE = 42      # semilla única para división, CV y modelos
TEST_SIZE = 0.20       # 80 % entrenamiento / 20 % prueba
CV_FOLDS = 5           # validación cruzada estratificada de 5 pliegues
PRIMARY_METRIC = "f1_macro"

# --------------------------------------------------------------------------
# Variable objetivo: nivel_riesgo a partir de meses_abierto
# --------------------------------------------------------------------------
# Decisión metodológica del proyecto (NO es una clasificación oficial del DANE):
#   Alto  : 1  <= meses_abierto <= 11   (primer año de operación)
#   Medio : 12 <= meses_abierto <= 42   (negocio "nuevo" según el umbral GEM de 42 meses)
#   Bajo  : meses_abierto >= 43          (negocio "establecido", > 42 meses)
TARGET_SOURCE = "meses_abierto"
TARGET = "nivel_riesgo"
LIMITE_ALTO_MAX = 11    # último mes incluido en "Alto"
LIMITE_MEDIO_MAX = 42   # último mes incluido en "Medio"
CLASS_ORDER = ["Alto", "Medio", "Bajo"]   # orden fijo para codificar y graficar
CLASS_TO_CODE = {c: i for i, c in enumerate(CLASS_ORDER)}

# --------------------------------------------------------------------------
# Variables (resultado de la auditoría de fuga de información)
# --------------------------------------------------------------------------
ID_COLUMN = "id_negocio"

CATEGORICAL_FEATURES = [
    "donde_funciona",
    "como_lleva_cuentas",
    "visible_desde_la_calle",
    "zona",
]
BINARY_FEATURES = [  # respuestas "Sí" / "No"
    "tiene_ayudantes",
    "acepta_transferencias",
    "tiene_nombre_comercial",
    "registrado_camara_comercio",
    "tiene_RUT",
    "usa_internet",
    "tiene_redes_sociales",
]
NUMERIC_FEATURES = ["edad_propietario", "le_deja_al_mes_COP"]

FEATURES = CATEGORICAL_FEATURES + BINARY_FEATURES + NUMERIC_FEATURES

# Columnas que nunca pueden entrar a X, con la razón documentada.
EXCLUDED_COLUMNS = {
    "id_negocio": "Identificador de fila; no aporta información del negocio.",
    "meses_abierto": "Se usa exclusivamente para construir la etiqueta nivel_riesgo.",
    "nivel_riesgo": "Es la variable objetivo.",
    "riesgo_financiero": (
        "Es una transformación determinística de le_deja_al_mes_COP "
        "(Sí si < $650.000); es redundante y fue creada por el equipo para otro objetivo."
    ),
}

# Categorías con menos de este número de casos en entrenamiento se agrupan
# como "infrecuentes" dentro del OneHotEncoder (se ajusta solo con train).
MIN_CATEGORY_FREQUENCY = 20

# Rangos válidos para la validación de entradas en la aplicación.
EDAD_MIN, EDAD_MAX = 18, 100
INGRESO_MIN, INGRESO_MAX = 0, 100_000_000
