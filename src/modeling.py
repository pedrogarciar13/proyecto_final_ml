"""Definición de pipelines y espacios de hiperparámetros de los cuatro modelos.

Cada modelo es un ``Pipeline`` (preprocesamiento + clasificador). Así, la
imputación, la codificación y el escalado se ajustan solo con los datos de
entrenamiento de cada pliegue y se aplican igual en la predicción.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.stats import loguniform, randint, uniform
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

from src import config


def _log1p(x):
    """log(1 + x): reduce la asimetría extrema del ingreso mensual."""
    return np.log1p(np.clip(x, 0, None))


def build_preprocessor(scale_numeric: bool, features: list[str] | None = None) -> ColumnTransformer:
    """Preprocesamiento común.

    * Categóricas y binarias: imputación por la moda + One-Hot. Las categorías
      con menos de ``MIN_CATEGORY_FREQUENCY`` casos en entrenamiento se agrupan
      como "infrecuentes" y las categorías nunca vistas se envían a ese grupo.
    * edad_propietario: imputación por la mediana.
    * le_deja_al_mes_COP: imputación por la mediana + log1p (no se eliminan
      valores atípicos; la transformación reduce su influencia).
    * Escalado estándar solo si el algoritmo lo necesita (regresión logística).
    """
    features = features or config.FEATURES
    cat_cols = [c for c in config.CATEGORICAL_FEATURES + config.BINARY_FEATURES if c in features]
    transformers = []
    if cat_cols:
        transformers.append(("cat", Pipeline([
            ("imputar", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="infrequent_if_exist",
                                     min_frequency=config.MIN_CATEGORY_FREQUENCY,
                                     sparse_output=False)),
        ]), cat_cols))
    if "edad_propietario" in features:
        steps = [("imputar", SimpleImputer(strategy="median"))]
        if scale_numeric:
            steps.append(("escalar", StandardScaler()))
        transformers.append(("edad", Pipeline(steps), ["edad_propietario"]))
    if "le_deja_al_mes_COP" in features:
        steps = [("imputar", SimpleImputer(strategy="median")),
                 ("log1p", FunctionTransformer(_log1p, feature_names_out="one-to-one"))]
        if scale_numeric:
            steps.append(("escalar", StandardScaler()))
        transformers.append(("ingreso", Pipeline(steps), ["le_deja_al_mes_COP"]))
    return ColumnTransformer(transformers, remainder="drop", verbose_feature_names_out=True)


@dataclass
class ModelSpec:
    name: str
    nombre_es: str
    estimator: object
    scale_numeric: bool
    param_space: dict
    search: str = "grid"          # "grid" o "random"
    n_iter: int = 40
    uses_sample_weight: bool = False
    complexity_rank: int = 0      # menor = más simple / interpretable
    description: str = ""
    extra: dict = field(default_factory=dict)

    def pipeline(self, features: list[str] | None = None) -> Pipeline:
        from sklearn.base import clone
        return Pipeline([
            ("preprocesamiento", build_preprocessor(self.scale_numeric, features)),
            ("modelo", clone(self.estimator)),
        ])


def get_model_specs() -> list[ModelSpec]:
    rs = config.RANDOM_STATE
    return [
        ModelSpec(
            name="logistic_regression",
            nombre_es="Regresión logística",
            estimator=LogisticRegression(max_iter=5000, class_weight="balanced", random_state=rs),
            scale_numeric=True,
            param_space={"modelo__C": [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0]},
            search="grid",
            complexity_rank=0,
            description=(
                "Modelo lineal multinomial: combina las variables con pesos y convierte "
                "el puntaje de cada clase en una estimación de pertenencia con softmax. "
                "C controla la regularización L2 (C pequeño = modelo más simple)."
            ),
        ),
        ModelSpec(
            name="decision_tree",
            nombre_es="Árbol de decisión",
            estimator=DecisionTreeClassifier(class_weight="balanced", random_state=rs),
            scale_numeric=False,
            param_space={
                "modelo__max_depth": [2, 3, 4, 5, 6, 8, 10],
                "modelo__min_samples_leaf": [5, 10, 20, 50, 100],
                "modelo__criterion": ["gini", "entropy"],
            },
            search="grid",
            complexity_rank=1,
            description=(
                "Divide los datos con preguntas sucesivas (p. ej. «¿edad <= 45?») hasta "
                "llegar a hojas con una clase dominante. La profundidad y el tamaño "
                "mínimo de hoja limitan el sobreajuste."
            ),
        ),
        ModelSpec(
            name="random_forest",
            nombre_es="Random Forest",
            estimator=RandomForestClassifier(class_weight="balanced", random_state=rs, n_jobs=-1),
            scale_numeric=False,
            param_space={
                "modelo__n_estimators": [200, 400, 600],
                "modelo__max_depth": [4, 6, 8, 10, 14, None],
                "modelo__min_samples_leaf": [1, 3, 5, 10, 20, 40],
                "modelo__max_features": ["sqrt", 0.3, 0.5],
            },
            search="random",
            n_iter=40,
            complexity_rank=2,
            description=(
                "Promedia cientos de árboles entrenados con muestras bootstrap y "
                "subconjuntos aleatorios de variables; reduce la varianza de un árbol único."
            ),
        ),
        ModelSpec(
            name="xgboost",
            nombre_es="XGBoost",
            estimator=XGBClassifier(objective="multi:softprob", eval_metric="mlogloss",
                                    tree_method="hist", random_state=rs, n_jobs=4),
            scale_numeric=False,
            param_space={
                "modelo__n_estimators": randint(100, 700),
                "modelo__learning_rate": loguniform(0.01, 0.2),
                "modelo__max_depth": randint(2, 7),
                "modelo__min_child_weight": randint(1, 20),
                "modelo__subsample": uniform(0.6, 0.4),
                "modelo__colsample_bytree": uniform(0.5, 0.5),
                "modelo__reg_lambda": loguniform(0.5, 20),
            },
            search="random",
            n_iter=40,
            uses_sample_weight=True,
            complexity_rank=3,
            description=(
                "Gradient boosting: agrega árboles pequeños en secuencia, cada uno "
                "corrigiendo los errores de los anteriores, con regularización. El "
                "desbalance se trata con pesos de muestra balanceados."
            ),
        ),
    ]
