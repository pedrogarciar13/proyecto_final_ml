# Termómetro de Riesgo · Negocios de comida en Colombia

Clasificador supervisado que asigna a un negocio de comida un **nivel de riesgo (Alto, Medio o Bajo)** a partir de sus características, entrenado con la **Encuesta de Micronegocios EMICRON 2024 del DANE** (7.523 negocios). Incluye el análisis (CRISP-DM), la comparación de cuatro modelos, una API en FastAPI y una aplicación web en español.

> **Qué predice y qué no.** La etiqueta `nivel_riesgo` se construyó con la **antigüedad del negocio** (`meses_abierto`): menos antigüedad = más riesgo. El modelo reconoce a qué grupo de antigüedad *se parece* un negocio. **No predice cierres reales ni probabilidades de cierre**: todos los negocios de la encuesta estaban abiertos.

## Resultados en una mirada

| Modelo | F1 macro CV (5 pliegues) | F1 macro prueba | Balanced acc. prueba | Accuracy prueba |
|---|---|---|---|---|
| Regresión logística | 0,427 ± 0,011 | 0,438 | 0,474 | 0,498 |
| **Árbol de decisión (final)** | **0,448 ± 0,011** | **0,451** | **0,464** | **0,500** |
| Random Forest | 0,446 ± 0,007 | 0,467 | 0,493 | 0,527 |
| XGBoost | 0,450 ± 0,013 | 0,467 | 0,497 | 0,521 |
| Línea base: azar estratificado | — | 0,331 | 0,331 | 0,411 |
| Línea base: siempre «Bajo» | — | 0,235 | 0,333 | 0,545 |

* **Regla de la etiqueta:** Alto = 1–11 meses · Medio = 12–42 meses · Bajo = 43 meses o más (16 % / 29 % / 54 %).
* **Modelo final:** árbol de decisión (profundidad 4), elegido con la *regla de un error estándar* sobre la CV: su F1 macro está a menos de un error estándar del de XGBoost y es el más fácil de explicar. El test se usó una sola vez, después de elegir.
* **Variables que más pesan:** edad del propietario y lo que el negocio le deja al mes. Importancia predictiva ≠ causalidad.
* El desempeño es **modesto** (≈ 0,45 de F1 macro frente a 0,33 al azar): las características disponibles explican poco de la antigüedad.

Detalle completo: [`docs/informe_tecnico.md`](docs/informe_tecnico.md) · Cuaderno: [`notebooks/analisis_modelado.ipynb`](notebooks/analisis_modelado.ipynb) · Presentación: [`docs/presentacion.md`](docs/presentacion.md) · Declaración de uso de IA: [`DECLARACION_USO_IA.md`](DECLARACION_USO_IA.md)

## Estructura

```
proyecto_final_ml/
├── data/raw/BASE_1_EMICRON_2024_comida_DANE.xlsx   # base original (no se modifica; se verifica su SHA-256)
├── notebooks/analisis_modelado.ipynb               # narrativa CRISP-DM con resultados ejecutados
├── src/
│   ├── config.py           # rutas, semilla, umbrales de la etiqueta y lista de variables aprobadas
│   ├── data_processing.py  # carga, limpieza, construcción de nivel_riesgo, auditoría de fuga, división 80/20
│   ├── eda.py              # análisis exploratorio (tablas y figuras)
│   ├── modeling.py         # pipelines y espacios de hiperparámetros de los 4 modelos
│   ├── train.py            # validación cruzada, selección y guardado del modelo
│   ├── evaluate.py         # métricas en prueba, matrices de confusión, interpretabilidad
│   ├── predict.py          # validación de entradas y predicción con el modelo guardado
│   └── viz.py              # estilo común de las figuras
├── models/modelo_final.joblib   # pipeline completo (preprocesamiento + árbol) y metadatos
├── app/                         # FastAPI + HTML/CSS/JS
│   ├── main.py
│   ├── templates/index.html
│   └── static/{css,js}/
├── reports/{figures,tables}/    # resultados generados por el código
├── tests/                       # pruebas automatizadas (pytest)
├── docs/                        # informe técnico y guion de presentación
├── DECLARACION_USO_IA.md        # declaración de uso de inteligencia artificial
├── Dockerfile · render.yaml     # despliegue
└── requirements.txt · requirements-app.txt
```

## Instalación

Requiere **Python 3.11 o superior** (probado con 3.13).

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Reproducir el análisis

Ejecutar desde la raíz del repositorio:

```bash
python -m src.eda        # tablas y figuras exploratorias            (~10 s)
python -m src.train      # CV de los 4 modelos y guardado del final  (~4 min)
python -m src.evaluate   # evaluación en prueba e interpretabilidad   (~30 s)
pytest                   # 45 pruebas automatizadas
```

La semilla es `42` (en `src/config.py`); volver a ejecutar produce los mismos resultados.

## Ejecutar la aplicación

```bash
uvicorn app.main:app --reload
```

Abrir <http://127.0.0.1:8000>. La documentación interactiva de la API está en <http://127.0.0.1:8000/docs>.

| Endpoint | Método | Uso |
|---|---|---|
| `/` | GET | Aplicación web |
| `/api/health` | GET | Estado del servicio y del modelo |
| `/api/metadata` | GET | Campos y opciones del formulario (leídos del modelo guardado) |
| `/api/predict` | POST | Clasificación de un negocio (JSON con las 13 variables) |

Ejemplo:

```bash
curl -X POST http://127.0.0.1:8000/api/predict -H "Content-Type: application/json" -d '{
  "donde_funciona": "Local o tienda", "como_lleva_cuentas": "Libro diario",
  "visible_desde_la_calle": "Sí", "zona": "Cabecera (urbana)", "tiene_ayudantes": "Sí",
  "acepta_transferencias": "Sí", "tiene_nombre_comercial": "Sí", "registrado_camara_comercio": "Sí",
  "tiene_RUT": "Sí", "usa_internet": "Sí", "tiene_redes_sociales": "Sí",
  "edad_propietario": 58, "le_deja_al_mes_COP": 3150000}'
```

Las entradas inválidas (campos vacíos, números fuera de rango, categorías desconocidas, `meses_abierto` en la solicitud) se rechazan con código 422 y mensajes en español, sin detalles técnicos.

## Despliegue

**Estado actual: no desplegado.** El entorno donde se construyó el proyecto no tiene credenciales de un servicio de hosting. Se verificó:

* La aplicación funciona localmente y en un entorno virtual limpio instalado solo con `requirements-app.txt`.
* El `Dockerfile` **no** pudo probarse de punta a punta: el entorno de desarrollo bloquea la descarga de paquetes dentro de contenedores. Debe probarse con `docker build` en un equipo con internet.

### Opción A · Render (gratis, recomendado)
1. Subir el repositorio a GitHub.
2. En <https://render.com>: **New → Blueprint** y seleccionar el repositorio. Render lee `render.yaml` y construye el `Dockerfile`.
3. Al terminar, abrir la URL `https://<nombre>.onrender.com/api/health`; debe responder `{"estado":"ok", ...}`. Luego probar una predicción desde la página.

### Opción B · Hugging Face Spaces (Docker)
1. Crear un Space de tipo **Docker** y subir `Dockerfile`, `requirements-app.txt`, `src/`, `app/` y `models/modelo_final.joblib`.
2. Agregar al inicio del `README.md` del Space `app_port: 8000` en el bloque YAML de configuración.

### Opción C · Cualquier equipo con Docker
```bash
docker build -t termometro-riesgo .
docker run -p 8000:8000 termometro-riesgo
```

## Limitaciones

1. Sesgo de supervivencia: no hay negocios cerrados; la etiqueta mide antigüedad, no fracaso.
2. Datos de corte transversal (2024) y autorreportados (meses e ingresos redondeados).
3. Señal débil: F1 macro ≈ 0,45; la clase Medio es la más difícil (F1 ≈ 0,33).
4. Los umbrales de la etiqueta son una decisión del proyecto, no una clasificación oficial del DANE.
5. No se usan los factores de expansión del DANE: los resultados describen la muestra.
6. El modelo depende mucho de la edad del propietario; no debe usarse para tomar decisiones sobre personas.

## Fuente de datos

Departamento Administrativo Nacional de Estadística [DANE]. (2025). *Encuesta de Micronegocios (EMICRON) 2024* [Conjunto de datos]. https://microdatos.dane.gov.co/index.php/catalog/875
