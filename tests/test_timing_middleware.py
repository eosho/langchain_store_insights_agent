from __future__ import annotations

import json
import logging
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.timing import RequestTimingMiddleware


class _ListHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


class RequestTimingMiddlewareTests(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = logging.getLogger("app.timing")
        self.logger.setLevel(logging.INFO)
        self.handler = _ListHandler()
        self.logger.addHandler(self.handler)

    def tearDown(self) -> None:
        self.logger.removeHandler(self.handler)

    def test_logs_non_negative_integer_duration_for_2xx(self) -> None:
        app = FastAPI()
        app.add_middleware(RequestTimingMiddleware)

        @app.get("/ok")
        async def ok() -> dict:
            return {"ok": True}

        client = TestClient(app)
        response = client.get("/ok")
        self.assertEqual(response.status_code, 200)

        payload = json.loads(self.handler.records[-1].getMessage())
        self.assertEqual(payload["method"], "GET")
        self.assertEqual(payload["path"], "/ok")
        self.assertEqual(payload["status_code"], 200)
        self.assertIsInstance(payload["duration_ms"], int)
        self.assertGreaterEqual(payload["duration_ms"], 0)

    def test_logs_non_negative_integer_duration_for_5xx_and_reraises(self) -> None:
        app = FastAPI()
        app.add_middleware(RequestTimingMiddleware)

        @app.get("/boom")
        async def boom() -> dict:
            raise RuntimeError("boom")

        client = TestClient(app)
        with self.assertRaises(RuntimeError):
            client.get("/boom")

        payload = json.loads(self.handler.records[-1].getMessage())
        self.assertEqual(payload["method"], "GET")
        self.assertEqual(payload["path"], "/boom")
        self.assertEqual(payload["status_code"], 500)
        self.assertIsInstance(payload["duration_ms"], int)
        self.assertGreaterEqual(payload["duration_ms"], 0)
