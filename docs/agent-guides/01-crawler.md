# Bloque 1 — Crawler de Just Eat

Leer primero la [guía común](00-arquitectura-y-practicas.md).

## Contrato y diseño

Entrada: una URL de restaurante de Just Eat. Salida: un JSON con la estructura real de `source/just_eat_venue_example.json`; el archivo entregado usa `venue` en singular. Conservar menús, secciones, platos, descripciones, precios y demás campos del ejemplo según su disponibilidad. El formato de salida no debe depender del método de extracción.

Separar tres operaciones: obtener los datos de la página, transformarlos al contrato y escribir el resultado. La transformación se prueba con datos guardados y no necesita Playwright. El comando compone estas operaciones; el navegador pertenece al adaptador de obtención.

## Pasos

1. Inspeccionar el ejemplo completo, incluidos `menus`, `sections`, `items` y `subSelections`; anotar tipos, campos opcionales y datos que no están disponibles directamente en la página. No inventar IDs del proveedor.
2. Inspeccionar una URL real y determinar dónde están los datos completos: estado estructurado, respuestas que usa la página o contenido renderizado. Guardar una fixture pequeña y representativa del formato observado.
3. Añadir Playwright y Chromium a la imagen `app`, manteniendo sus versiones compatibles. Consultar su documentación oficial y la skill de Playwright cuando corresponda al escribir pruebas de navegador. Cerrar recursos y fijar timeouts.
4. Validar esquema HTTP(S) y hostname de Just Eat en la entrada, y revisar el destino tras redirecciones. Extraer todas las secciones y variantes necesarias, incluyendo contenido que se cargue de forma diferida; no asumir que el primer bloque de JSON contiene el menú entero.
5. Implementar la transformación pura y validar el resultado antes de publicarlo. Los metadatos propios, errores y fecha de captura deben ir en un informe separado si añadirlos alteraría el contrato del ejemplo.
6. Implementar `make crawl URL=...`, pasando la URL como un argumento sin ejecutarla como código de shell. Escribir en `output/` y evitar reemplazar una salida válida por una captura incompleta.
7. Documentar URL probada, fecha, origen de los datos y forma de comprobar la integridad del menú. Si el sitio bloquea el acceso, registrar la evidencia; una fixture no demuestra que el crawl en vivo haya funcionado.

## Comprobaciones y cierre

- Fixture con varias secciones, un plato sin descripción y variantes/precios: comparar estructura y contenido esperados.
- Respuesta inválida o menú incompleto: error reconocible y ausencia de un archivo presentado como completo.
- Prueba en vivo de una URL accesible y una URL fallida, fuera de la suite habitual.
- Comando documentado, salida de muestra e independencia del pipeline que usa los JSON ya entregados.

Un bloqueo externo no impide avanzar al bloque 2, pero deja pendiente la verificación en vivo del crawler. No registrar la tarea como totalmente validada por haber adaptado el JSON de ejemplo.
