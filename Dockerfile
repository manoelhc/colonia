FROM python:3.12-slim

WORKDIR /app

# Install uv package manager
RUN pip install --no-cache-dir uv

# Expose port
EXPOSE 8000

# Start the application (dependencies installed via mounted volume)
CMD ["sh", "-c", "uv run alembic upgrade head && uv run python -m main"]
