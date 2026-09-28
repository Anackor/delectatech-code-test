.PHONY: up down check test crawl match classify images pipeline dashboard

# Pasar una URL como: make crawl URL=https://www.just-eat.es/restaurants-foo/menu
export CRAWL_URL = $(value URL)
# Por defecto procesa 50 locales; se puede repetir la muestra con SEED=123.
export MATCH_PACK_SIZE = $(if $(PACK_SIZE),$(PACK_SIZE),50)
export MATCH_SEED = $(value SEED)

up:
	docker compose up --build -d
	docker compose exec -T --user appuser app python -m app.db

down:
	docker compose down

check:
	docker compose exec -T --user appuser app python -m app.db

test:
	docker compose exec -T --user appuser app python -m unittest discover -s tests -t . -v

crawl:
	docker compose exec -T --user appuser -e CRAWL_URL app python -m app.crawler.entrypoint

match:
	docker compose exec -T --user appuser -e MATCH_PACK_SIZE -e MATCH_SEED app python -m app.matching.entrypoint

classify:
	docker compose exec -T --user appuser app python -m app.classification.entrypoint

images:
	docker compose exec -T --user appuser app python -m app.images.entrypoint

pipeline:
	docker compose exec -T --user appuser -e MATCH_PACK_SIZE -e MATCH_SEED app python -m app.matching.entrypoint
	docker compose exec -T --user appuser app python -m app.classification.entrypoint

dashboard:
	docker compose up --build -d app
