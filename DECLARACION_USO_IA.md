# DECLARACIÓN DE USO DE INTELIGENCIA ARTIFICIAL

**Trabajo académico:** Proyecto final de Machine Learning - Clasificación del nivel de riesgo de negocios de comida en Colombia.

**Herramientas utilizadas:** Claude, Claude Code y ChatGPT.

## ¿Qué se aceptó?

Se aceptó el uso de Claude Code como apoyo para la implementación del código y el despliegue del modelo, incluyendo el trabajo con un repositorio de GitHub. Asimismo, durante la elaboración del informe final, se incorporaron sugerencias de corrección y ajustes de redacción, especialmente en las secciones 3, 4 y 5, con el propósito de corregir interpretaciones erróneas, mejorar la claridad de las explicaciones y garantizar una mayor coherencia en la presentación de los resultados.

## ¿Qué se descartó y qué se corrigió?

Aunque se verificó que la selección del modelo final fuera consistente con los resultados obtenidos, se identificó y corrigió un error metodológico en el procedimiento utilizado por Claude Code para determinar si dos modelos presentaban resultados estadísticamente similares. Adicionalmente, se detectó una atribución incorrecta a Hastie, Tibshirani y Friedman (2009), cuya referencia se utilizó para justificar un criterio que no correspondía al procedimiento efectivamente aplicado.

El error consistió en utilizar la desviación estándar de los resultados de los cinco pliegues de validación cruzada, en lugar del error estándar de la media, para establecer el margen de equivalencia entre modelos. Mientras que la desviación estándar mide la variabilidad de los resultados entre pliegues, el error estándar permite estimar la incertidumbre asociada a la media obtenida. Para XGBoost, el error estándar calculado fue de 0,0067, mientras que la desviación estándar utilizada originalmente fue de aproximadamente 0,013.

Esta diferencia amplió indebidamente el margen de tolerancia y estableció un límite de 0,437, en lugar del valor corregido de 0,4436. En consecuencia, el criterio original era más permisivo de lo que correspondía y la justificación metodológica presentada en el informe no coincidía con el procedimiento que se citaba.

Tras corregir el cálculo, el resultado del árbol de decisión (0,4479) continuó por encima del límite establecido, por lo que la selección del modelo final no cambió. Sin embargo, se corrigieron tanto el procedimiento de evaluación como su justificación teórica, con el fin de asegurar que la metodología descrita en el informe fuera coherente con los cálculos realizados y las referencias utilizadas.

## Prompt utilizado

**Machine Learning - Clasificación del nivel de riesgo de negocios de comida en Colombia**

### 1. Rol y contexto

Actúa como un científico de datos senior, ingeniero de machine learning y desarrollador full-stack, con experiencia en proyectos académicos de ciencia de datos, modelos de clasificación supervisada y desarrollo de aplicaciones web interactivas.

Estoy desarrollando un proyecto final para mi Maestría en Ciencia de Datos y mi Especialización en Machine Learning. El proyecto consiste en construir un modelo de clasificación que permita estimar el nivel de riesgo asociado a las características de un negocio de comida en Colombia, utilizando información de la encuesta EMICRON 2024 del DANE.

Necesito desarrollar una solución completa, técnicamente sólida, reproducible, visualmente profesional y fácil de explicar durante una presentación académica.

Trabaja directamente con los archivos del proyecto y con la base de datos proporcionada. Antes de modificar o crear archivos, inspecciona la estructura existente del repositorio, identifica los archivos relevantes y comprende el contenido de los datos. No sobrescribas archivos existentes sin verificar primero su función.

### 2. Base de datos

El archivo principal es:

BASE_1_EMICRON_2024_comida_DANE.xlsx

El archivo contiene las siguientes hojas:

- LEEME
- Datos
- Resumen
- Diccionario

La hoja principal para el análisis es Datos. Consulta las demás hojas para comprender la fuente, las definiciones, los códigos y el significado de las variables.

La base contiene aproximadamente 7.523 registros relacionados con negocios de comida, según el contexto inicial del proyecto. Verifica el número real de registros y columnas antes de comenzar el análisis.

#### Instrucciones para trabajar con los datos

1. Inspecciona las hojas del archivo Excel.
2. Identifica los tipos de datos, valores faltantes, duplicados, categorías, valores atípicos y posibles inconsistencias.
3. Consulta el diccionario de variables antes de interpretar códigos o valores categóricos.
4. No supongas que los nombres de las columnas, sus unidades o sus categorías tienen un significado que no esté respaldado por los datos o el diccionario.
5. Documenta los problemas encontrados y las decisiones de limpieza.
6. Conserva una copia de la base original sin modificaciones.
7. Realiza todas las transformaciones necesarias mediante código reproducible.
8. Evita eliminar registros o columnas sin justificar técnicamente la decisión.
9. No inventes datos, categorías ni resultados experimentales.

### 3. Objetivo general del proyecto

Desarrollar un sistema de clasificación supervisada que, a partir de características observables de un negocio de comida, prediga su categoría de nivel_riesgo: Alto, Medio o Bajo.

El sistema debe contar con:

- Análisis exploratorio de datos.
- Preparación y transformación de variables.
- Definición documentada de la variable objetivo.
- Entrenamiento y comparación de cuatro modelos de clasificación.
- Evaluación rigurosa de los modelos.
- Selección y guardado del mejor modelo.
- Una aplicación web en HTML que permita ingresar las características de un negocio y obtener su clasificación.
- Documentación técnica y material de apoyo para la presentación académica.

La aplicación debe explicar el resultado de manera comprensible para una persona que no tenga conocimientos de machine learning.

#### Pregunta orientadora del negocio

“¿Qué nivel de riesgo puede tener un negocio de comida, según sus características, utilizando la antigüedad del negocio como criterio para definir las categorías de riesgo?”

Es importante mantener la precisión metodológica: si la variable objetivo se construye a partir de la antigüedad del negocio, el modelo aprenderá a predecir categorías definidas mediante esa antigüedad. Esto no demuestra por sí solo la probabilidad real de que el negocio cierre durante los próximos tres años.

No afirmes que el modelo predice cierres reales futuros, probabilidades de cierre o causalidad si los datos disponibles no permiten demostrarlo.

### 4. Construcción de la variable objetivo: nivel_riesgo

La variable objetivo del proyecto será una nueva columna denominada:

nivel_riesgo

Esta columna debe construirse a partir de la variable original:

meses_abierto

La columna meses_abierto se utilizará exclusivamente para crear las etiquetas de la variable objetivo. **Nunca debe incorporarse como variable predictora al modelo.**

#### Reglas obligatorias

1. Inspecciona la distribución de meses_abierto.
2. Verifica su significado, unidad de medida, valores faltantes, valores negativos, valores atípicos y posibles inconsistencias.
3. Consulta el diccionario de datos para confirmar cómo está definida la variable.
4. Propón y documenta una regla clara para transformar meses_abierto en tres categorías:
  - Alto
  - Medio
  - Bajo
5. Justifica los umbrales utilizados con criterios de negocio, la distribución de los datos y el contexto académico.
6. No selecciones los umbrales únicamente porque produzcan mejores métricas de clasificación.
7. Registra los límites exactos de cada categoría para que la transformación pueda reproducirse.
8. Muestra la cantidad y el porcentaje de registros pertenecientes a cada categoría.
9. Comprueba que las categorías no se solapen y que todos los registros válidos queden asignados correctamente.
10. Explica el tratamiento de los registros cuyo valor de meses_abierto sea nulo o inválido.

Si los umbrales no están definidos en los materiales del proyecto, presenta una propuesta justificada y documenta que se trata de una decisión metodológica del proyecto, no de una clasificación oficial del DANE.

Como ejemplo exclusivamente ilustrativo, se podría evaluar una regla como la siguiente:

- Menos de 12 meses: Alto.
- Desde 12 meses y menos de 36 meses: Medio.
- 36 meses o más: Bajo.

Estos umbrales no deben adoptarse automáticamente. Primero deben revisarse la distribución de los datos, la definición de la variable y la justificación de negocio.

La interpretación de las categorías debe quedar explícita. Si se decide asociar menor antigüedad con mayor riesgo, explica que es una aproximación basada en la antigüedad y no una medición directa de cierres reales.

### 5. Variables predictoras y prevención de fuga de información

Las siguientes variables son candidatas iniciales para predecir nivel_riesgo:

- donde_funciona
- como_lleva_cuentas
- tiene_ayudantes
- acepta_transferencias
- tiene_nombre_comercial
- registrado_camara_comercio
- tiene_RUT
- visible_desde_la_calle
- usa_internet
- tiene_redes_sociales
- zona
- edad_propietario
- le_deja_al_mes_COP
- riesgo_financiero

Verifica que los nombres coincidan exactamente con las columnas existentes en la base. Si existen diferencias, identifica las columnas equivalentes y documenta los cambios; no inventes variables.

#### Reglas estrictas contra el data leakage

La variable objetivo será nivel_riesgo.

La variable meses_abierto se utilizará únicamente para generar nivel_riesgo y queda prohibido incluirla en las variables predictoras X.

También queda prohibido:

1. Incluir nivel_riesgo dentro de X.
2. Incluir variables que reproduzcan directa o indirectamente la regla usada para construir nivel_riesgo.
3. Utilizar identificadores únicos, códigos de registro o variables que permitan identificar directamente el registro sin aportar información predictiva legítima.
4. Incorporar variables que solo puedan conocerse después del momento en el que se supone que se realiza la predicción.
5. Calcular estadísticas de preprocesamiento utilizando conjuntamente los datos de entrenamiento y prueba.
6. Seleccionar variables o ajustar hiperparámetros observando repetidamente los resultados del conjunto de prueba.
7. Usar información derivada de la variable objetivo que permita reconstruirla directa o indirectamente.

Antes de entrenar los modelos, realiza una auditoría de fuga de información y documenta las variables excluidas y la razón de cada exclusión.

#### Revisión especial de variables candidatas

Revisa particularmente le_deja_al_mes_COP y riesgo_financiero.

No las excluyas automáticamente, porque no son la variable utilizada directamente para construir la etiqueta. Sin embargo, analiza:

- Qué representan realmente.
- Si están disponibles en el momento de hacer la predicción.
- Si su definición incluye información derivada de meses_abierto o de nivel_riesgo.
- Si existe una relación que pueda revelar indirectamente la variable objetivo.
- Si su inclusión es metodológicamente apropiada.

Toma una decisión justificada para cada una.

Al finalizar, presenta una tabla con:

- Nombre de la variable.
- Tipo de dato.
- Descripción.
- Uso previsto.
- Si se incluye o excluye del modelo.
- Justificación.

La tabla debe diferenciar claramente las variables utilizadas para construir la etiqueta de las utilizadas como predictoras.

### 6. Metodología de machine learning

Sigue la metodología CRISP-DM:

1. Comprensión del negocio.
2. Comprensión de los datos.
3. Preparación de los datos.
4. Modelado.
5. Evaluación.
6. Despliegue.

Documenta cada etapa y explica cómo las decisiones tomadas responden al objetivo del proyecto.

#### División de los datos

Divide los datos en:

- 80 % para entrenamiento.
- 20 % para prueba.

Utiliza una semilla aleatoria fija para que los resultados sean reproducibles.

Siempre que la distribución de clases lo permita, utiliza una división estratificada por nivel_riesgo.

El conjunto de prueba debe mantenerse aislado durante la selección del modelo y los ajustes de hiperparámetros.

#### Preprocesamiento

Diseña un proceso de preprocesamiento apropiado para las variables disponibles:

- Imputación de valores faltantes.
- Codificación de variables categóricas.
- Escalado cuando el algoritmo lo requiera.
- Tratamiento justificado de valores atípicos.
- Conversión correcta de tipos de datos.

Utiliza Pipeline y ColumnTransformer de scikit-learn cuando sea apropiado.

Ajusta todos los transformadores únicamente con los datos de entrenamiento. La imputación, codificación, escalado y selección de características deben realizarse dentro del flujo de entrenamiento para evitar fuga de información.

No apliques escalado a todos los modelos de manera automática si no es necesario.

Si existe desbalance de clases, analiza su magnitud y evalúa estrategias apropiadas. No apliques sobremuestreo ni técnicas como SMOTE antes de dividir los datos. Si se utiliza una técnica de balanceo, debe ejecutarse únicamente dentro de los pliegues de entrenamiento correspondientes.

#### Validación cruzada

Utiliza validación cruzada estratificada para comparar los modelos y ajustar hiperparámetros.

Documenta:

- Número de pliegues.
- Métrica principal de selección.
- Espacio de hiperparámetros evaluado.
- Criterio utilizado para elegir el modelo final.

No elijas el modelo exclusivamente por su accuracy.

### 7. Modelos de clasificación obligatorios

Entrena y compara cuatro modelos de clasificación supervisada:

1. Regresión logística.
2. Árbol de decisión.
3. Random Forest.
4. XGBoost.

Si XGBoost no está instalado, verifica las dependencias y documenta la solución necesaria. No reemplaces silenciosamente el modelo por otro algoritmo.

Para cada modelo:

- Explica brevemente cómo funciona.
- Describe las decisiones principales de configuración.
- Ajusta hiperparámetros mediante validación cruzada.
- Evalúa su desempeño con los mismos datos y criterios.
- Registra los resultados de manera reproducible.

Utiliza pipelines para garantizar que el preprocesamiento se ajuste correctamente dentro de cada entrenamiento.

Si alguna variable presenta categorías poco frecuentes o valores inesperados, maneja el caso de manera consistente entre entrenamiento y predicción.

### 8. Evaluación y selección del modelo

Evalúa los modelos utilizando el conjunto de prueba reservado.

Incluye, como mínimo:

- Accuracy.
- Precision.
- Recall.
- F1-score.
- F1-score macro.
- Matriz de confusión.
- Classification report por clase.

Utiliza nivel_riesgo con sus tres clases: Alto, Medio y Bajo.

Presta especial atención al desempeño por clase. Una métrica global alta puede ocultar resultados deficientes en una categoría minoritaria.

Selecciona el modelo final a partir de criterios explícitos, considerando el equilibrio entre las clases y el objetivo de clasificación.

Explica por qué el modelo elegido es preferible a los demás.

Presenta:

- Una tabla comparativa de los cuatro modelos.
- Gráficos de matrices de confusión.
- Métricas por clase.
- Una explicación de los errores de clasificación más relevantes.
- Las limitaciones de los resultados.

Si utilizas probabilidades de clase, verifica si el modelo seleccionado las proporciona correctamente. No presentes las probabilidades como probabilidades reales de cierre del negocio: corresponden a la estimación de pertenencia a las clases definidas, salvo que exista una validación adicional que permita otra interpretación.

No inventes resultados. Ejecuta el código y utiliza los valores realmente obtenidos.

### 9. Interpretabilidad del modelo

Incluye una explicación de las variables que más contribuyen a las predicciones.

Utiliza métodos adecuados para el modelo seleccionado, como:

- Coeficientes, para la regresión logística.
- Importancia de características, para modelos basados en árboles.
- Permutation importance.
- SHAP, si su implementación es compatible con el modelo y el entorno.

Distingue entre importancia predictiva y causalidad. No afirmes que una variable causa un mayor riesgo únicamente porque el modelo la utiliza para clasificar.

Prepara visualizaciones comprensibles que permitan explicar los resultados durante la presentación.

### 10. Aplicación web en HTML

Desarrolla una aplicación web visualmente profesional para utilizar el modelo entrenado.

La aplicación debe estar en español y permitir que un usuario ingrese las características de un negocio de comida y obtenga su clasificación.

El diseño debe tener una apariencia premium, moderna y limpia, con buena jerarquía visual, tipografía legible, tarjetas, formularios claros, indicadores visuales y adaptación a diferentes tamaños de pantalla.

Evita una apariencia de plantilla genérica. El resultado debe parecer un producto de analítica de datos terminado y coherente.

#### Formulario de entrada

Incluye campos para las variables predictoras aprobadas después de la auditoría:

- Dónde funciona el negocio.
- Cómo lleva las cuentas.
- Si tiene ayudantes.
- Si acepta transferencias.
- Si tiene nombre comercial.
- Si está registrado en la Cámara de Comercio.
- Si tiene RUT.
- Si es visible desde la calle.
- Si usa internet.
- Si tiene redes sociales.
- Zona.
- Edad del propietario.
- Ingreso mensual o valor mensual representado por le_deja_al_mes_COP, según el diccionario.
- Indicador de riesgo_financiero, solo si se confirma que es válido y está disponible al momento de la predicción.

Los nombres, las opciones y los tipos de campos deben corresponder a las definiciones reales de la base.

Usa listas desplegables para variables categóricas, controles booleanos para variables binarias y campos numéricos con validaciones para variables cuantitativas.

No solicites meses_abierto en el formulario. Esta variable se utiliza exclusivamente para construir la etiqueta durante el entrenamiento y no debe formar parte de la entrada del modelo.

No solicites al usuario nivel_riesgo, porque es el resultado que debe predecir el sistema.

#### Resultado de la predicción

Después de completar el formulario, muestra:

- Categoría predicha: Alto, Medio o Bajo.
- Una explicación breve de la categoría.
- Una visualización clara del resultado.
- Una nota visible sobre el alcance de la predicción.
- Una opción para modificar los datos y realizar otra predicción.

La aplicación debe indicar que el resultado es una clasificación basada en las características ingresadas y en una etiqueta definida a partir de la antigüedad del negocio. No debe afirmar que el sistema calcula directamente la probabilidad de cierre en los próximos tres años.

Si se muestra un porcentaje de confianza, explica correctamente su significado y verifica que provenga de una salida válida del modelo. No lo denomines probabilidad real de cierre.

#### Arquitectura

El HTML no debe contener una copia manual de las reglas de clasificación del modelo.

La predicción debe realizarse con el modelo entrenado y guardado, incluyendo su pipeline de preprocesamiento.

Elige una arquitectura que permita que el formulario se comunique con el modelo, por ejemplo, una interfaz HTML/CSS/JavaScript conectada a una API en Python con FastAPI o Flask.

No intentes ejecutar directamente un modelo de scikit-learn desde HTML estático si la arquitectura no lo permite.

La solución debe funcionar de manera reproducible en un equipo local y debe incluir instrucciones para ejecutarla.

Si se requiere un backend, implementa sus endpoints, validaciones y manejo de errores.

### 11. Pruebas de la aplicación

Verifica que:

- El modelo se cargue correctamente.
- El formulario envíe los datos en el formato esperado.
- El backend aplique el mismo preprocesamiento utilizado durante el entrenamiento.
- Las categorías ingresadas coincidan con las aceptadas por el modelo.
- Los campos obligatorios se validen.
- Los valores numéricos inválidos se rechacen con mensajes comprensibles.
- Los valores categóricos desconocidos se manejen de forma segura.
- La aplicación entregue una predicción válida.
- Se pueda realizar más de una predicción sin reiniciar el sistema.
- La aplicación maneje los errores sin exponer información técnica innecesaria al usuario.
- La interfaz funcione en escritorio y en pantallas pequeñas.

Crea pruebas automatizadas para el procesamiento de datos, la predicción y los endpoints de la aplicación.

Incluye al menos dos casos nuevos de prueba, distintos de los registros utilizados durante el entrenamiento, para demostrar que la aplicación funciona correctamente.

No utilices estos casos para ajustar el modelo después de observar sus resultados.

### 12. Organización y calidad del código

Antes de programar, inspecciona la estructura del repositorio y propone una organización adecuada.

Si el proyecto no tiene una estructura definida, utiliza una estructura similar a esta y adáptala a las necesidades reales:

```text
proyecto/
├── data/
│   └── BASE_1_EMICRON_2024_comida_DANE.xlsx
├── notebooks/
│   └── analisis_modelado.ipynb
├── src/
│   ├── data_processing.py
│   ├── train.py
│   ├── evaluate.py
│   └── predict.py
├── models/
│   └── modelo_final.joblib
├── app/
│   ├── main.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/
│       ├── js/
│       └── images/
├── tests/
├── requirements.txt
├── README.md
└── .gitignore
```

La estructura es una propuesta, no una obligación de duplicar archivos o carpetas que ya existan.

Requisitos de calidad:

- Código modular, claro y documentado.
- Funciones con responsabilidades específicas.
- Nombres de variables descriptivos.
- Manejo explícito de errores.
- Semillas aleatorias documentadas.
- Dependencias especificadas.
- Separación entre entrenamiento, evaluación e inferencia.
- Ausencia de rutas absolutas dependientes de un solo equipo.
- Ausencia de secretos o credenciales en el repositorio.
- Guardado del modelo final y de su pipeline.
- Reproducibilidad de los resultados.

Evita generar archivos redundantes, copiar el mismo código en varios lugares o crear complejidad innecesaria.

### 13. Despliegue

El proyecto obtiene un reconocimiento adicional si el modelo queda desplegado y puede utilizarse desde una aplicación accesible.

Por eso:

1. Prepara la aplicación para ejecutarse localmente.
2. Documenta cómo desplegarla en un servicio compatible.
3. Si el entorno y los permisos lo permiten, realiza el despliegue.
4. Verifica la URL y prueba que la aplicación realmente funcione antes de reportar que está publicada.
5. Si no puedes realizar el despliegue desde el entorno disponible, deja los archivos y las instrucciones necesarios para completarlo.

No afirmes que el modelo está desplegado si solo se ha ejecutado localmente.

### 14. Documentación académica y presentación

Prepara material que facilite la explicación del proyecto y su evaluación académica.

Incluye:

- Problema de negocio.
- Objetivo general y objetivos específicos.
- Descripción de la fuente de datos.
- Diccionario resumido de las variables utilizadas.
- Justificación de la variable objetivo.
- Regla de construcción de nivel_riesgo.
- Auditoría de fuga de información.
- Metodología CRISP-DM.
- Análisis exploratorio.
- Preparación de los datos.
- Descripción de los cuatro modelos.
- Estrategia de validación.
- Comparación de resultados.
- Justificación del modelo final.
- Interpretabilidad.
- Arquitectura de la aplicación.
- Pruebas realizadas.
- Limitaciones.
- Conclusiones y recomendaciones.

La presentación debe poder explicarse en aproximadamente 10 minutos, con tiempo adicional para preguntas.

Propón una estructura de diapositivas que priorice los resultados, las decisiones metodológicas y la demostración de la aplicación. Evita llenar las diapositivas de código.

Prepara respuestas breves para preguntas técnicas previsibles, especialmente sobre:

- Por qué se seleccionó esa variable objetivo.
- Cómo se definieron los niveles de riesgo.
- Cómo se evitó la fuga de información.
- Por qué se compararon esos cuatro modelos.
- Cómo se eligió el mejor modelo.
- Qué significan las métricas.
- Cuáles son las limitaciones de los datos.
- Qué significa realmente la predicción.
- Qué información adicional sería necesaria para predecir cierres reales en el futuro.

### 15. Transparencia en el uso de inteligencia artificial

El proyecto debe mantener transparencia sobre el uso de herramientas de inteligencia artificial.

Ayúdame a documentar:

- Qué herramienta de IA se utilizó.
- Para qué tareas se utilizó.
- Qué instrucciones o prompts se proporcionaron.
- Qué resultados generados se aceptaron.
- Qué resultados se rechazaron o modificaron.
- Qué verificaciones se realizaron sobre el código y las decisiones metodológicas.
- Qué fuentes externas se consultaron.

No inventes referencias bibliográficas ni atribuyas fuentes que no se hayan consultado. Usa citas verificables para las fuentes metodológicas y documentales que realmente se utilicen.

La solución debe ser comprensible para mí: necesito poder explicar y defender las decisiones del proyecto sin depender de respuestas memorizadas.

### 16. Forma de trabajo solicitada a Claude Code

Trabaja de manera ordenada, verificable e incremental.

#### Fase 1. Inspección

Antes de realizar cambios:

1. Inspecciona el repositorio.
2. Identifica los archivos existentes.
3. Localiza la base de datos.
4. Verifica las columnas, hojas y tipos de datos.
5. Revisa el diccionario.
6. Presenta un resumen de los hallazgos y los posibles problemas metodológicos.

#### Fase 2. Plan

Propón un plan de implementación dividido en etapas. Identifica las decisiones que necesitan justificación y las dependencias del proyecto.

No inventes información para completar los vacíos.

#### Fase 3. Preparación y análisis

Implementa la limpieza, el análisis exploratorio y la construcción de nivel_riesgo.

Antes de continuar, verifica la distribución de las clases y deja documentada la regla utilizada para generarlas.

#### Fase 4. Modelado

Implementa el entrenamiento, la validación cruzada, la comparación de los cuatro modelos y la evaluación final.

Comprueba explícitamente que meses_abierto y nivel_riesgo no estén presentes en las variables predictoras.

#### Fase 5. Aplicación

Implementa la interfaz web, la API y la integración con el modelo final.

Verifica que el formulario utilice exactamente las variables aprobadas en la auditoría de fuga de información.

#### Fase 6. Pruebas y documentación

Ejecuta las pruebas disponibles, corrige los errores y documenta los pasos para instalar, entrenar, evaluar y ejecutar la aplicación.

#### Fase 7. Revisión final

Entrega un resumen de:

- Archivos creados y modificados.
- Decisiones metodológicas.
- Variables utilizadas y excluidas.
- Regla de construcción de nivel_riesgo.
- Resultados reales de los cuatro modelos.
- Modelo seleccionado y justificación.
- Pruebas ejecutadas y su resultado.
- Instrucciones para ejecutar la aplicación.
- Estado real del despliegue.
- Limitaciones pendientes.

No te limites a sugerir código: cuando tengas acceso al repositorio y al entorno, implementa los cambios, ejecútalos y verifica los resultados.

Si encuentras un problema, identifica su causa, propón una solución y comprueba que la solución funciona.

No marques una tarea como completada sin haber verificado su resultado.

### 17. Criterios de aceptación

El proyecto se considerará listo cuando:

1. La base de datos haya sido inspeccionada y documentada.
2. nivel_riesgo se construya de forma reproducible a partir de meses_abierto.
3. meses_abierto no se utilice como predictor.
4. No se utilicen variables que filtren directa o indirectamente la etiqueta.
5. Se hayan entrenado y comparado los cuatro modelos solicitados.
6. Las métricas se hayan calculado sobre datos de prueba que no se utilizaron para ajustar los modelos.
7. El modelo final y su preprocesamiento se hayan guardado correctamente.
8. La aplicación web permita ingresar datos y obtener una predicción real del modelo.
9. Se hayan probado al menos dos casos nuevos.
10. Existan instrucciones claras de instalación y ejecución.
11. La documentación explique los resultados y las limitaciones.
12. No se afirme que se predicen cierres reales futuros sin datos que permitan validar ese objetivo.

**Prioridad metodológica:** es preferible entregar un modelo correctamente construido, reproducible y con limitaciones explícitas que presentar métricas artificialmente altas por una fuga de información o por una interpretación incorrecta de la variable objetivo.

### 18. Revisión y ajuste incoherente del modelo sobre el informe final

Como estoy cursando una Especialización en Machine Learning y una Maestría en Ciencia de Datos, mi objetivo con este proyecto no es únicamente obtener un modelo funcional o entregar un informe final bien redactado. Necesito comprender en profundidad las decisiones técnicas y metodológicas tomadas durante el desarrollo del proyecto, interpretar correctamente los resultados y adquirir los conocimientos necesarios para justificar y defender cada decisión ante una sustentación académica.

La construcción del código se realizó con ayuda de Claude Code. Por lo tanto, no quiero limitarme a aceptar lo que el código hace o lo que indican sus resultados. Necesito entender cómo funciona, por qué se implementaron determinadas soluciones, qué alternativas existían y si las decisiones tomadas son metodológicamente correctas.

Mi responsabilidad principal en el informe final corresponde a las siguientes secciones:

- Sesión 3. Preparación y diseño experimental.
- Sesión 4. Modelado.
- Sesión 5. Evaluación.

Tu función será acompañarme durante todo este proceso como tutor técnico, revisor crítico y asesor de redacción académica, ayudándome a comprender, verificar, documentar y comunicar rigurosamente el trabajo realizado.

#### Comprensión técnica y metodológica del proyecto

Te haré preguntas sobre el código, los datos, las decisiones metodológicas, los experimentos, las métricas y los resultados. Algunas preguntas iniciales pueden ser:

- ¿Cómo se evitó la fuga de información (data leakage) durante la preparación de los datos, el entrenamiento y la evaluación?
- ¿Cómo se identificó y trató el desbalance de clases? ¿Qué técnicas se utilizaron y por qué?
- ¿Cómo se separaron los conjuntos de entrenamiento, validación y prueba? ¿Se respetó el propósito de cada uno?
- ¿Se utilizó correctamente el conjunto de prueba, evitando emplearlo para seleccionar modelos, ajustar hiperparámetros o tomar decisiones durante el desarrollo?
- ¿Contra qué línea base (baseline) se compararon los modelos? ¿Qué modelos se evaluaron y bajo qué condiciones experimentales?
- ¿Cómo se realizó la validación cruzada y qué conclusiones pueden extraerse de sus resultados?
- ¿Cómo se seleccionó el modelo final? ¿La elección está respaldada por evidencia experimental y criterios previamente definidos?
- ¿Qué métricas son más relevantes para el problema y cómo se relacionan con el costo de los falsos positivos y los falsos negativos?
- ¿Qué tan estables son los resultados entre los distintos pliegues o experimentos? ¿Cómo debe interpretarse su variabilidad?
- ¿Cómo se seleccionó o debería seleccionarse el umbral de decisión? ¿Qué implicaciones tiene para las métricas y las decisiones del negocio?
- ¿Qué limitaciones tiene el modelo y qué conclusiones pueden sostenerse realmente a partir de los resultados obtenidos?

Estas preguntas son ejemplos, no una lista exhaustiva. Te haré todas las preguntas adicionales que considere necesarias para comprender el proyecto y prepararme para defenderlo académicamente.

#### Cómo debes responder mis preguntas

Para cada pregunta técnica, procura seguir esta estructura cuando sea pertinente:

1. Respuesta directa: explica primero la idea principal con claridad.
2. Fundamento conceptual: desarrolla los conceptos de Machine Learning y estadística necesarios para entender la decisión.
3. Aplicación en mi proyecto: explica qué se hizo concretamente, cómo se implementó y dónde se encuentra en el código o en los resultados.
4. Justificación metodológica: explica por qué se tomó esa decisión, qué alternativas existían y cuáles son sus ventajas, desventajas y supuestos.
5. Interpretación de resultados: relaciona la decisión con los resultados experimentales y sus implicaciones prácticas.
6. Riesgos y limitaciones: identifica posibles errores, sesgos, debilidades metodológicas o aspectos que todavía deban verificarse.
7. Posible pregunta de sustentación: cuando aporte valor, plantea una pregunta que podría hacer un evaluador y explica cómo construir una respuesta técnicamente fundamentada.

No es necesario utilizar siempre los siete apartados. Prioriza la claridad, la profundidad y la pertinencia de cada respuesta, evitando explicaciones repetitivas o estructuras innecesariamente extensas.

Adapta las explicaciones a mi formación en Machine Learning y Ciencia de Datos. No simplifiques en exceso los conceptos, pero tampoco asumas que ya comprendo todas las decisiones específicas implementadas en el proyecto. Si utilizas términos técnicos, fórmulas o conceptos estadísticos, explica su significado y su aplicación práctica.

#### erificación del código y de la evidencia

Es fundamental que distingas entre lo que debería hacerse metodológicamente, lo que efectivamente implementa el código y lo que puede demostrarse mediante los resultados disponibles.

Cuando te pregunte cómo se realizó un procedimiento, no asumas que se implementó correctamente solo porque el código se ejecutó sin errores.

Debes:

- Revisar el código relevante antes de afirmar cómo funciona el procedimiento.
- Identificar las funciones, variables, transformaciones y etapas que sustentan tu explicación.
- Contrastar, cuando sea posible, la implementación con los resultados, registros experimentales y archivos disponibles.
- Diferenciar claramente entre hechos comprobados, interpretaciones razonables, hipótesis y aspectos pendientes de verificar.
- Señalar inconsistencias entre el código, los resultados, las decisiones metodológicas y la documentación.
- Explicar las consecuencias de los posibles errores y proponer cómo comprobarlos o corregirlos.
- No inventar resultados, métricas, procedimientos, experimentos, referencias bibliográficas ni justificaciones que no estén respaldados por la evidencia disponible.

Si no tienes suficiente información para responder con certeza, indícame exactamente qué código, archivo, resultado o evidencia necesitas revisar. Si es posible, ofrece una explicación provisional, identificando explícitamente sus supuestos y limitaciones.

Cuando corresponda, contrasta las decisiones con buenas prácticas de Machine Learning, estadística y diseño experimental. Si utilizas fuentes académicas o técnicas externas para justificar una afirmación, cita referencias verificables y distingue entre recomendaciones generales y decisiones específicas de mi proyecto.

#### Elaboración de las secciones del informe final

Una vez que haya comprendido las decisiones técnicas mediante nuestras conversaciones, redactaré las secciones 3, 4 y 5 del informe final.

Mi intención es escribirlas a partir de lo aprendido, no delegarte la elaboración completa del informe sin comprender su contenido.

Cuando te comparta un borrador, deberás revisarlo de manera integral en los siguientes aspectos:

#### A. Exactitud técnica y metodológica

- Verifica que cada afirmación corresponda con lo que realmente se hizo en el proyecto.
- Comprueba que la descripción de los experimentos, modelos, métricas, validaciones y resultados sea correcta.
- Identifica afirmaciones que no estén respaldadas por el código o la evidencia disponible.
- Detecta contradicciones, omisiones importantes, interpretaciones estadísticas incorrectas y conclusiones que excedan los resultados obtenidos.
- Comprueba que las razones expuestas para seleccionar un modelo o una métrica sean coherentes con los criterios experimentales y el problema de negocio.
- Señala cuándo una afirmación requiere evidencia adicional, una referencia o una explicación más precisa.

#### B. Coherencia entre las secciones

Verifica que exista continuidad lógica entre la preparación de los datos y el diseño experimental (sesión 3), el entrenamiento y la selección de modelos (sesión 4), y la evaluación e interpretación de los resultados (sesión 5).

Asegúrate de que no existan contradicciones entre las secciones ni diferencias injustificadas entre lo que se describe en la metodología, lo que muestra el código y lo que se concluye a partir de los resultados.

#### C. Redacción académica y presentación profesional

Revisa:

- Ortografía, gramática, puntuación y sintaxis.
- Claridad, precisión y fluidez de las explicaciones.
- Uso correcto de la terminología técnica y estadística.
- Estructura de los párrafos y conexión entre las ideas.
- Eliminación de repeticiones, ambigüedades, expresiones informales y afirmaciones innecesariamente complejas.
- Consistencia en los nombres de los modelos, las métricas, las variables, los conjuntos de datos y los procedimientos.
- Uso adecuado de tablas, figuras, títulos, subtítulos y referencias cuando corresponda.

La redacción debe ser formal, técnica y académica, pero natural y comprensible. Evita el lenguaje excesivamente rebuscado, las afirmaciones grandilocuentes y las explicaciones que parezcan correctas sin aportar información concreta.

#### Forma de revisar mis borradores

Cuando te entregue un fragmento del informe, sigue este procedimiento:

1. Diagnóstico: identifica los aciertos, errores, imprecisiones y aspectos que necesitan mayor desarrollo.
2. Justificación de las correcciones: explícame por qué una afirmación es incorrecta, ambigua, incompleta o metodológicamente cuestionable.
3. Versión corregida: presenta una propuesta de redacción que conserve mi intención original, mejore la calidad académica y respete lo que realmente se hizo.
4. Verificaciones pendientes: enumera las afirmaciones que no pueden confirmarse todavía y especifica qué evidencia se necesita para validarlas.

No cambies automáticamente una afirmación dudosa por otra que parezca más técnica. Primero explica el problema y verifica qué ocurrió realmente.

Cuando una modificación afecte una decisión metodológica importante, no te limites a corregir la redacción: explícame el cambio conceptual y sus implicaciones. Si existen varias interpretaciones posibles, preséntalas y ayúdame a determinar cuál está respaldada por la evidencia.

Si el fragmento está bien escrito y es técnicamente correcto, indícalo. No realices cambios innecesarios solo para reformular el texto.

#### Aprendizaje colaborativo y toma de decisiones

Quiero que este proceso sea colaborativo e iterativo. Mi objetivo es aprender, cuestionar y validar cada decisión, no aceptar automáticamente tus recomendaciones.

Por lo tanto:

- No des por hecho que tu primera interpretación es correcta.
- No asumas que las decisiones implementadas en el código son necesariamente las mejores.
- Si detectas una inconsistencia, explícala con argumentos técnicos y evidencia.
- Si te planteo una objeción o considero que una recomendación no es coherente, analiza mi argumento de manera crítica y revisa la evidencia antes de mantener o modificar tu posición.
- Si mi interpretación es correcta, reconócelo y ajusta tu explicación.
- Si mi interpretación es incorrecta, explícame por qué, sin limitarte a contradecirme.
- Cuando existan varias alternativas válidas, compara sus ventajas, desventajas, supuestos e implicaciones para nuestro problema.
- Distingue entre errores que deben corregirse, mejoras recomendables y decisiones metodológicas que pueden defenderse razonablemente.
- No implementes cambios en el código ni des por aprobada una modificación metodológica sin explicarme su propósito, impacto y justificación. Cuando una modificación sea importante, espera mi confirmación antes de tratarla como decisión definitiva.

Quiero mantener el control sobre las decisiones del proyecto y participar activamente en la revisión de cada propuesta.

#### Principios que debes respetar durante todo el proceso

1. Rigor antes que apariencia: es preferible reconocer una limitación o un error que presentar una explicación convincente pero incorrecta.
2. Evidencia antes que suposiciones: toda afirmación sobre lo realizado en el proyecto debe sustentarse en el código, los resultados, los archivos o la documentación disponible.
3. Comprensión antes que redacción: primero debemos entender y validar las decisiones técnicas; después, documentarlas.
4. Precisión antes que complejidad: utiliza el nivel técnico necesario para explicar cada decisión, sin añadir complejidad innecesaria.
5. Trazabilidad: cuando sea posible, relaciona cada conclusión con el procedimiento, el resultado o la evidencia que la respalda.
6. Transparencia sobre la incertidumbre: indica expresamente qué está comprobado, qué es una interpretación y qué falta por verificar.
7. Coherencia académica: las conclusiones deben ser proporcionales a la evidencia y reconocer las limitaciones del diseño experimental.
8. Autonomía del estudiante: ayúdame a desarrollar criterio técnico para que pueda explicar y defender personalmente el proyecto, en lugar de memorizar respuestas o aceptar recomendaciones sin comprenderlas.

#### Dinámica de trabajo

Trabajaremos por etapas, de acuerdo con las preguntas que vaya formulando y los materiales que te comparta.

Primero profundizaremos en los conceptos, las decisiones metodológicas y la implementación del proyecto. Después, utilizaré lo aprendido para redactar las secciones correspondientes del informe. Finalmente, revisaremos los borradores, contrastaremos sus afirmaciones con la evidencia y realizaremos las correcciones necesarias.

No es necesario que intentes resolver todas las cuestiones desde el principio ni que redactes anticipadamente las secciones que todavía no hemos trabajado. Responde a cada consulta con el nivel de profundidad que requiera y conserva la coherencia con las decisiones que hayamos verificado previamente.

Si una pregunta posterior pone en duda una conclusión anterior, vuelve a examinarla en lugar de asumir que sigue siendo correcta.

**Objetivo final:** Comprender a profundidad el proyecto de Machine Learning, justificar técnicamente sus decisiones, evaluar críticamente sus resultados y entregar un informe académico profesional, coherente, verificable y fiel a lo que realmente se implementó, de manera que pueda sustentar su contenido con conocimiento propio y argumentos sólidos.
