# Food Delivery Data Integration & Analysis

Implementación por bloques del [roadmap](docs/ROADMAP.md). Los bloques 0 y 1 están completados: entorno Docker y crawler de Just Eat.

## Requisitos

- Docker con Compose.
- GNU Make, opcional; debajo están los comandos equivalentes de Docker Compose.

## Arranque y comprobación

Desde `code-test/`:

| Con Make | Sin Make |
| --- | --- |
| `make up` | `docker compose up --build -d` y `docker compose exec -T app python -m app.db` |
| `make check` | `docker compose exec -T app python -m app.db` |
| `make test` | `docker compose exec -T app python -m unittest discover -s tests -t . -v` |
| `make down` | `docker compose down` |

`make up` levanta `app` y `db` y verifica la conexión. `make test` ejecuta pruebas unitarias de reglas y casos de uso, además de integraciones de JSON y PostgreSQL. `make down` conserva el volumen de datos.

Las credenciales locales predeterminadas están en [`.env.example`](.env.example). Se pueden cambiar copiando ese archivo a `.env` antes de iniciar el entorno; `.env` no se versiona. Para cambiar credenciales de una base ya inicializada hay que actualizar también el volumen o crear uno nuevo.

`source/` se monta en `app` como solo lectura; `output/` recibe los resultados exportados. PostgreSQL guarda sus datos en un volumen de Docker. La base de datos no publica un puerto al host: `app` se conecta a `db:5432` dentro de Compose.

## Crawler de Just Eat

Con los servicios levantados, extrae un restaurante con:

```sh
make crawl URL=https://www.just-eat.es/restaurants-tiflis-restaurant-barcelona/menu
```

El comando abre la página con Chromium y convierte su estado estructurado de servidor al formato de `source/just_eat_venue_example.json`. Conserva los menús de entrega y recogida, secciones, platos, precios, variantes y extras. El JSON se escribe de forma atómica en `output/<slug>.json`; la salida estándar informa de la versión del menú, recuentos y duración.

La URL debe ser una página pública de menú de `www.just-eat.es`, sin parámetros. Una respuesta bloqueada, un catálogo incompleto o un cambio de formato termina con un JSON de error en stderr y no sustituye una salida existente. El crawler requiere acceso de red a Just Eat, pero los siguientes bloques utilizan los ficheros ya entregados y no dependen de esa conexión.

## Estado

`crawl` está disponible. Los objetivos `match`, `classify`, `images`, `pipeline` y `dashboard` se incorporarán en sus bloques. La [decisión de arquitectura](docs/ADR-0001-pipeline-local-docker-first.md) y la [constitución](CONSTITUTION.md) describen el alcance completo.
