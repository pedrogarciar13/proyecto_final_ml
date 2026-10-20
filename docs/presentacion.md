# Guion de presentación (≈ 10 minutos + preguntas)

Prioridad: resultados, decisiones metodológicas y demostración. Sin código en las diapositivas.

| # | Diapositiva | Contenido clave | Visual | Tiempo |
|---|---|---|---|---|
| 1 | **Título** | "¿A qué grupo de riesgo se parece un negocio de comida?" · EMICRON 2024 · nombres | Logo del termómetro | 0:20 |
| 2 | **Problema y pregunta** | Micronegocios de comida; la pregunta orientadora; objetivo general | Una frase grande + 3 objetivos | 0:50 |
| 3 | **Datos** | 7.523 negocios, 16 columnas, sin nulos; qué es EMICRON; hallazgos (respuestas redondeadas, ingreso muy asimétrico, `riesgo_financiero` = ingreso < $650.000) | Tabla pequeña de hallazgos | 1:00 |
| 4 | **Cómo se definió el riesgo** | Alto < 12 meses · Medio 12–42 · Bajo > 42; por qué (primer año crítico; umbral GEM de 42 meses; evitar el pico de 36); 16/29/54 % | `01_distribucion_meses_abierto.png` + barras de clases | 1:20 |
| 5 | **Lo que el modelo NO hace** | Todos los negocios estaban abiertos → no predice cierres; "Alto" = se parece a negocios en su primer año | Recuadro de advertencia | 0:30 |
| 6 | **Auditoría de fuga** | `meses_abierto` solo para la etiqueta; fuera `riesgo_financiero` e `id`; ingreso y edad incluidos con justificación; todo el preprocesamiento dentro del pipeline | Tabla Incluida/Excluida con colores | 1:00 |
| 7 | **Metodología** | CRISP-DM; 80/20 estratificado; CV de 5 pliegues; F1 macro; pesos balanceados; regla de una desviación estándar | Diagrama de flujo simple | 0:50 |
| 8 | **Resultados** | Cuatro modelos ≈ 0,44–0,47 F1 macro vs 0,33 azar; accuracy engaña ("siempre Bajo" = 0,54) | `06_comparacion_modelos.png` | 1:10 |
| 9 | **Modelo elegido y errores** | Árbol (profundidad 4): empatado con XGBoost en CV y explicable; la clase Medio es la difícil; errores entre clases vecinas | `05_matrices_confusion.png` (solo el árbol, ampliado) | 1:00 |
| 10 | **¿Qué mira el modelo?** | Edad del propietario y su ingreso; importancia ≠ causalidad | `08_importancia_permutacion.png` | 0:40 |
| 11 | **Demostración en vivo** | Ejemplo joven ambulante → Alto; restaurante formal → Bajo; caso rural → Medio con puntajes casi iguales (mostrar incertidumbre) | Aplicación web | 1:30 |
| 12 | **Limitaciones y próximos pasos** | Supervivencia, corte transversal, señal débil; qué datos harían falta para predecir cierres | 3 + 3 viñetas | 0:40 |

**Plan B para la demo:** capturas de pantalla de la aplicación (escritorio y móvil) por si falla la conexión, y la app corriendo localmente (`uvicorn app.main:app`).

---

## Respuestas breves a preguntas previsibles

**¿Por qué esa variable objetivo?**
Porque la base no tiene información de cierres: todos los negocios estaban abiertos. La antigüedad es el dato disponible más cercano a la idea de riesgo (los negocios jóvenes son los más expuestos). Lo presentamos como una aproximación, no como una medida de fracaso.

**¿Cómo se definieron los niveles?**
Alto: primer año (1–11 meses), la etapa con mayor mortalidad empresarial. Medio: 12–42 meses, negocios "nuevos" según el GEM. Bajo: más de 42 meses, negocios "establecidos" según el GEM. Evitamos cortar en 36 porque ahí hay un pico de respuestas redondeadas ("3 años"). Los cortes se fijaron antes de entrenar.

**¿Cómo evitaron la fuga de información?**
`meses_abierto` solo se usó para crear la etiqueta y hay una verificación automática que impide que entre a X. Excluimos `riesgo_financiero` (es el ingreso con un umbral) y el identificador. Separamos el 20 % de prueba antes de todo; la imputación, codificación, escalado y pesos de clase se ajustan dentro de cada pliegue con `Pipeline`; el test se usó una sola vez.

**¿Y el ingreso no es fuga? El diccionario decía que sí.**
Esa advertencia era para el objetivo anterior (`riesgo_financiero`, que se calcula con el ingreso). Para `nivel_riesgo`, el ingreso no se deriva de la antigüedad (correlación 0,18) y el dueño lo conoce al momento de responder. Sí aclaramos que es contemporáneo: podría ser consecuencia de la antigüedad, por eso no hablamos de causalidad.

**¿Por qué esos cuatro modelos?**
Cubren el espectro de complejidad en datos tabulares: un modelo lineal de referencia (logística), uno de reglas interpretable (árbol) y dos ensambles de árboles, *bagging* (Random Forest) y *boosting* (XGBoost).

**¿Cómo eligieron el mejor?**
Con F1 macro de validación cruzada y la regla de una desviación estándar: XGBoost fue el mejor (0,450 ± 0,013), pero el árbol (0,448) está dentro de esa variación. Entre modelos equivalentes preferimos el más simple. En el test, XGBoost y Random Forest quedaron 0,016 por encima; no cambiamos la decisión con el test para no contaminarlo.

**¿Qué significan las métricas?**
Precision: de los que el modelo llamó "Alto", cuántos lo eran. Recall: de los "Alto" reales, cuántos encontró. F1: equilibrio de ambas. F1 macro: promedio de las tres clases, cada una con el mismo peso; por eso es justa con la clase minoritaria. Accuracy no sirve sola: decir siempre "Bajo" da 54 % de accuracy y no detecta ningún negocio en riesgo.

**¿Por qué el desempeño es tan bajo?**
Porque las características disponibles explican poco de la antigüedad: un negocio de 11 meses y uno de 13 se parecen mucho. Preferimos un modelo honesto de 0,45 a uno con 0,90 inflado por fuga.

**¿Cuáles son las limitaciones de los datos?**
Sesgo de supervivencia, una sola medición en el tiempo, respuestas redondeadas y autorreportadas, posible tope en 500 meses, y no usamos los factores de expansión del DANE.

**¿Qué significa realmente la predicción?**
"Este negocio tiene características parecidas a las de los negocios que llevaban X tiempo abiertos en la encuesta." No es una probabilidad de cierre. Los porcentajes indican qué tan mezclado es el grupo de negocios parecidos.

**¿Qué haría falta para predecir cierres reales?**
Seguir a los mismos negocios en el tiempo (panel), observar si cerraron después del momento de predicción, incluir negocios que cerraron, y variables previas como capital inicial, deudas o experiencia. Con eso se podría usar análisis de supervivencia.

**¿Es ético usar la edad del propietario?**
Es la variable más informativa, pero el modelo es descriptivo y académico. No debe usarse para negar crédito u oportunidades por edad. Mostramos cuánto cae el desempeño sin ella (F1 macro de 0,448 a 0,353).
