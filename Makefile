sync:
	uv sync
run:
	uv run python -m main
test:
	uv sync --only-dev
	uv run pytest tests
