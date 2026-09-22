# ADR-0001: Pipeline local reproducible para integrar datos de restaurantes

- **Estado:** Aceptado
- **Fecha:** 2026-09-22
- **Ámbito:** `code-test/`

## Contexto

El enunciado pide: (1) extraer un restaurante y su menú completo desde una URL de Just Eat con la estructura del ejemplo; (2) enlazar los restaurantes ya entregados con Google; (3) clasificar los platos de los restaurantes enlazados según la taxonomía; (4) explicar y demostrar en CPU la extracción de platos desde unas pocas imágenes; y (5) mostrar resultados y métricas en un dashboard interactivo. La entrega también requiere instrucciones de ejecución, capturas del dashboard, una muestra de datos unidos y categorizados y un informe del uso de IA.

Los archivos reales contienen 2.696 URLs y restaurantes de Just Eat, 22.991 locales de Google y una taxonomía de 101 categorías. `just_eat_venues.json` ocupa unos 195 MB y `google_venues.json` unos 63 MB. El enunciado llama `food_categories.json` a la taxonomía en la tarea 3, pero el material entregado contiene **`food_categories.xlsx`**: ese XLSX será la fuente de verdad. Las imágenes están organizadas por CID de Google y la POC trabajará solo con una muestra.

## Decisión

El ejercicio será **docker-first**: la ejecución y las pruebas locales se definirán mediante Docker Compose y comandos ejecutados dentro de contenedores. Habrá **dos contenedores**: `app` (Python) y `db` (PostgreSQL). Docker Compose define ambos servicios; un `Dockerfile` construye únicamente `app` y `db` usa la imagen oficial de PostgreSQL. El repositorio podrá procesar los datos entregados y abrir el dashboard sin claves de API ni servicios ajenos a estos contenedores. El crawler, que sí requiere acceso a Just Eat, será un comando independiente; su disponibilidad no bloqueará el resto del pipeline.

Usaremos un único proyecto **Python 3.12** con comandos CLI para cada etapa y una aplicación **Streamlit** para el dashboard. Ambos se ejecutarán en `app` y compartirán la conexión a PostgreSQL; `db` tendrá un volumen persistente. Los datos originales se montarán como entrada de solo lectura y se exportará al host una muestra JSON o CSV de los locales enlazados y platos categorizados. **FastAPI no se incorpora inicialmente**: con un dashboard en el mismo proyecto no hay una API que justifique otro servidor. Se añadirá solo si aparece un consumidor independiente de los datos.

| Necesidad | Elección | Motivo |
| --- | --- | --- |
| Ejecución local | Docker Compose con `app` y `db`; un Dockerfile para Python y la imagen oficial de PostgreSQL | Arranque conjunto de aplicación y base de datos; Chromium y Tesseract quedan dentro de `app`. |
| Lectura de entradas | `ijson` para JSON grandes; `openpyxl` para XLSX | Evitar cargar todos los menús en memoria y leer el archivo de taxonomía real. |
| Crawler | Playwright con Chromium; extracción preferente de datos estructurados de la página | Just Eat puede renderizar contenido dinámico; se conservarán nombre, dirección, menús, secciones, platos, descripciones y precios en el formato del ejemplo. |
| Matching | Filtro de candidatos por coordenadas o dirección, más similitud de nombre con `RapidFuzz` | Reducir comparaciones y tolerar variantes de nombre. Guardar puntuación, evidencias y estado `matched`, `ambiguous` o `unmatched`; aceptar solo coincidencias por encima de umbrales comprobados. |
| Clasificación | Reglas y alias léxicos reproducibles sobre nombre, descripción y sección; `RapidFuzz` para variantes | Asignar un `uidentifier` existente en el XLSX y derivar de esa fila `name`, `parent` y `family`. Los casos sin evidencia suficiente irán a una categoría genérica pertinente o quedarán señalados para revisión. |
| POC de imágenes | Pillow + Tesseract OCR (`spa`/`eng`), en una muestra limitada | Funciona en CPU y permite extraer texto de cartas fotografiadas; se devolverán candidatos con imagen de origen y estado cuando no se detecte una carta legible. |
| Persistencia y visualización | PostgreSQL y Streamlit | La base de datos persiste en `db`; el dashboard consulta sus resultados y muestra filtros, restaurantes enlazados, oferta por categoría y cobertura/calidad del pipeline. |

El flujo será: **entradas inmutables → normalización → matching → clasificación → PostgreSQL/exportación → dashboard**. Crawler y OCR son entradas adicionales, invocadas por separado. Cada etapa producirá resultados deterministas a partir de sus entradas, registrará fallos por registro y podrá repetirse sin duplicar datos. Las claves originales de Just Eat, `googlePlaceId`/CID, ID de menú e ID de plato se conservarán para trazabilidad.

## Verificación prevista

- Comparar el JSON de un crawl con `just_eat_venue_example.json`, incluidas secciones, platos y precios; informar de bloqueos o menús incompletos.
- Revisar manualmente una muestra de pares positivos, ambiguos y negativos; ajustar umbrales de matching con esa muestra y publicar cobertura y distribución de puntuaciones.
- Revisar una muestra estratificada de platos categorizados y la tasa de categoría genérica; comprobar que todas las categorías de salida existen en el XLSX y mantienen su jerarquía.
- Evaluar la POC OCR sobre unas pocas imágenes con transcripción manual de referencia y registrar aciertos, falsos positivos y casos no legibles. El informe técnico explicará límites y mejoras de producción.
- Levantar `app` y `db` con Docker Compose, ejecutar pipeline y pruebas en `app`, abrir el dashboard y documentar los comandos exactos en el README.

## Consecuencias y límites

Se acepta el coste de levantar PostgreSQL para mantener los dos contenedores acordados, sin GPU ni APIs de IA de pago. El crawler depende de la página y de sus medidas de acceso; si una URL falla, el proceso debe registrar el motivo y continuar. OCR no reconocerá con fiabilidad todos los platos en fotos de comida sin texto; esos casos se señalarán como no concluyentes. Las decisiones de matching y clasificación deben poder auditarse mediante sus evidencias, no solo por el resultado final.
