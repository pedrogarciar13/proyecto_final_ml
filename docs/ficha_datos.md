# Ficha de datos · PFI LUMO

## 1. Base principal: EMICRON 2024, negocios de comida

| Campo | Valor |
|---|---|
| Nombre | Encuesta de Micronegocios (EMICRON) 2024 |
| Productor | Departamento Administrativo Nacional de Estadística (DANE) |
| Portal | Archivo Nacional de Datos (ANDA) del DANE, catálogo 875: https://microdatos.dane.gov.co/index.php/catalog/875 |
| Licencia o condiciones | Microdatos anonimizados de acceso público del DANE, de uso libre con citación de la fuente según los términos de uso del ANDA |
| Fecha de acceso | 15 de octubre de 2026 |
| Módulos usados (8) | Identificación; Características del micronegocio; Sitio o ubicación; Personal ocupado (propietario); Ventas e ingresos; Costos, gastos y activos; TIC; Inclusión financiera. Unidos por DIRECTORIO + SECUENCIA_P + SECUENCIA_ENCUESTA |
| Filtro | Grupo de actividad "Alojamiento y servicios de comida" (GRUPOS12 = 07) |
| Filas | 7.523 negocios |
| Columnas | 218 en el archivo técnico unido (`emicron_2024_comida_alojamiento.csv`); 16 en la versión de trabajo traducida (`BASE_1_EMICRON_2024_comida_DANE.xlsx`, hoja Datos) |
| Unidad de análisis | Un micronegocio (hasta 9 personas ocupadas) y su propietario |
| Datos personales | No contiene nombres, documentos ni direcciones. Se excluyó el sexo del propietario por razones éticas |

### Columnas de trabajo (16)

| Columna | Tipo | Código DANE | Faltantes | Valores | Uso en el modelo |
|---|---|---|---|---|---|
| id_negocio | Entero | — (creado por el equipo) | 0 | 1 a 7.523 | Excluida: identificador |
| donde_funciona | Categórica (8) | P3053 | 0 | Vivienda 48,7 %, ambulante 30,4 %, local 16,0 %, domicilio 4,1 %, finca, vehículo, obra, otro | Predictora |
| como_lleva_cuentas | Categórica ordinal (5) | P640 | 0 | No lleva 64,7 %, cuaderno/Excel/caja 30,1 %, libro diario 3,9 %, balance o PyG 1,0 %, informes contables | Predictora |
| tiene_ayudantes | Binaria | P3031 | 0 | No 68,0 % / Sí 32,0 % | Predictora |
| meses_abierto | Entera | P3034 | 0 | 1 a 500; mediana 48 | **Solo para construir el objetivo**; excluida de las predictoras |
| acepta_transferencias | Binaria | P1764_3 | 0 | No 69,8 % / Sí 30,2 % | Predictora |
| tiene_nombre_comercial | Binaria | P3035 | 0 | No 79,1 % / Sí 20,9 % | Predictora |
| registrado_camara_comercio | Binaria | P1055 | 0 | No 87,2 % / Sí 12,8 % | Predictora |
| tiene_RUT | Binaria | P1633 | 0 | No 81,7 % / Sí 18,3 % | Predictora |
| visible_desde_la_calle | Categórica (3) | P469 | 0 | Sí 62,8 %, No 20,6 %, No aplica 16,6 % | Predictora |
| usa_internet | Binaria | P2524 | 0 | No 58,6 % / Sí 41,4 % | Predictora |
| tiene_redes_sociales | Binaria | P1559 | 0 | No 87,8 % / Sí 12,2 % | Predictora |
| zona | Binaria | CLASE_TE | 0 | Cabecera 89,3 % / Rural 10,7 % | Predictora |
| edad_propietario | Entera | P241 | 0 | 18 a 91; mediana 49 | Predictora (riesgo ético declarado en la sección 6) |
| le_deja_al_mes_COP | Entera (pesos) | P3072 | 0 | 0 a 43.093.000; mediana 600.000 | Predictora |
| riesgo_financiero | Binaria (calculada) | Derivada de P3072 | 0 | Sí 51,1 % / No 48,9 % | Excluida: se deriva de le_deja_al_mes_COP y no es el objetivo de este proyecto |

### Variable objetivo (construida por el equipo)

`nivel_riesgo`, a partir de `meses_abierto`: **Alto** de 1 a 11 meses (16,3 %), **Medio** de 12 a 42 meses (29,2 %), **Bajo** de 43 meses o más (54,5 %). Es una decisión metodológica del proyecto, no una clasificación oficial del DANE.

### Calidad

- Sin faltantes explícitos en las 16 columnas. "No aplica" en `visible_desde_la_calle` funciona como vacío estructural.
- 19 filas con respuestas idénticas en las 15 columnas de contenido; se conservan (son encuestas distintas).
- `meses_abierto` y `le_deja_al_mes_COP` tienen colas largas a la derecha.
- Categorías con muy pocos casos en `donde_funciona` (obra, vehículo, otro).

### Cita APA 7

Departamento Administrativo Nacional de Estadística [DANE]. (2025). *Encuesta de Micronegocios (EMICRON) 2024* [Conjunto de datos]. Archivo Nacional de Datos. https://microdatos.dane.gov.co/index.php/catalog/875

## 2. Base de contexto: RUES, restaurantes 2015–2022

| Campo | Valor |
|---|---|
| Nombre | Registro Único Empresarial y Social (RUES): Establecimientos, agencias y sucursales |
| Productor | Confecámaras |
| Portal | Datos Abiertos Colombia, conjunto nb3d-v3n7: https://www.datos.gov.co/d/nb3d-v3n7 |
| Licencia | Creative Commons Atribución-CompartirIgual 4.0 (CC BY-SA 4.0) |
| Fecha de acceso | 13 de octubre de 2026 |
| Filtro | CIIU 5611 (restaurantes), matriculados entre 2015 y 2022 |
| Filas | 106.859 establecimientos |
| Columnas | 10 en la versión de trabajo (`BASE_2_RUES_restaurantes_contexto.xlsx`) |
| Uso | Solo contexto: el 26,6 % cerró antes de 3 años y el 11,4 % antes del primer año. No se usa para entrenar |
| Datos personales | Se eliminaron nombres, cédulas y NIT (Ley 1581 de 2012) |

### Cita APA 7

Confecámaras. (2026). *Establecimientos – Agencias – Sucursales (RUES)* [Conjunto de datos]. Datos Abiertos Colombia. https://www.datos.gov.co/d/nb3d-v3n7
