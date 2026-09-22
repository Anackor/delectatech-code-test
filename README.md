# Food Delivery Data Integration & Analysis

Implementación por bloques del [roadmap](docs/ROADMAP.md). El bloque 0 prepara el entorno Docker; los ejercicios se incorporarán en los siguientes bloques.

## Requisitos

- Docker con Compose.
- GNU Make, opcional; debajo están los comandos equivalentes de Docker Compose.

## Arranque y comprobación

Desde `code-test/`:

| Con Make | Sin Make |
| --- | --- |
| `make up` | `docker compose up --build -d` y `docker compose exec -T app python -m app.db` |
| `make check` | `docker compose exec -T app python -m app.db` |
| `make test` | `docker compose exec -T app python -m unittest discover -s tests -v` |
| `make down` | `docker compose down` |

`make up` levanta `app` y `db` y verifica la conexión. `make test` ejecuta una prueba de integración contra PostgreSQL. `make down` conserva el volumen de datos.

Las credenciales locales predeterminadas están en [`.env.example`](.env.example). Se pueden cambiar copiando ese archivo a `.env` antes de iniciar el entorno; `.env` no se versiona. Para cambiar credenciales de una base ya inicializada hay que actualizar también el volumen o crear uno nuevo.

`source/` se monta en `app` como solo lectura; `output/` recibe los resultados exportados. PostgreSQL guarda sus datos en un volumen de Docker. La base de datos no publica un puerto al host: `app` se conecta a `db:5432` dentro de Compose.

## Estado

Los objetivos `crawl`, `match`, `classify`, `images`, `pipeline` y `dashboard` del Makefile indican el bloque en el que se implementarán. La [decisión de arquitectura](docs/ADR-0001-pipeline-local-docker-first.md) y la [constitución](CONSTITUTION.md) describen el alcance completo.
