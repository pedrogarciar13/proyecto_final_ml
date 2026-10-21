# Anexo A · Enfoque de emprendimiento: LUMO

Enfoque declarado desde el anteproyecto (reto R10, 8 de octubre de 2026): **emprendimiento**, aplicado a LUMO, el SaaS que construye Santiago Simanca. Se sostuvo hasta la entrega; lo que cambió en el camino fue la base de datos (de RUES a EMICRON) y la variable objetivo, no el enfoque.

## 1. Propuesta de valor

LUMO es un software para restaurantes y negocios de comida: "Pregúntale a tu negocio". El dueño carga sus ventas y gastos y conversa con sus datos en español, sin saber de contabilidad ni de tableros.

El termómetro le añade a LUMO una **herramienta interna de prospección**: desde la consola de administración, LUMO clasifica a un negocio en etapa temprana, de consolidación o establecida y le envía el mensaje que corresponde a esa etapa, en lugar de un mensaje igual para todos.

## 2. Usuario y cliente

- **Usuario del termómetro:** el administrador de LUMO (hoy, su fundador), que decide a quién contactar y qué decirle.
- **Cliente final de LUMO:** dueños de micronegocios de comida en Colombia. Según EMICRON 2024, el 64,7 % no lleva cuentas, el 87,2 % no está en Cámara de Comercio y el 48,7 % funciona desde su vivienda. Es un segmento grande, poco atendido por el software contable tradicional y que necesita orden más que funciones avanzadas.

## 3. Hipótesis de negocio

> Si LUMO le envía a cada negocio un mensaje adaptado a su etapa (temprana, consolidación o establecida), según el termómetro, entonces la tasa de respuesta al primer contacto será al menos el **doble** que la de un mensaje genérico.

Hipótesis secundaria: los negocios en etapa temprana ("Alto") son los que más se registran, porque todavía no tienen un sistema y su mayor riesgo de cierre (11,4 % de los restaurantes registrados cierra antes del primer año, RUES) hace más urgente el orden financiero.

## 4. Estimación del impacto (con supuestos declarados)

| Dato o supuesto | Valor | Tipo |
|---|---|---|
| Restaurantes matriculados en Colombia en 2024 | 16.523 | Dato (RUES) |
| Proporción en etapa temprana según la encuesta | 16,3 % | Dato (EMICRON 2024, muestra sin ponderar) |
| Prospectos contactados en el piloto | 500 | Supuesto |
| Tasa de respuesta con mensaje genérico | 3 % | Supuesto, por validar |
| Tasa de respuesta con mensaje por etapa | 6 % | Hipótesis (el doble) |
| Conversión de respuesta a registro | 25 % | Supuesto, por validar |
| Precio mensual del plan de pago | USD 50 | Dato interno de LUMO |

Con esos supuestos, de 500 contactos: el mensaje genérico genera 15 respuestas y unos 4 registros; el mensaje por etapa genera 30 respuestas y unos 8 registros. Es decir, **unos 4 clientes adicionales por cada 500 contactos**, con el mismo esfuerzo comercial: unos **USD 200 más de ingreso mensual recurrente** (4 × USD 50), o USD 2.400 al año si se quedan doce meses. Si alguno de los supuestos cambia, la cuenta se rehace con la misma fórmula: contactos × tasa de respuesta × conversión.

Estos números no son resultados: son la meta contra la que se medirá el piloto.

## 5. Ruta para validar la hipótesis

1. **Semana 1:** integrar el termómetro en la consola de administración de LUMO (prevista para esta entrega).
2. **Semanas 2 a 5:** piloto con 500 negocios de comida de Bogotá y Chía, reunidos de directorios públicos y redes sociales. Mitad con mensaje por etapa y mitad con mensaje genérico, asignados al azar.
3. **Medir:** tasa de respuesta y de registro por grupo y por etapa.
4. **Decidir:** si el mensaje por etapa no supera al genérico, se retira el termómetro y se prueba otra segmentación.
5. **Con los registros reales:** comparar la etapa estimada con la fecha real de apertura que declare cada negocio, para medir el error del modelo fuera de la encuesta.
