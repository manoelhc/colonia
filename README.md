# colonia
An Open Source Alternative to Spacelift



# Development Environment Setup

To set up the development environment, follow these steps:

## 1. Clone the Repository
```bash
git clone https://github.com/manoelhc/colonia.git
cd colonia
```

## 2. Install Python 3.14.0
Install `pyenv` and install the 3.14.0 version of Python using `pyenv`:
```bash
pyenv install 3.14.0
pyenv local 3.14.0
```

Follow the instructions to add the proper environment variables to your shell.

## 3. Install Dependencies
Install `uv` package manager:
```bash
pip install uv
```

Install project dependencies:
```bash
uv sync
```

## 4. Database Setup

Colonia uses SQLite with Alembic for database migrations.

### Initialize the Database
Run the migrations to create the database schema:
```bash
uv run alembic upgrade head
```

This will:
- Create the SQLite database file (`colonia.db`)
- Create all necessary tables (projects, etc.)
- Apply all pending migrations

### Migration Commands

**Check current migration status:**
```bash
uv run alembic current
```

**View migration history:**
```bash
uv run alembic history
```

**Create a new migration (after model changes):**
```bash
uv run alembic revision --autogenerate -m "Description of changes"
```

**Upgrade to latest migration:**
```bash
uv run alembic upgrade head
```

**Downgrade one migration:**
```bash
uv run alembic downgrade -1
```

**Downgrade to specific revision:**
```bash
uv run alembic downgrade <revision_id>
```

## 5. Run Colonia
Start the development server:
```bash
uv run python -m main
```

The application will be available at `http://localhost:8000`

## 6. RabbitMQ Integration

Colonia uses RabbitMQ for asynchronous repository scanning. When a project is created with a repository URL, the backend sends a message to RabbitMQ, which triggers the `repo-scan.py` consumer to fetch and process the `colonia.yaml` file from the repository.

### Starting RabbitMQ

Use Docker Compose to start RabbitMQ locally:
```bash
docker-compose up -d
```

RabbitMQ will be available at:
- AMQP: `localhost:5672`
- Management UI: `http://localhost:15672` (username: `colonia`, password: `colonia`)

### Running the Repository Scanner

Start the repository scanner consumer in a separate terminal:
```bash
uv run python repo-scan.py
```

The scanner will:
1. Listen for messages from RabbitMQ
2. Fetch `colonia.yaml` from the repository
3. Create/update/delete environments and stacks based on the YAML configuration

### colonia.yaml Format

The `colonia.yaml` file should be placed at the root of your repository and follows this format:

```yaml
environments:
  - name: development
    dir: example/environments/development
  - name: staging
    dir: example/environments/staging

stacks:
  - name: "VPC"
    environments:
      - development
      - staging
    stack: stacks/vpc
  - name: "ECS"
    environments:
      - development
      - staging
    stack: stacks/ecs
```

If no `colonia.yaml` file exists in the repository, no resources will be created.

## Project Structure

```
colonia/
├── alembic/              # Database migrations
│   └── versions/         # Migration files
├── models/               # SQLModel database models
│   ├── project.py        # Project model
│   ├── environment.py    # Environment model
│   ├── stack.py          # Stack model
│   └── stack_environment.py  # Stack-Environment relationship
├── static/               # Static assets (CSS, JS)
├── templates/            # HTML templates
├── tests/                # Test files
├── api.py                # API endpoint handlers
├── database.py           # Database configuration
├── main.py               # Application entry point
├── rabbitmq.py           # RabbitMQ connection utilities
├── repo-scan.py          # RabbitMQ consumer for repository scanning
├── docker-compose.yml    # Docker Compose for RabbitMQ
└── alembic.ini           # Alembic configuration
```
