import numpy as np
import pandas as pd
import pytest

from src import config
from src.data_processing import load_raw_data
from src.predict import InputValidationError, form_schema, predict, validate_input


def test_model_loads_with_full_pipeline(artifact):
    pipe = artifact["pipeline"]
    assert "preprocesamiento" in pipe.named_steps and "modelo" in pipe.named_steps
    assert artifact["variables"] == config.FEATURES
    assert artifact["clases"] == ["Alto", "Medio", "Bajo"]


def test_new_cases_are_not_in_training_data(new_cases):
    raw = load_raw_data()[config.FEATURES]
    for case in new_cases.values():
        match = np.ones(len(raw), dtype=bool)
        for col, val in case.items():
            match &= (raw[col] == val).to_numpy()
        assert not match.any()


@pytest.mark.parametrize("name", ["vendedor_ambulante_joven", "restaurante_formal_local", "cocina_rural_en_vivienda"])
def test_new_cases_get_valid_prediction(artifact, new_cases, name):
    out = predict(new_cases[name], artifact)
    assert out["nivel_riesgo"] in ("Alto", "Medio", "Bajo")
    scores = out["puntajes_por_clase"]
    assert set(scores) == {"Alto", "Medio", "Bajo"}
    assert abs(sum(scores.values()) - 1) < 1e-3
    assert max(scores, key=scores.get) == out["nivel_riesgo"]
    assert "probabilidad de cierre" in out["alcance"]  # la nota de alcance siempre se entrega


def test_prediction_matches_pipeline_directly(artifact, new_cases):
    """La función de predicción aplica el mismo preprocesamiento del entrenamiento."""
    case = new_cases["restaurante_formal_local"]
    direct = artifact["pipeline"].predict(pd.DataFrame([case])[config.FEATURES])[0]
    assert predict(case, artifact)["nivel_riesgo"] == config.CLASS_ORDER[int(direct)]


def test_form_categories_match_model(artifact):
    pre = artifact["pipeline"].named_steps["preprocesamiento"]
    encoder = pre.named_transformers_["cat"].named_steps["onehot"]
    cat_cols = next(cols for name, _, cols in pre.transformers_ if name == "cat")
    learned = {col: set(cats) for col, cats in zip(cat_cols, encoder.categories_)}
    for field in form_schema(artifact):
        if field["tipo"] in ("binaria", "categorica"):
            assert set(field["opciones"]) <= learned[field["nombre"]]
    names = [f["nombre"] for f in form_schema(artifact)]
    assert names == config.FEATURES and "meses_abierto" not in names


def test_missing_fields_are_reported(artifact, new_cases):
    case = dict(new_cases["cocina_rural_en_vivienda"])
    del case["zona"]
    case["tiene_RUT"] = ""
    with pytest.raises(InputValidationError) as exc:
        validate_input(case, artifact)
    assert set(exc.value.errors) == {"zona", "tiene_RUT"}


@pytest.mark.parametrize("field, value", [
    ("edad_propietario", "treinta"), ("edad_propietario", 5), ("edad_propietario", 150),
    ("edad_propietario", 30.5), ("le_deja_al_mes_COP", -1), ("le_deja_al_mes_COP", "inf"),
    ("le_deja_al_mes_COP", True),
])
def test_invalid_numbers_rejected(artifact, new_cases, field, value):
    case = {**new_cases["cocina_rural_en_vivienda"], field: value}
    with pytest.raises(InputValidationError) as exc:
        validate_input(case, artifact)
    assert field in exc.value.errors


def test_unknown_category_rejected(artifact, new_cases):
    case = {**new_cases["cocina_rural_en_vivienda"], "donde_funciona": "Nave espacial"}
    with pytest.raises(InputValidationError) as exc:
        validate_input(case, artifact)
    assert "donde_funciona" in exc.value.errors


def test_label_fields_are_refused(artifact, new_cases):
    case = {**new_cases["cocina_rural_en_vivienda"], "meses_abierto": 3}
    with pytest.raises(InputValidationError):
        validate_input(case, artifact)


def test_pipeline_handles_unseen_category_safely(artifact, new_cases):
    """Aunque la API rechaza categorías desconocidas, el pipeline no falla con ellas."""
    row = pd.DataFrame([{**new_cases["cocina_rural_en_vivienda"], "donde_funciona": "Desconocido"}])
    assert artifact["pipeline"].predict(row[config.FEATURES])[0] in (0, 1, 2)
