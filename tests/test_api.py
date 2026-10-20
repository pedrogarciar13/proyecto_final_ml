import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["estado"] == "ok"


def test_index_page(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Termómetro de Riesgo" in r.text
    assert "meses_abierto" not in r.text


def test_metadata_lists_only_approved_fields(client):
    body = client.get("/api/metadata").json()
    names = [f["nombre"] for f in body["campos"]]
    assert len(names) == 13
    for forbidden in ("meses_abierto", "nivel_riesgo", "riesgo_financiero", "id_negocio"):
        assert forbidden not in names


def test_several_predictions_in_a_row(client, new_cases):
    for case in new_cases.values():
        r = client.post("/api/predict", json=case)
        assert r.status_code == 200
        body = r.json()
        assert body["nivel_riesgo"] in ("Alto", "Medio", "Bajo")
        assert body["alcance"]


def test_invalid_input_returns_readable_422(client, new_cases):
    case = {**new_cases["vendedor_ambulante_joven"], "edad_propietario": "abc", "zona": "Luna"}
    r = client.post("/api/predict", json=case)
    assert r.status_code == 422
    body = r.json()
    assert body["error"] == "Revise los datos ingresados."
    assert set(body["campos"]) == {"edad_propietario", "zona"}


def test_malformed_json_is_handled(client):
    r = client.post("/api/predict", content=b"{no es json", headers={"Content-Type": "application/json"})
    assert r.status_code == 422
    assert "Traceback" not in r.text


def test_non_object_json_is_handled(client):
    r = client.post("/api/predict", json=[1, 2, 3])
    assert r.status_code == 422
