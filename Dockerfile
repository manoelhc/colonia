FROM python:3.14-slim

WORKDIR /app

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY . .

# Create database directory
RUN mkdir -p /app/data

# Run database migrations
RUN uv run alembic upgrade head

# Expose port
EXPOSE 8000

# Start the application
CMD ["uv", "run", "python", "-m", "main"]
