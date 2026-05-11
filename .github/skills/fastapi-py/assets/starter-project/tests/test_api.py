"""Tests for API endpoints."""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from main import app

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class TestItems:
    """Test cases for items API."""

    def test_create_item(self):
        response = client.post("/api/v1/items/", json={"title": "Test Item"})
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Item"
        assert "id" in data

    def test_list_items(self):
        response = client.get("/api/v1/items/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_item_not_found(self):
        response = client.get("/api/v1/items/9999")
        assert response.status_code == 404

    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
