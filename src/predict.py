"""Inferencia: carga del modelo guardado, validación de entradas y predicción.

La predicción siempre la hace el pipeline guardado (preprocesamiento + modelo),
por lo que se aplica exactamente la misma transformación que en el entrenamiento.
"""
from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from src import config

# Preguntas tal como se muestran en el formulario (basadas en el diccionario).
FIELD_INFO: dict[str, dict[str, str]] = {
    "donde_funciona": {"pregunta": "¿Dónde funciona principalmente el negocio?", "grupo": "Operación"},
    "visible_desde_la_calle": {"pregunta": "¿El negocio se ve desde la calle?", "grupo": "Operación",
                               "ayuda": "«No aplica» corresponde, por ejemplo, a negocios ambulantes o a domicilio."},
    "zona": {"pregunta": "¿En qué zona está el negocio?", "grupo": "Operación"},
    "tiene_ayudantes": {"pregunta": "¿Alguien le ayuda en el negocio?", "grupo": "Operación"},
    "como_lleva_cuentas": {"pregunta": "¿Cómo lleva las cuentas?", "grupo": "Formalidad"},
    "tiene_nombre_comercial": {"pregunta": "¿Tiene nombre comercial?", "grupo": "Formalidad"},
    "registrado_camara_comercio": {"pregunta": "¿Está registrado en la Cámara de Comercio?", "grupo": "Formalidad"},
    "tiene_RUT": {"pregunta": "¿Tiene RUT ante la DIAN?", "grupo": "Formalidad"},
    "acepta_transferencias": {"pregunta": "¿Acepta transferencias o pagos por internet?", "grupo": "Digital",
                              "ayuda": "Por ejemplo Nequi, Daviplata o transferencia bancaria."},
    "usa_internet": {"pregunta": "¿El negocio usa internet?", "grupo": "Digital"},
    "tiene_redes_sociales": {"pregunta": "¿Tiene redes sociales?", "grupo": "Digital"},
    "edad_propietario": {"pregunta": "Edad del propietario (años)", "grupo": "Propietario y finanzas"},
    "le_deja_al_mes_COP": {"pregunta": "¿Cuánto le deja el negocio al mes? (pesos colombianos)",
                           "grupo": "Propietario y finanzas",
                           "ayuda": "Ganancia mensual que el dueño reporta (pregunta P3072 de EMICRON)."},
}

CLASS_TEXT = {
    "Alto": ("Las características ingresadas se parecen más a las de los negocios que llevaban "
             "menos de 12 meses abiertos en la encuesta (su primer año de operación)."),
    "Medio": ("Las características ingresadas se parecen más a las de los negocios que llevaban "
              "entre 12 y 42 meses abiertos: ya superaron el primer año, pero aún son negocios nuevos."),
    "Bajo": ("Las características ingresadas se parecen más a las de los negocios con más de 42 meses "
             "abiertos, es decir, negocios ya establecidos."),
}

SCOPE_NOTE = (
    "Esta clasificación compara el negocio con los 7.523 negocios de comida de la encuesta EMICRON 2024 "
    "del DANE. La etiqueta de riesgo se definió a partir de la antigüedad del negocio (menor antigüedad = "
    "mayor riesgo). No es una probabilidad de cierre ni un pronóstico de lo que pasará con el negocio."
)


class InputValidationError(ValueError):
    """Errores de validación con mensajes comprensibles para el usuario."""

    def __init__(self, errors: dict[str, str]):
        super().__init__("; ".join(f"{k}: {v}" for k, v in errors.items()))
        self.errors = errors


@lru_cache(maxsize=1)
def load_artifact(path: str | Path = config.MODEL_PATH) -> dict:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el modelo entrenado en {path}. Ejecute: python -m src.train")
    artifact = joblib.load(path)
    for key in ("pipeline", "variables", "clases", "opciones_formulario"):
        if key not in artifact:
            raise ValueError(f"El archivo del modelo está incompleto (falta '{key}').")
    if artifact["variables"] != config.FEATURES:
        raise ValueError("Las variables del modelo guardado no coinciden con la configuración actual.")
    return artifact


def allowed_categories(artifact: dict) -> dict[str, list[str]]:
    return {col: [o["valor"] for o in opts]
            for col, opts in artifact["opciones_formulario"]["categoricas"].items()}


def form_schema(artifact: dict) -> list[dict]:
    """Descripción de los campos del formulario (se sirve a la interfaz web)."""
    cats = allowed_categories(artifact)
    nums = artifact["opciones_formulario"]["numericas"]
    fields = []
    for col in config.FEATURES:
        info = FIELD_INFO[col]
        field = {"nombre": col, "pregunta": info["pregunta"], "grupo": info["grupo"], "ayuda": info.get("ayuda", "")}
        if col in config.BINARY_FEATURES:
            field.update(tipo="binaria", opciones=["Sí", "No"])
        elif col in cats:
            field.update(tipo="categorica", opciones=cats[col])
        else:
            lo, hi = ((config.EDAD_MIN, config.EDAD_MAX) if col == "edad_propietario"
                      else (config.INGRESO_MIN, config.INGRESO_MAX))
            field.update(tipo="numerica", minimo=lo, maximo=hi, mediana_entrenamiento=nums[col]["mediana"],
                         paso=1 if col == "edad_propietario" else 1000)
        fields.append(field)
    return fields


def validate_input(data: Any, artifact: dict) -> dict:
    """Comprueba campos obligatorios, categorías permitidas y rangos numéricos."""
    if not isinstance(data, dict):
        raise InputValidationError({"_": "Los datos deben enviarse como un objeto JSON."})
    errors: dict[str, str] = {}
    cats = allowed_categories(artifact)
    clean: dict[str, Any] = {}
    forbidden = {"meses_abierto", "nivel_riesgo", "riesgo_financiero"}.intersection(data)
    if forbidden:
        errors["_"] = f"Estos campos no se usan para predecir: {', '.join(sorted(forbidden))}."
    for col in config.FEATURES:
        value = data.get(col)
        label = FIELD_INFO[col]["pregunta"]
        if value is None or (isinstance(value, str) and not value.strip()):
            errors[col] = f"Responda: {label}"
            continue
        if col in config.NUMERIC_FEATURES:
            try:
                if isinstance(value, bool):
                    raise ValueError
                number = float(str(value).replace(" ", ""))
                if not math.isfinite(number):
                    raise ValueError
            except (TypeError, ValueError):
                errors[col] = "Debe ser un número válido."
                continue
            lo, hi = ((config.EDAD_MIN, config.EDAD_MAX) if col == "edad_propietario"
                      else (config.INGRESO_MIN, config.INGRESO_MAX))
            if not lo <= number <= hi:
                errors[col] = f"Debe estar entre {lo:,} y {hi:,}.".replace(",", ".")
                continue
            if col == "edad_propietario" and number != int(number):
                errors[col] = "La edad debe ser un número entero de años."
                continue
            clean[col] = number
        else:
            text = str(value).strip()
            if text not in cats[col]:
                errors[col] = "Opción no reconocida. Elija una de las opciones de la lista."
                continue
            clean[col] = text
    if errors:
        raise InputValidationError(errors)
    return clean


def _readable_condition(feature: str, threshold: float, goes_left: bool) -> str | None:
    """Traduce una división del árbol a lenguaje natural."""
    for col in config.NUMERIC_FEATURES:
        if feature == col:
            if col == "le_deja_al_mes_COP":
                value = f"${np.expm1(threshold):,.0f}".replace(",", ".")
                return f"Le deja al mes {'hasta' if goes_left else 'más de'} {value}"
            return f"Edad del propietario {'de hasta' if goes_left else 'mayor a'} {threshold:.0f} años"
    for col in config.CATEGORICAL_FEATURES + config.BINARY_FEATURES:
        if feature.startswith(col + "_"):
            category = feature[len(col) + 1:]
            question = FIELD_INFO[col]["pregunta"].rstrip("?").lstrip("¿")
            if category == "infrequent_sklearn":
                category = "una opción poco frecuente"
            if col in config.BINARY_FEATURES:
                answer = category if not goes_left else ("No" if category == "Sí" else "Sí")
                return f"{question}: {answer}"
            return f"{question}: {'no es' if goes_left else 'es'} «{category}»"
    return None


def decision_path_explanation(pipeline, X: pd.DataFrame) -> list[str]:
    """Reglas que siguió el árbol para esta predicción (vacío si no es un árbol)."""
    model = pipeline.named_steps["modelo"]
    if not hasattr(model, "tree_"):
        return []
    pre = pipeline.named_steps["preprocesamiento"]
    Xt = pre.transform(X)
    names = [n.split("__", 1)[1] for n in pre.get_feature_names_out()]
    tree = model.tree_
    node_ids = model.decision_path(Xt).indices
    steps = []
    for node in node_ids:
        if tree.children_left[node] == tree.children_right[node]:
            continue  # hoja
        feat = names[tree.feature[node]]
        goes_left = Xt[0, tree.feature[node]] <= tree.threshold[node]
        text = _readable_condition(feat, tree.threshold[node], goes_left)
        if text:
            steps.append(text)
    return steps


def predict(data: dict, artifact: dict | None = None) -> dict:
    """Valida los datos de un negocio y devuelve la clasificación del modelo."""
    artifact = artifact or load_artifact()
    clean = validate_input(data, artifact)
    X = pd.DataFrame([clean], columns=artifact["variables"])
    pipeline = artifact["pipeline"]
    code = int(pipeline.predict(X)[0])
    classes = artifact["clases"]
    label = classes[code]
    scores = {}
    if hasattr(pipeline, "predict_proba"):
        proba = pipeline.predict_proba(X)[0]
        model_classes = list(pipeline.named_steps["modelo"].classes_)
        scores = {classes[int(c)]: round(float(p), 4) for c, p in zip(model_classes, proba)}
    return {
        "nivel_riesgo": label,
        "explicacion": CLASS_TEXT[label],
        "puntajes_por_clase": scores,
        "nota_puntajes": (
            ("Proporción de negocios de entrenamiento de cada clase en el grupo del árbol al que llegó "
             "este negocio (ponderada para compensar el desbalance de clases). ")
            if hasattr(pipeline.named_steps["modelo"], "tree_") else
            "Estimación del modelo de pertenencia a cada clase. "
        ) + "Indica qué tan clara es la clasificación; no es una probabilidad de cierre.",
        "reglas_aplicadas": decision_path_explanation(pipeline, X),
        "alcance": SCOPE_NOTE,
        "modelo": artifact.get("nombre_modelo_es", artifact.get("nombre_modelo")),
        "entrada": clean,
    }
