# Roadmap de implementación

Este plan desarrolla el [ADR-0001](ADR-0001-pipeline-local-docker-first.md) y la [constitución](../CONSTITUTION.md). El trabajo se divide en un bloque de preparación, uno por cada tarea del enunciado y un cierre de entrega. Cada bloque termina con un resultado que se puede ejecutar y revisar antes de pasar al siguiente. Marcar una casilla solo cuando la tarea esté terminada y verificada; dejar pendientes las tareas parciales o bloqueadas e indicar lo que falta.

## Bloque 0 — Preparación del proyecto

**Objetivo:** disponer de un entorno local reproducible antes de escribir la lógica de los ejercicios.

- [x] Crear `compose.yaml` con exactamente dos servicios: `app` (Python) y `db` (PostgreSQL), conexión entre ambos, comprobación de disponibilidad de la base de datos y volumen persistente para PostgreSQL.
- [x] Crear el `Dockerfile` de `app`, el archivo de dependencias, la estructura mínima del proyecto y `.dockerignore`. Montar `source/` como entrada de solo lectura y `output/` para los artefactos exportados.
- [x] Crear un `Makefile` con comandos operativos de arranque, parada y pruebas, y objetivos reservados para `crawl`, `match`, `classify`, `images`, `pipeline` y `dashboard`, que se implementarán en sus bloques. Documentar también los comandos equivalentes de Docker Compose para quien no tenga `make`.
- [x] Configurar la conexión a PostgreSQL mediante variables de entorno locales de ejemplo; añadir una comprobación mínima de conexión y la infraestructura de pruebas.

- [x] **Validación de cierre:** las dos imágenes/servicios arrancan con `make up`, `app` conecta con `db`, `make test` funciona dentro de `app` y `make down` detiene el entorno. No hace falta todavía procesar datos ni servir el dashboard final.

## Bloque 1 — Tarea 1: crawler de Just Eat

**Objetivo:** obtener un restaurante y su menú completo a partir de una URL.

- [x] Implementar `make crawl URL=...` como comando independiente; leer la página con Playwright y priorizar datos estructurados cuando estén disponibles.
- [x] Extraer datos del restaurante, menús, secciones, platos, descripciones y precios; guardar un JSON con la estructura de `just_eat_venue_example.json`.
- [x] Tratar respuestas fallidas, campos ausentes y cambios de formato con errores explícitos. El crawl de una URL no debe ser requisito para ejecutar el análisis de los datos ya proporcionados.

- [x] **Validación de cierre:** Tiflis Restaurant produjo dos menús, 26 secciones y 178 apariciones; Edo produjo dos menús, 36 secciones y 292 apariciones, incluidas 28 con selecciones. Sus campos se compararon con el ejemplo. Una URL inexistente y otra con parámetros devolvieron un error identificable y no se exige rastrear las 2.696 URLs.

## Bloque 2 — Tarea 2: matching de restaurantes

**Objetivo:** enlazar locales de Just Eat con candidatos entre los 22.991 locales de Google. `make match` procesa por defecto un pack aleatorio de 50 locales para mantener cada ejecución local acotada; el tamaño y la semilla se pueden indicar explícitamente para repetir una muestra.

- [x] Leer los JSON grandes de forma incremental y normalizar identificadores, nombre, dirección y coordenadas sin alterar los archivos originales.
- [x] Seleccionar candidatos por proximidad geográfica o dirección y puntuarlos con similitud de nombre; registrar distancia, puntuación y decisión `matched`, `ambiguous` o `unmatched`.
- [x] Guardar los resultados en PostgreSQL con claves estables y una carga repetible sin duplicados; exportar una muestra de pares para revisión.
- [x] Revisar manualmente una muestra de aciertos, casos dudosos y rechazos antes de fijar los umbrales.

- [x] **Validación de cierre:** revisada una muestra de aciertos, ambiguos y rechazos, y verificada una segunda ejecución del mismo pack contra PostgreSQL. Este bloque utiliza `just_eat_venues.json`, no depende del crawler.

## Bloque 3 — Tarea 3: clasificación de platos

**Objetivo:** categorizar los platos de los restaurantes enlazados con la taxonomía real entregada.

- [x] Leer `food_categories.xlsx` como fuente de verdad; validar `uidentifier`, `name`, `parent` y `family`.
- [x] Recorrer menús, secciones y platos conservando sus IDs; aplicar reglas y alias sobre nombre, descripción y sección, con tratamiento explícito de categorías genéricas o casos para revisión.
- [x] Persistir categoría, regla o evidencia usada y origen del plato en PostgreSQL; exportar una muestra del conjunto unido y categorizado.
- [x] Revisar una muestra de clasificaciones y medir la proporción de categorías genéricas o sin resolver: 4.215 platos, 3.857 clasificados, 358 en revisión y 554 clasificaciones genéricas en la muestra procesada.

- [x] **Validación de cierre:** `make classify` asigna a cada plato procesado una categoría válida o un estado de revisión, mantiene la jerarquía del XLSX y puede repetirse sin duplicados. No se requiere clasificar los restaurantes de Just Eat que no estén enlazados.

## Bloque 4 — Tarea 4: imágenes, enfoque técnico y POC

**Objetivo:** demostrar en CPU la extracción de candidatos a platos de unas pocas imágenes.

- [x] Seleccionar una muestra pequeña de `google_images.zip`, conservando CID y nombre de imagen.
- [x] Aplicar preparación de imagen y OCR con Tesseract; convertir el texto legible de cartas en candidatos a platos. Registrar `sin_texto_legible` o `no_concluyente` cuando corresponda, sin inventar platos de fotografías sin texto.
- [x] Generar JSON o CSV por imagen con candidatos, texto fuente y estado.
- [x] Documentar técnica, evaluación frente a una transcripción manual pequeña, errores esperados y una posible mejora de producción para fotos de comida sin texto.

- [x] **Validación de cierre:** `make images` procesó cuatro imágenes en CPU, produjo `output/runs/<execution_id>/image-candidates.json` con dos resultados con candidatos aceptados y dos `inconclusive`; separa líneas OCR, revisión y candidatos aceptados. La evaluación visual, la prueba OCR real, los límites y las rutas de evolución están documentados en `docs/IMAGE_POC.md` y en comentarios de código.

## Bloque 5 — Tarea 5: dashboard

**Objetivo:** explorar los resultados guardados en PostgreSQL.

- [ ] Registrar de forma genérica cada ejecución de caso de uso, sus entradas versionadas, parámetros, estado, métricas y error; conservar los resultados por ejecución para distinguir procesados, nuevos, actualizados, sin cambios y rechazados. Falta calcular `updated` y `rejected` por elemento; actualmente se registran `processed`, `new`, `unchanged` y los estados propios de cada proceso.
- [x] Guardar cada exportación como un artefacto inmutable ligado a su ejecución y conservar en PostgreSQL su ruta, tipo, huella y metadatos.
- [x] Crear el dashboard interactivo con Streamlit en `app`, sin introducir FastAPI mientras no exista un consumidor de API independiente. La página raíz abrirá directamente el crawler; no habrá una pestaña de resumen global.
- [x] Crear una pantalla de historial y detalle para crawler, matching, clasificación e imágenes; permitir relanzar cada caso de uso desde controles validados que creen una nueva ejecución. La pantalla OCR acepta imágenes directas; el comando mantiene `source/google_images.zip` como entrada.
- [x] Mostrar, como mínimo, número de restaurantes enlazados y oferta de platos por categoría, junto con una métrica útil de cobertura o calidad del matching/clasificación.
- [x] Tratar el estado sin datos con un mensaje claro y guardar capturas para el README.

- [ ] **Validación de cierre:** `make dashboard` abre una página local que consulta PostgreSQL y las cifras coinciden con las consultas de la base de datos.

## Cierre de entrega

- [x] Añadir una licencia propietaria que reserve todos los derechos y requiera autorización escrita previa para cualquier uso empresarial.
- [x] Completar `README.md` con arquitectura, decisiones de matching y clasificación, requisitos, comandos Docker/Make, ejecución completa, dashboard y capturas.
- [ ] Entregar una muestra final de datos unidos y categorizados, la salida de la POC de imágenes y el informe de herramientas de IA utilizadas. La salida de imágenes y el informe de IA están versionados; el ZIP de `output/` se generará tras el ciclo completo de pruebas.
- [ ] Ejecutar desde cero el recorrido documentado: levantar servicios, pruebas, pipeline, POC y dashboard. Comprobar que los artefactos se reproducen sin depender de una ejecución anterior.

- [ ] **Validación de cierre:** una persona puede reproducir la entrega siguiendo el README y encontrar los cinco ejercicios, sus resultados y sus límites documentados.

## Orden y dependencias

`Bloque 0 → Bloque 1 → Bloque 2 → Bloque 3 → Bloque 4 → Bloque 5 → Cierre` es el orden de trabajo propuesto. El bloque 1 es independiente del bloque 2: si Just Eat bloquea el crawl, se registra la incidencia y se continúa con el dataset proporcionado. El dashboard necesita los resultados de los bloques 2 y 3; la POC de imágenes puede ejecutarse de forma separada.
