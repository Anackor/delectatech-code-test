# Constitución del ejercicio

## Objetivo

Entregar un pipeline de datos de restauración que pueda reproducirse localmente: extraer un menú de Just Eat, enlazar los locales proporcionados con Google, clasificar sus platos con la taxonomía entregada, demostrar una extracción limitada desde imágenes y explorar los resultados en un dashboard.

## Principios de trabajo

1. **Docker-first y dos contenedores.** Docker Compose define `app` (Python: pipeline, pruebas y dashboard) y `db` (PostgreSQL). Un Dockerfile construye `app`; `db` usa la imagen oficial de PostgreSQL. El README debe dar los comandos exactos para repetir la ejecución en un equipo local.
2. **Una fuente de verdad por dato.** Los JSON, el XLSX y las imágenes de `source/` permanecen intactos. Los datos transformados se generan en `output/` y conservan identificadores y procedencia.
3. **Resultados verificables.** Matching y clasificación exponen puntuación o regla aplicada y distinguen resultados fiables de ambiguos. No se inventan platos a partir de imágenes sin evidencia legible.
4. **Fallos aislados.** Un restaurante, URL o imagen defectuosos no detienen el procesamiento de los demás. Las etapas se pueden repetir sin duplicados.
5. **Alcance ajustado al enunciado.** El crawl acepta una URL y produce el JSON del ejemplo; el pipeline analítico usa el dataset ya proporcionado. La POC de imágenes usa una muestra pequeña y CPU.
6. **Entrega comprensible.** README con arquitectura breve, ejecución y capturas; muestra de salida; métricas de cobertura y calidad; informe de herramientas de IA utilizadas.

## Stack acordado

Python 3.12 · Docker Compose · PostgreSQL · Playwright/Chromium para el crawler · `ijson` y `openpyxl` para entradas · `RapidFuzz` para matching y variantes textuales · Pillow/Tesseract para OCR en CPU · Streamlit para dashboard. FastAPI se reservará para el caso de que exista un consumidor de API independiente; no forma parte de la primera implementación. Las pruebas automatizadas cubrirán las reglas y transformaciones críticas con el menor número de dependencias posible.

La decisión y sus límites se desarrollan en [ADR-0001](docs/ADR-0001-pipeline-local-docker-first.md).
