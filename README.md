# Food Delivery Data Integration & Analysis

Implementación docker-first del reto de integración y análisis de datos de restauración. El proyecto se desarrolla por bloques según el [roadmap](docs/ROADMAP.md): el bloque 0 prepara el entorno y el bloque 1 implementa el crawler de Just Eat.

## Instalación local

Solo se necesita Docker con Docker Compose. GNU Make es opcional: todos los comandos tienen alternativa con Docker Compose. Python, PostgreSQL, Chromium y las dependencias del proyecto se instalan dentro del contenedor `app`.

```sh
git clone https://github.com/Anackor/delectatech-code-test.git
cd delectatech-code-test
```

Las credenciales locales predeterminadas están en [`.env.example`](.env.example). Para personalizarlas, copie el archivo antes del primer arranque:

```powershell
Copy-Item .env.example .env
```

Desde la raíz del repositorio, inicie el entorno:

```sh
make up
```

Sin Make:

```sh
docker compose up --build -d
docker compose exec -T app python -m app.db
```

`app` y `db` son los únicos servicios. PostgreSQL no expone puertos al host; `app` se conecta a `db:5432`. Los datos de `source/` se montan como entrada de solo lectura y los resultados se escriben en `output/`. El volumen de PostgreSQL persiste tras detener los servicios.

## Operación local

| Acción | Con Make | Sin Make |
| --- | --- | --- |
| Arrancar y comprobar PostgreSQL | `make up` | `docker compose up --build -d` y `docker compose exec -T app python -m app.db` |
| Comprobar PostgreSQL | `make check` | `docker compose exec -T app python -m app.db` |
| Ejecutar pruebas | `make test` | `docker compose exec -T app python -m unittest discover -s tests -t . -v` |
| Detener servicios | `make down` | `docker compose down` |

`make test` ejecuta pruebas unitarias de reglas y casos de uso, además de integraciones de JSON y PostgreSQL.

## Reproducir los casos de uso

| Caso de uso | Comando | Estado |
| --- | --- | --- |
| Extraer el menú de un restaurante Just Eat | `make crawl URL=...` | Disponible |
| Enlazar restaurantes Just Eat y Google | `make match` | Disponible |
| Clasificar platos | `make classify` | Disponible |
| Extraer candidatos desde imágenes | `make images` | Bloque 4 pendiente |
| Consultar métricas en dashboard | `make dashboard` | Bloque 5 pendiente |

### Crawler de Just Eat

Con el entorno iniciado, ejecute una captura válida:

```sh
make crawl URL=https://www.just-eat.es/restaurants-tiflis-restaurant-barcelona/menu
```

El crawler abre la página con Chromium, interpreta su estado estructurado y genera `output/restaurants-tiflis-restaurant-barcelona.json`. La salida estándar informa de la versión del menú, los recuentos y la duración.

Para elegir el nombre del archivo de salida:

```sh
docker compose exec -T app python -m app.crawler.entrypoint \
  https://www.just-eat.es/restaurants-tiflis-restaurant-barcelona/menu \
  --output output/tiflis.json
```

Para probar un error de entrada controlado:

```sh
make crawl URL=https://www.just-eat.es/restaurants-tiflis-restaurant-barcelona/menu?invalid=1
```

La URL debe ser una página pública de menú de `www.just-eat.es`, sin parámetros. Un bloqueo, catálogo incompleto o cambio de formato produce un JSON de error en `stderr`, devuelve un código distinto de cero y no reemplaza una salida previa. El crawler requiere acceso de red a Just Eat; los bloques analíticos posteriores trabajan sobre los ficheros entregados y no dependen de esa conexión.

### Clasificación de platos

Ejecute primero `make match` para guardar los restaurantes aceptados y, a continuación:

```sh
make classify
```

El comando lee `source/food_categories.xlsx` como fuente de verdad, recorre de forma incremental los menús de los restaurantes enlazados y crea `output/classified-dishes.json`. Cada aparición conserva los IDs de restaurante, menú, sección y plato; incluye la categoría del XLSX con su jerarquía, o el estado `review` cuando no existe evidencia suficiente.

La taxonomía aporta el identificador, nombre, padre, familia y marca de categoría genérica de cada resultado. Las reglas se ejecutan por orden: nombre del plato, sección, cocina declarada por el restaurante junto con una señal específica del plato, descripción y categoría genérica del padre de la taxonomía. Las coincidencias usan alias con límites de palabra para evitar que un ingrediente o una subcadena cambien indebidamente la categoría. Los casos restantes quedan marcados para revisión.

## Arquitectura y estado

Cada ejercicio separa reglas, casos de uso y adaptadores. El crawler organiza el caso de uso y sus puertos en `app/crawler/application/`; los adaptadores de Playwright, Just Eat y JSON están en `app/crawler/adapters/`. La clasificación sigue la misma estructura en `app/classification/`: XLSX y JSON son entradas, las reglas son puras y PostgreSQL/JSON son salidas. Las pruebas se dividen entre `tests/unit/`, `tests/integration/` y fuentes reutilizables en `tests/sources/`.

La [decisión de arquitectura](docs/ADR-0001-pipeline-local-docker-first.md) y la [constitución](CONSTITUTION.md) documentan el alcance y las restricciones del ejercicio.
