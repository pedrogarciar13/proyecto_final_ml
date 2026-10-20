"""API y aplicación web (FastAPI).

Ejecutar localmente desde la raíz del repositorio:
    uvicorn app.main:app --reload
y abrir http://127.0.0.1:8000
"""
from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # permite ejecutar sin instalar el paquete
    sys.path.insert(0, str(ROOT))

from src.predict import (InputValidationError, SCOPE_NOTE, form_schema,  # noqa: E402
                         load_artifact, predict)

logger = logging.getLogger("riesgo_negocios")
APP_DIR = Path(__file__).resolve().parent

def _artifact():
    return load_artifact()


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Si el modelo no carga, la app lo informa en /api/health en lugar de caerse.
    try:
        _artifact()
    except Exception:  # pragma: no cover - solo registro
        logger.exception("No se pudo cargar el modelo al iniciar")
    yield


app = FastAPI(
    title="Clasificador de nivel de riesgo · Negocios de comida (EMICRON 2024)",
    description="Clasifica un negocio de comida en Alto / Medio / Bajo según una etiqueta definida "
                "a partir de la antigüedad del negocio. No predice cierres reales.",
    version="1.0.0",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")


# --------------------------------------------------------------------------
# Manejo de errores: mensajes claros y sin detalles técnicos internos
# --------------------------------------------------------------------------
@app.exception_handler(InputValidationError)
async def _input_error(_: Request, exc: InputValidationError):
    return JSONResponse(status_code=422, content={
        "error": "Revise los datos ingresados.", "campos": exc.errors})


@app.exception_handler(RequestValidationError)
async def _request_error(_: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={
        "error": "La solicitud no tiene el formato esperado (se requiere un objeto JSON).", "campos": {}})


@app.exception_handler(Exception)
async def _unexpected_error(_: Request, exc: Exception):
    logger.exception("Error inesperado", exc_info=exc)
    return JSONResponse(status_code=500, content={
        "error": "Ocurrió un error interno. Intente de nuevo en unos segundos."})


# --------------------------------------------------------------------------
# Rutas
# --------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


@app.get("/api/health")
def health():
    try:
        artifact = _artifact()
        return {"estado": "ok", "modelo": artifact["nombre_modelo_es"]}
    except Exception:
        return JSONResponse(status_code=503, content={"estado": "error",
                                                      "detalle": "El modelo no está disponible."})


@app.get("/api/metadata")
def metadata():
    """Campos del formulario y datos del modelo (generados desde el modelo guardado)."""
    artifact = _artifact()
    cv = artifact.get("resumen_cv", {})
    return {
        "campos": form_schema(artifact),
        "clases": artifact["clases"],
        "regla_objetivo": artifact["regla_objetivo"],
        "modelo": {
            "nombre": artifact["nombre_modelo_es"],
            "cv_f1_macro": cv.get("cv_f1_macro_media"),
            "cv_balanced_accuracy": cv.get("cv_balanced_accuracy_media"),
            "entrenado_en": artifact.get("entrenado_en"),
        },
        "alcance": SCOPE_NOTE,
    }


@app.post("/api/predict")
async def predict_endpoint(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raise InputValidationError({"_": "El cuerpo de la solicitud no es un JSON válido."})
    return predict(payload, _artifact())
