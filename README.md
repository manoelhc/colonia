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

## Project Structure

```
colonia/
├── alembic/              # Database migrations
│   └── versions/         # Migration files
├── models/               # SQLModel database models
├── static/               # Static assets (CSS, JS)
├── templates/            # HTML templates
├── api.py               # API endpoint handlers
├── database.py          # Database configuration
├── main.py              # Application entry point
└── alembic.ini          # Alembic configuration
```
