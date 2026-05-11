# FastAPI Starter Project

A minimal FastAPI project template with:

- **FastAPI** — Modern async web framework
- **Pydantic v2** — Data validation and settings
- **SQLAlchemy** — ORM with SQLite (swappable)
- **pytest** — Testing with TestClient

## Quick Start

```bash
# Create virtual environment
uv venv

# Install dependencies
uv sync

# Copy environment file
cp .env.example .env

# Run development server
uv run uvicorn main:app --reload

# Run tests
uv run pytest
```

## Project Structure

```txt
├── main.py              # Application entry point
├── app/
│   ├── __init__.py
│   ├── config.py        # Settings management
│   ├── database.py      # DB connection
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   └── api/
│       └── v1/
│           ├── router.py
│           └── items.py  # Item CRUD routes
└── tests/
    └── test_api.py      # API tests
```

## API Endpoints

| Method | Endpoint           | Description        |
| ------ | ------------------ | ------------------ |
| GET    | `/health`          | Health check       |
| GET    | `/api/v1/items/`   | List items         |
| POST   | `/api/v1/items/`   | Create item        |
| GET    | `/api/v1/items/{id}` | Get item         |
| PUT    | `/api/v1/items/{id}` | Update item      |
| DELETE | `/api/v1/items/{id}` | Delete item      |

## Documentation

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>
- **OpenAPI JSON**: <http://localhost:8000/openapi.json>
