import numpy as np
import pandas as pd
import pytest

from src import config
from src.data_processing import (DataValidationError, assert_no_leakage, assign_risk_level,
                                 build_target, check_target_integrity, clean_data, get_X_y,
                                 load_raw_data, prepare_dataset, split_data)


@pytest.fixture(scope="module")
def df():
    return prepare_dataset()


def test_raw_file_is_unchanged_and_complete():
    raw = load_raw_data(verify_hash=True)
    assert raw.shape == (7523, 16)
    assert raw["id_negocio"].is_unique


@pytest.mark.parametrize("meses, esperado", [
    (1, "Alto"), (11, "Alto"), (12, "Medio"), (36, "Medio"), (42, "Medio"),
    (43, "Bajo"), (48, "Bajo"), (500, "Bajo"),
])
def test_risk_level_boundaries(meses, esperado):
    assert assign_risk_level(pd.Series([meses])).iat[0] == esperado


@pytest.mark.parametrize("valor", [0, -5, None, "abc", np.nan])
def test_invalid_months_get_no_label(valor):
    assert pd.isna(assign_risk_level(pd.Series([valor], dtype=object)).iat[0])


def test_invalid_rows_are_dropped_and_counted():
    raw = load_raw_data().head(5).copy()
    raw.loc[raw.index[0], "meses_abierto"] = -1
    out = build_target(clean_data(raw))
    assert len(out) == 4
    assert out.attrs["registros_sin_etiqueta"] == 1


def test_target_distribution_matches_documentation(df):
    counts = df[config.TARGET].value_counts()
    assert counts.to_dict() == {"Bajo": 4099, "Medio": 2200, "Alto": 1224}
    check_target_integrity(df)  # sin solapamientos ni registros sin etiqueta


def test_predictors_exclude_label_sources(df):
    X, y = get_X_y(df)
    for col in ("meses_abierto", "nivel_riesgo", "riesgo_financiero", "id_negocio"):
        assert col not in X.columns
    assert list(X.columns) == config.FEATURES
    assert set(y.unique()) == {0, 1, 2}


def test_leakage_guard_raises():
    bad = pd.DataFrame(columns=config.FEATURES + ["meses_abierto"])
    with pytest.raises(DataValidationError):
        assert_no_leakage(bad)


def test_split_is_stratified_and_reproducible(df):
    X, y = get_X_y(df)
    a = split_data(X, y)
    b = split_data(X, y)
    assert len(a[0]) == 6018 and len(a[1]) == 1505
    assert a[1].index.equals(b[1].index)
    assert set(a[0].index).isdisjoint(a[1].index)
    train_p = a[2].value_counts(normalize=True).sort_index()
    test_p = a[3].value_counts(normalize=True).sort_index()
    assert np.allclose(train_p, test_p, atol=0.01)


def test_clean_data_handles_bad_values():
    raw = load_raw_data().head(3).copy()
    raw["edad_propietario"] = raw["edad_propietario"].astype(object)
    raw.loc[raw.index[0], "edad_propietario"] = "no sabe"
    raw.loc[raw.index[1], "le_deja_al_mes_COP"] = -100
    raw.loc[raw.index[2], "zona"] = "  Rural  "
    out = clean_data(raw)
    assert pd.isna(out["edad_propietario"].iat[0])
    assert pd.isna(out["le_deja_al_mes_COP"].iat[1])
    assert out["zona"].iat[2] == "Rural"
