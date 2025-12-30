sync:
	uv sync
run:
	docker compose -f docker-compose.full.yml up
test:
	uv sync --only-dev
	uv run pytest tests
run-new:
	docker compose -f docker-compose.full.yml down
	docker login
	docker network rm colonia_colonia-network|| true
	docker compose -f docker-compose.full.yml up --build
