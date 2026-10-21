# Trazabilidad CRISP-DM · retos R10 a R18

Cada reto acumulativo del curso es un paso del proyecto. Esta tabla dice en qué fase de CRISP-DM cae cada reto y qué archivo del repositorio lo demuestra.

| Reto | Fase CRISP-DM | Qué se pedía | Evidencia en el repositorio |
|---|---|---|---|
| R10 | Comprensión del negocio | Anteproyecto: problema y decisión, enfoque, datos candidatos, métrica de éxito y riesgos | [`docs/retos/R10_Anteproyecto_PFI_LUMO.pdf`](retos/R10_Anteproyecto_PFI_LUMO.pdf) (8 de octubre de 2026). Declara el enfoque de emprendimiento con LUMO, que se mantuvo hasta la entrega |
| R11 | Comprensión de los datos | Ficha de datos y diagnóstico de calidad | [`docs/ficha_datos.md`](ficha_datos.md), [`reports/tables/calidad_datos.csv`](../reports/tables/calidad_datos.csv), [`reports/tables/hallazgos_datos.csv`](../reports/tables/hallazgos_datos.csv), [`reports/tables/resumen_numericas.csv`](../reports/tables/resumen_numericas.csv) |
| R12 | Preparación de los datos | Diseño experimental sin fuga, línea base e interpretación inicial | [`src/data_processing.py`](../src/data_processing.py) (etiqueta, partición 80/20 estratificada), [`reports/tables/auditoria_variables.csv`](../reports/tables/auditoria_variables.csv) (auditoría de fuga), [`tests/test_data_processing.py`](../tests/test_data_processing.py) (pruebas de ausencia de fuga), líneas base en [`reports/tables/metricas_prueba.csv`](../reports/tables/metricas_prueba.csv) |
| R13 | Modelado y evaluación | Comparación de modelos con validación cruzada y modelo final preliminar | [`src/modeling.py`](../src/modeling.py), [`src/train.py`](../src/train.py), [`reports/tables/comparacion_cv.csv`](../reports/tables/comparacion_cv.csv), `reports/tables/cv_resultados_*.csv`, [`reports/tables/seleccion_modelo.json`](../reports/tables/seleccion_modelo.json) |
| R14 | Modelado (avance consolidado) | Informe de avance hasta el modelado | [`docs/retos/R14_Avance_PFI_LUMO_16oct.pdf`](retos/R14_Avance_PFI_LUMO_16oct.pdf) (16 de octubre de 2026) y [`notebooks/analisis_modelado.ipynb`](../notebooks/analisis_modelado.ipynb) |
| R15 a R17 | Modelado y evaluación (no supervisado) | Estructura latente y segmentos, cuando aplique | No se aplicó: la decisión de LUMO se resuelve con clasificación supervisada. Queda como trabajo futuro (segmentar prospectos por perfil) |
| R18 | Despliegue y cierre | Resumen ejecutivo en inglés, riesgos, plan de seguimiento y presentación | `resumen_ejecutivo_EN.pdf` (en el .zip de entrega), plan de seguimiento en la sección 6 del informe, [`docs/presentacion.md`](presentacion.md), aplicación en [`app/`](../app/) desplegada en https://termometro-riesgo-negocios.onrender.com/ |

## Cambios de rumbo documentados

- **Datos (entre R10 y R14):** el anteproyecto proponía el registro mercantil (RUES) para predecir el cierre a 3 años. Se descartó como base principal porque solo trae 4 variables útiles y no incluye informales; se cambió a la EMICRON 2024 del DANE. El RUES queda como contexto (26,6 % de cierre antes de 3 años). Ver R14.
- **Variable objetivo (después de R14):** el avance usaba riesgo financiero (le deja menos de $650.000 al mes). El modelo final usa la etapa del negocio según su antigüedad (`nivel_riesgo`), porque la EMICRON solo tiene negocios abiertos y la decisión de LUMO es qué mensaje enviar según la etapa. Ver la sección 1 del informe y `docs/informe_tecnico.md`.
