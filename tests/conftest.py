import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# Casos NUEVOS, inventados para las pruebas (no son registros de la base).
# No se usaron para ajustar el modelo; solo verifican que la app funcione.
NEW_CASES = {
    "vendedor_ambulante_joven": {
        "donde_funciona": "Ambulante (calle)", "como_lleva_cuentas": "No lleva cuentas",
        "visible_desde_la_calle": "No aplica", "zona": "Cabecera (urbana)", "tiene_ayudantes": "No",
        "acepta_transferencias": "Sí", "tiene_nombre_comercial": "No", "registrado_camara_comercio": "No",
        "tiene_RUT": "No", "usa_internet": "Sí", "tiene_redes_sociales": "No",
        "edad_propietario": 23, "le_deja_al_mes_COP": 410000,
    },
    "restaurante_formal_local": {
        "donde_funciona": "Local o tienda", "como_lleva_cuentas": "Libro diario",
        "visible_desde_la_calle": "Sí", "zona": "Cabecera (urbana)", "tiene_ayudantes": "Sí",
        "acepta_transferencias": "Sí", "tiene_nombre_comercial": "Sí", "registrado_camara_comercio": "Sí",
        "tiene_RUT": "Sí", "usa_internet": "Sí", "tiene_redes_sociales": "Sí",
        "edad_propietario": 58, "le_deja_al_mes_COP": 3150000,
    },
    "cocina_rural_en_vivienda": {
        "donde_funciona": "En su vivienda", "como_lleva_cuentas": "Cuaderno, Excel o caja",
        "visible_desde_la_calle": "No", "zona": "Rural", "tiene_ayudantes": "No",
        "acepta_transferencias": "No", "tiene_nombre_comercial": "No", "registrado_camara_comercio": "No",
        "tiene_RUT": "No", "usa_internet": "No", "tiene_redes_sociales": "No",
        "edad_propietario": 44, "le_deja_al_mes_COP": 275000,
    },
}


@pytest.fixture(scope="session")
def new_cases():
    return NEW_CASES


@pytest.fixture(scope="session")
def artifact():
    from src.predict import load_artifact
    return load_artifact()
