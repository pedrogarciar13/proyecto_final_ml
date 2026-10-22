# Transparencia en el uso de inteligencia artificial

> Este documento lo inicia la herramienta de IA con lo que hizo. **El equipo debe completarlo** con su propia revisión antes de entregar (marcado como *[Completar por el equipo]*).

## 1. Herramienta utilizada
* **Claude Code** (Anthropic), agente de programación que trabajó directamente sobre el repositorio en un entorno en la nube.
* Fecha de trabajo: 20 de octubre de 2026.

## 2. Instrucciones proporcionadas
* Documento `PROMPT.docx` del equipo (requisitos del proyecto: rol, datos, variable objetivo, reglas contra la fuga de información, cuatro modelos, aplicación web, pruebas, despliegue, documentación y transparencia).
* Archivo de datos `BASE_1_EMICRON_2024_comida_DANE.xlsx`.

## 3. Tareas en las que se usó
| Tarea | Qué hizo la IA |
|---|---|
| Inspección de datos | Leyó las 4 hojas del Excel, verificó tipos, nulos, duplicados, rangos y relaciones (p. ej., descubrió que `riesgo_financiero` = ingreso < $650.000) |
| Variable objetivo | Comparó varias reglas de cortes (12/36, 12/48, 12/60, 24/60, cuartiles) sobre la distribución y propuso 12/42 con justificación (GEM, primer año, pico de redondeo en 36) |
| Código | Escribió `src/`, `app/`, `tests/`, `Dockerfile`, `render.yaml` |
| Ejecución | Entrenó y evaluó los modelos, generó tablas y figuras, ejecutó el cuaderno y las pruebas |
| Interfaz | Diseñó la aplicación web y la revisó con capturas automatizadas (escritorio, móvil, modo oscuro) |
| Documentación | Redactó `README.md`, `docs/informe_tecnico.md`, `docs/presentacion.md` y este archivo |

## 4. Resultados aceptados, modificados o rechazados durante el trabajo
* **Rechazado:** adoptar automáticamente el corte ilustrativo 12/36 del enunciado (cae sobre un pico de respuestas "3 años").
* **Modificado:** la primera regla de selección de modelo combinaba F1 macro, balanced accuracy y complejidad, y elegía Random Forest. Se reemplazó por una regla de una desviación estándar, que elige el árbol, usando solo resultados de validación cruzada y antes de evaluar en el conjunto de prueba.
* **Corregido por revisión:** se señaló que la «regla de una desviación estándar» no coincidía con la regla de un error estándar de Hastie, Tibshirani y Friedman (2009), que se citaba. El código y los textos se corrigieron para usar el error estándar de la media (desviación estándar muestral de los 5 pliegues dividida por √5). El modelo elegido no cambió.
* **Rechazado:** usar `riesgo_financiero` como predictora (redundante con el ingreso).
* **Mantenido pese a un resultado de test desfavorable:** en prueba, Random Forest y XGBoost superan al árbol por 0,016 de F1 macro; no se cambió el modelo para no ajustar con el test.
* **Corregido:** errores de programación detectados al ejecutar (un formato de texto en un gráfico, una prueba que leía mal los nombres de columnas del codificador) y un resumen incorrecto de las reglas del árbol en el informe, corregido al compararlo con el archivo de reglas exportado.
* *[Completar por el equipo: qué resultados de la IA aceptaron, cambiaron o descartaron después de revisarlos.]*

## 5. Verificaciones realizadas
* Todas las cifras de la documentación provienen de archivos generados por el código (`reports/tables/`); el entrenamiento se ejecutó dos veces con resultados idénticos (semilla 42).
* 45 pruebas automatizadas aprobadas (`pytest`), incluidas pruebas de ausencia de fuga y de límites de la etiqueta.
* La aplicación se probó en un entorno virtual limpio con solo las dependencias de despliegue.
* El `Dockerfile` **no** pudo verificarse de punta a punta (el entorno bloquea descargas dentro de contenedores).
* *[Completar por el equipo: revisiones propias del código, de la regla de la etiqueta y de las conclusiones.]*

## 6. Fuentes externas consultadas
* Hoja LEEME del archivo de datos (referencia del DANE).
* Búsquedas web sobre las definiciones del *Global Entrepreneurship Monitor* (42 meses) y los estudios de supervivencia de Confecámaras. **Solo se vieron resúmenes de resultados de búsqueda**; los documentos originales no pudieron abrirse desde el entorno. Deben verificarse antes de citarlos (ver sección 16 del informe).
* Documentación de las bibliotecas (scikit-learn, XGBoost, FastAPI) a partir del conocimiento del modelo; no se descargaron páginas.
* No se inventaron referencias: las que no fueron verificadas están marcadas como pendientes.

## 7. Responsabilidad
El equipo es responsable de entender, verificar y defender cada decisión. Se recomienda leer en orden: `docs/informe_tecnico.md` → `notebooks/analisis_modelado.ipynb` → `src/data_processing.py` → `src/train.py`.
