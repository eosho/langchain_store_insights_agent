from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes.version import router, _NAME, _VERSION


def _build_test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


client = TestClient(_build_test_app())


def test_version_endpoint_status() -> None:
    response = client.get("/version")
    assert response.status_code == 200


def test_version_endpoint_content_type() -> None:
    response = client.get("/version")
    assert response.headers["content-type"].startswith("application/json")


def test_version_endpoint_json_shape() -> None:
    data = client.get("/version").json()
    assert "name" in data
    assert "version" in data


def test_version_endpoint_values() -> None:
    data = client.get("/version").json()
    assert data["name"] == _NAME
    assert data["version"] == _VERSION

