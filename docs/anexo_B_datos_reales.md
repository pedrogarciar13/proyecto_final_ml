# Anexo B · Datos reales

El proyecto usa datos reales y observados, no simulados ni generados con inteligencia artificial.

## 1. Procedencia

| | Base principal | Base de contexto |
|---|---|---|
| Qué es | Encuesta de Micronegocios (EMICRON) 2024 | Registro mercantil (RUES), establecimientos |
| Quién la produce | DANE, encuesta oficial del sistema estadístico nacional | Confecámaras, a partir de las matrículas de las Cámaras de Comercio |
| Dónde | https://microdatos.dane.gov.co/index.php/catalog/875 | https://www.datos.gov.co/d/nb3d-v3n7 |
| Licencia o condiciones | Microdatos anonimizados de acceso público, uso con citación de la fuente según los términos del ANDA del DANE | CC BY-SA 4.0 |
| Fecha de acceso | 15 de octubre de 2026 | 13 de octubre de 2026 |
| Filas usadas | 7.523 (más de las 1.000 que exige el bono) | 106.859 |

## 2. Cómo se obtuvo

1. En el ANDA del DANE se descargaron los módulos de EMICRON 2024 en formato CSV (archivos `BDATOS-EMICRON-Modulo_...-2024.zip`).
2. Se unieron por DIRECTORIO + SECUENCIA_P + SECUENCIA_ENCUESTA.
3. Se filtró GRUPOS12 = 07 (alojamiento y servicios de comida).
4. Se tradujeron 16 columnas a español con el diccionario oficial del DANE.

Los archivos crudos van en `datos_crudos/` (ver su LEEME).

## 3. Suciedad real encontrada

Ver la sección 2 del informe y la ficha de datos:
- colas largas en meses abierto y ganancia;
- "No aplica" como vacío estructural;
- categorías con muy pocos casos;
- 19 filas con respuestas idénticas;
- ganancia declarada por el dueño, no verificada.

## 4. Tratamiento ético y protección de datos

- **Anonimización:** los microdatos del DANE no traen nombres, documentos, teléfonos ni direcciones. El DANE los publica bajo reserva estadística (Ley 79 de 1993), que impide identificar a quien respondió. En el RUES se eliminaron nombres, cédulas y NIT antes de trabajar.
- **Normativa:** Ley 1581 de 2012 de protección de datos personales. El proyecto no cruza las bases para identificar personas.
- **Variables excluidas por ética:** el sexo del propietario no se usa.
- **Variable sensible que sí se usa:** la edad del propietario. Se declara como riesgo de discriminación por edad en la sección 6, con la medida de que el resultado solo cambia el mensaje comercial, nunca la oferta ni el precio.
- **En LUMO:** el termómetro no guarda datos que identifiquen al negocio para hacer la clasificación.
