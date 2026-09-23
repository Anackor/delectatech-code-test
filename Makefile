.PHONY: up down check test crawl match classify images pipeline dashboard

# Pasar una URL como: make crawl URL=https://www.just-eat.es/restaurants-foo/menu
export CRAWL_URL = $(value URL)

up:
	docker compose up --build -d
	docker compose exec -T app python -m app.db

down:
	docker compose down

check:
	docker compose exec -T app python -m app.db

test:
	docker compose exec -T app python -m unittest discover -s tests -t . -v

crawl:
	docker compose exec -T -e CRAWL_URL app python -m app.crawler.entrypoint

match:
	$(error El matching se implementara en el bloque 2)

classify:
	$(error La clasificacion se implementara en el bloque 3)

images:
	$(error La POC de imagenes se implementara en el bloque 4)

pipeline:
	$(error El pipeline se implementara en los bloques 2 y 3)

dashboard:
	$(error El dashboard se implementara en el bloque 5)
