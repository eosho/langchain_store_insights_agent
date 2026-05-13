import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import health


class TestReadyzEndpoint(unittest.TestCase):
    def _client_with_checks(self, checks):
        app = FastAPI()
        app.include_router(health.router, prefix="/v1/api")
        app.state.readyz_checks = checks
        return TestClient(app)

    def test_readyz_all_checks_pass(self):
        async def db_check():
            return None

        async def llm_check():
            return None

        with self._client_with_checks([("db", db_check), ("llm", llm_check)]) as client:
            response = client.get("/v1/api/readyz")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "ready", "checks": {"db": "ok", "llm": "ok"}},
        )

    def test_health_endpoint_unchanged(self):
        with self._client_with_checks([]) as client:
            response = client.get("/v1/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_readyz_returns_503_when_one_check_fails(self):
        async def db_check():
            return None

        async def vector_store_check():
            raise RuntimeError("vector store unavailable")

        with self._client_with_checks(
            [("db", db_check), ("vector_store", vector_store_check)]
        ) as client:
            response = client.get("/v1/api/readyz")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["status"], "not_ready")
        self.assertEqual(response.json()["checks"]["db"], "ok")
        self.assertEqual(
            response.json()["checks"]["vector_store"],
            "fail: vector store unavailable",
        )


if __name__ == "__main__":
    unittest.main()
