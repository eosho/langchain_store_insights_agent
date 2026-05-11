# Testing FastAPI Applications

## Basic Testing with TestClient

```python
# test_main.py
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_create_item():
    response = client.post(
        "/items/",
        json={"title": "Test Item", "description": "A test item"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Item"
    assert "id" in data
```

## Pytest Fixtures

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """Get auth headers for authenticated requests."""
    response = client.post(
        "/token",
        data={"username": "test@example.com", "password": "testpass"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

## Testing with Authentication

```python
def test_protected_route_unauthorized(client):
    response = client.get("/users/me")
    assert response.status_code == 401


def test_protected_route_authorized(client, auth_headers):
    response = client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert "email" in response.json()
```

## Async Testing

```python
# test_async.py
import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/async-endpoint")
    assert response.status_code == 200
```

## Mocking Dependencies

```python
from unittest.mock import Mock, patch


def test_with_mocked_service(client):
    mock_service = Mock()
    mock_service.get_item.return_value = {"id": 1, "title": "Mocked"}

    with patch("app.api.endpoints.items.item_service", mock_service):
        response = client.get("/items/1")

    assert response.status_code == 200
    assert response.json()["title"] == "Mocked"


def test_override_dependency(client):
    def mock_get_current_user():
        return {"id": 1, "username": "testuser", "role": "admin"}

    app.dependency_overrides[get_current_user] = mock_get_current_user
    response = client.get("/admin/")
    assert response.status_code == 200
    app.dependency_overrides.clear()
```

## Testing File Uploads

```python
def test_upload_file(client):
    response = client.post(
        "/upload/",
        files={"file": ("test.txt", b"file content", "text/plain")},
    )
    assert response.status_code == 200
    assert response.json()["filename"] == "test.txt"
```

## Testing WebSockets

```python
def test_websocket(client):
    with client.websocket_connect("/ws") as websocket:
        websocket.send_json({"message": "hello"})
        data = websocket.receive_json()
        assert data["message"] == "hello"
```

## Coverage Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.coverage.run]
source = ["app"]
omit = ["tests/*", "*/__init__.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
fail_under = 80
```

## Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_users.py

# Run with verbose output
pytest -v

# Run only failing tests
pytest --lf

# Parallel execution
pytest -n auto
```

## Best Practices

- **Use fixtures** — Share setup code across tests
- **Test isolation** — Each test should be independent
- **Test the API** — Focus on request/response, not internals
- **Mock external services** — Don't call real APIs in tests
- **100% happy path, 80% edge cases** — Cover critical paths first
- **Use factories** — Factory Boy for test data generation
- **Name tests clearly** — `test_<what>_<condition>_<expected>`
