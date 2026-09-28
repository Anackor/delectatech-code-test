# Bloque 2 — Matching de restaurantes

Leer primero la [guía común](00-arquitectura-y-practicas.md).

## Contrato y diseño

Entradas: el diccionario `just_eat_venues.json` y la lista `google_venues.json`. Salida: una decisión por restaurante de Just Eat con estado, candidato elegido si existe, puntuación, evidencias y versión de parámetros. Las reglas de puntuación y decisión no acceden a archivos ni SQL.

Mantener separados normalización, generación de candidatos, puntuación y elección. Una puntuación de similitud no es una probabilidad calibrada. Conservar al menos la evidencia del mejor candidato y del segundo cuando determine la ambigüedad.

## Pasos

1. Perfilar campos y ausencias de ambos archivos con lectura incremental. Confirmar claves de Google y extracción del CID, coordenadas, códigos postales y posibles duplicados.
2. Definir un registro normalizado mínimo con ID, nombre, dirección y coordenadas. Preservar números de calle y sucursales; normalizar acentos y puntuación sin destruir información útil.
3. Generar candidatos con una estrategia geográfica sencilla y un fallback acotado por dirección cuando falten coordenadas. No descartar un local únicamente por carecer de ubicación ni comparar todos los pares sin medir el coste.
4. Calcular distancia y similitud de nombre/dirección con pesos explícitos. Determinar `matched` por umbral y separación suficiente respecto al segundo candidato; usar `ambiguous` para evidencia contradictoria y `unmatched` cuando sea insuficiente.
5. Decidir la cardinalidad a partir de los datos: cada local de Just Eat admite como máximo un enlace aceptado, pero no imponer una correspondencia global uno a uno sin comprobar marcas virtuales, duplicados o varias URLs por local físico. Registrar conflictos y resolver empates de forma determinista.
6. Crear el esquema mínimo en PostgreSQL y guardar entidades, decisiones y evidencia. Elegir una política de repetición que no deje un antiguo enlace activo si ahora el resultado es ambiguo o no enlazado.
7. Implementar `make match`, informe de cobertura y muestra de pares. Revisar y etiquetar manualmente ejemplos de locales homónimos, sucursales, nombres distintos en la misma dirección y datos incompletos; reservar ejemplos para evaluación.

## Comprobaciones y cierre

- Casos de acentos, sucursales próximas, coordenadas ausentes, coordenadas inválidas y empate.
- Un nombre igual a gran distancia no basta para enlazar; una variante de nombre con dirección coherente puede hacerlo.
- Integración: claves y referencias válidas, repetición sin duplicados y sustitución de un resultado obsoleto.
- Informe con denominadores de cobertura, errores/rechazos de entrada y resultados de la muestra manual. No presentar la proporción de locales enlazados como precisión.

El bloque debe ejecutarse a partir del dataset proporcionado aunque el crawler siga pendiente. Conservar datos suficientes para que el dashboard pueda distinguir restaurantes de Just Eat enlazados de locales físicos de Google únicos.
