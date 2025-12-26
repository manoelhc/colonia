sync:
	uv sync
run:
	docker compose -f docker-compose.full.yml up
test:
	uv sync --only-dev
	uv run pytest tests
