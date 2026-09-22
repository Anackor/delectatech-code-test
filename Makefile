.PHONY: up down check test crawl match classify images pipeline dashboard

up:
	docker compose up --build -d
	docker compose exec -T app python -m app.db

down:
	docker compose down

check:
	docker compose exec -T app python -m app.db

test:
	docker compose exec -T app python -m unittest discover -s tests -v

crawl:
	$(error El crawler se implementara en el bloque 1)

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
