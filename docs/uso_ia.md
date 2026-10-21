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
* **Modificado:** la primera regla de selección de modelo combinaba F1 macro, balanced accuracy y complejidad, y elegía Random Forest. Se reemplazó por la regla estándar de una desviación estándar (más simple de defender), que elige el árbol. El cambio se hizo con resultados de **validación cruzada únicamente**, antes de evaluar en el conjunto de prueba. Se deja constancia porque es una decisión tomada después de ver resultados de CV.
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

## 8. Uso de IA de Santiago Simanca

| Campo | Detalle |
|---|---|
| Herramienta | Claude (Anthropic), en la app de Claude |
| Para qué la usó | Conseguir y unir los datos del DANE (EMICRON 2024) y del RUES; perfilar la base; revisar el prompt y el termómetro de Pedro contra la rúbrica; redactar las secciones 1, 2, 6 y 7 del informe, la ficha de datos y los anexos A y B; armar la trazabilidad de los retos; preparar la integración del termómetro en LUMO |

**Prompts principales**
1. "Ayúdame a conseguir datos públicos reales de restaurantes en Colombia para el proyecto final y a revisar si sirven para el termómetro."
2. "Revisa el prompt de Pedro contra las instrucciones del proyecto, prueba el termómetro y dime qué sigue."
3. "Hagamos mi parte del informe (secciones 1, 2, 6 y 7, ficha de datos y anexos A y B) con el modelo de Pedro, orientada a que LUMO decida a quién escribirle y qué mensaje enviarle."
4. "¿Puedo correr el modelo dentro de LUMO? Dame un prompt para integrarlo."

**Qué aceptó**
* La unión de 8 módulos de EMICRON 2024 y el filtro de negocios de comida (7.523 filas).
* Los porcentajes y el diagnóstico de calidad calculados con código sobre el Excel (faltantes, duplicados, desbalance y tasas de cierre del RUES).
* La lectura de los niveles del modelo como etapa del negocio para decidir el mensaje comercial.
* La prueba independiente de que la edad del propietario explica casi todo el desempeño (F1 macro de 0,43 con edad y ganancia; 0,35 sin edad), que coincide con `reports/tables/sensibilidad_variables.csv`.
* La estructura de los anexos y la estimación de impacto con USD 50 por cliente.

**Qué descartó o corrigió**
* Presentar el termómetro como "probabilidad de cierre a 3 años": la base solo tiene negocios abiertos.
* Cambiar el objetivo del modelo a última hora: decidió mantener el de Pedro y ajustar la lectura para LUMO.
* La sección de microcredenciales del bono de enfoque.

**Qué verificó**
* Las cifras de sus secciones contra el Excel y contra las tablas de `reports/tables/`.
* El termómetro desplegado en Render con casos de prueba y entradas inválidas.

**Qué puede explicar sin la herramienta**
* Por qué el modelo no predice cierres.
* Por qué la edad del propietario es un riesgo técnico y ético.
* Por qué se usa F1 macro y no exactitud cuando "Alto" es solo el 16 %.
* Por qué LUMO consulta el modelo en Render y no lo ejecuta él mismo.

