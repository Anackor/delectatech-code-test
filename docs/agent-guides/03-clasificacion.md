# Bloque 3 — Clasificación de platos

Leer primero la [guía común](00-arquitectura-y-practicas.md).

## Contrato y diseño

Procesar los platos de restaurantes con matching aceptado. La fuente de categorías es `food_categories.xlsx`, aunque una sección del enunciado diga JSON. Una clasificación resuelta referencia un `uidentifier` del XLSX; `name`, `parent` y `family` se obtienen de esa misma fila.

Separar lectura de taxonomía y menús, clasificación pura y persistencia. La función de clasificación recibe texto y contexto, devuelve categoría o estado de revisión, y explica la regla que decidió el resultado. La clasificación no modifica la taxonomía.

## Pasos

1. Validar IDs únicos, columnas y valores del XLSX; interpretar explícitamente `is_generic_or_other`, incluida su posible representación como texto. No convertir la cadena `false` mediante `bool()`.
2. Definir la clave de una aparición de plato tras inspeccionar IDs repetidos en menús/secciones. Conservar IDs del proveedor y evitar que una importación multiplique platos por el join con decisiones de matching.
3. Diseñar reglas con prioridades explícitas sobre nombre, descripción y sección, contemplando español, catalán o inglés según los datos observados. Usar límites de palabra y resolver solapamientos: una mención a un ingrediente en la descripción no debe dominar automáticamente al nombre del plato.
4. Implementar alias de categorías como datos y similitud léxica cuando aporte evidencia. Probar platos compuestos y bebidas; derivar familia y padre desde la categoría elegida, nunca mediante decisiones independientes incompatibles.
5. Definir el fallback con categorías genéricas realmente presentes y pertinentes. Si no existe evidencia suficiente, conservar estado de revisión y el motivo en vez de inventar una categoría. El enunciado busca una categoría por plato: informar de pendientes y resolverlos o declararlos como limitación antes de dar la tarea por completa.
6. Guardar resultado, regla/versión y procedencia; implementar `make classify` y exportar una muestra unida con restaurante de ambas fuentes y plato. Una nueva ejecución debe actualizar reglas y excluir resultados de enlaces que hayan dejado de estar aceptados.
7. Evaluar una muestra manual distribuida entre familias/categorías y casos difíciles. Publicar aciertos sobre esa muestra, cobertura y tasa de genéricos/revisión, indicando qué ejemplos se usaron para ajustar reglas.

## Comprobaciones y cierre

- Texto vacío, alias con acentos, reglas solapadas, bebidas, platos compuestos y categoría inexistente.
- Coherencia completa de `uidentifier`, `name`, `parent` y `family` frente al XLSX.
- Repetición sin duplicados y tratamiento de un plato o matching que cambia de estado.
- Exportación interpretable, reglas explicadas y pendientes cuantificados. Guardar la muestra de entrega fuera del directorio ignorado `output/` cuando se prepare el repositorio final.
