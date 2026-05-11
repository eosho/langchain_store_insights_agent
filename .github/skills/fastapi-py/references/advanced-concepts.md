# Advanced FastAPI Features

## Lifespan Events

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: runs before accepting requests
    print("Starting up...")
    app.state.db_pool = await create_db_pool()
    app.state.redis = await create_redis_connection()

    yield  # App runs here

    # Shutdown: runs after all requests complete
    print("Shutting down...")
    await app.state.db_pool.close()
    await app.state.redis.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    # Access shared resources
    return {"pool_size": app.state.db_pool.size}
```

## Custom Middleware

### Function-based Middleware

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        import time

        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        response.headers["X-Response-Time"] = f"{duration:.4f}s"
        return response


app.add_middleware(TimingMiddleware)
```

### Request/Response Logging

```python
import logging

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        return response


# Note: BaseHTTPMiddleware subclasses need type: ignore[arg-type]
# when passed to add_middleware due to Starlette typing gap
app.add_middleware(LoggingMiddleware)  # type: ignore[arg-type]
```

## WebSockets

```python
from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client {client_id} left")
```

## Streaming Responses

### Server-Sent Events (SSE)

```python
import asyncio

from fastapi.responses import StreamingResponse


async def event_generator():
    for i in range(10):
        yield f"data: Event {i}\n\n"
        await asyncio.sleep(1)


@app.get("/stream")
async def stream_events():
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
```

### File Streaming

```python
from fastapi.responses import StreamingResponse


def file_iterator(file_path: str, chunk_size: int = 8192):
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            yield chunk


@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"/files/{filename}"
    return StreamingResponse(
        file_iterator(file_path),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
```

## Background Tasks

```python
from fastapi import BackgroundTasks


def send_notification(email: str, message: str):
    # Simulate slow operation
    import time

    time.sleep(5)
    print(f"Sent to {email}: {message}")


@app.post("/notify/{email}")
async def notify(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_notification, email, "Welcome!")
    return {"message": "Notification scheduled"}
```

## Caching with Redis

```python
import json
from functools import wraps
from typing import Callable

import redis.asyncio as redis

redis_client = redis.from_url("redis://localhost")


def cache(expire: int = 60):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            cached = await redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            result = await func(*args, **kwargs)
            await redis_client.setex(cache_key, expire, json.dumps(result))
            return result

        return wrapper

    return decorator


@app.get("/expensive/")
@cache(expire=300)
async def expensive_operation():
    # Simulated expensive computation
    return {"result": "computed"}
```

## Rate Limiting

```python
import time
from collections import defaultdict

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()

        # Clean old requests
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] if now - t < self.window_seconds
        ]

        if len(self.requests[client_ip]) >= self.max_requests:
            raise HTTPException(429, "Too many requests")

        self.requests[client_ip].append(now)
        return await call_next(request)


app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)
```

## Custom Exception Handlers

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class CustomException(Exception):
    def __init__(self, name: str, code: int):
        self.name = name
        self.code = code


@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.code,
        content={"error": exc.name, "detail": "Custom error occurred"},
    )


@app.get("/error/")
async def raise_error():
    raise CustomException(name="CustomError", code=418)
```

## Request Validation with Custom Types

```python
from typing import Annotated

from pydantic import AfterValidator


def validate_positive(v: int) -> int:
    if v <= 0:
        raise ValueError("must be positive")
    return v


PositiveInt = Annotated[int, AfterValidator(validate_positive)]


@app.get("/items/{item_id}")
def read_item(item_id: PositiveInt):
    return {"item_id": item_id}
```

## GraphQL Integration

```python
import strawberry
from strawberry.fastapi import GraphQLRouter


@strawberry.type
class Query:
    @strawberry.field
    def hello(self, name: str = "World") -> str:
        return f"Hello {name}"


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")
```

## Sub-Applications

```python
from fastapi import FastAPI

# Main app
app = FastAPI()

# Sub-application for API v1
api_v1 = FastAPI()


@api_v1.get("/items/")
def read_items_v1():
    return {"version": "v1", "items": []}


# Sub-application for API v2
api_v2 = FastAPI()


@api_v2.get("/items/")
def read_items_v2():
    return {"version": "v2", "items": [], "metadata": {}}


# Mount sub-apps
app.mount("/api/v1", api_v1)
app.mount("/api/v2", api_v2)
```

## Best Practices

- **Use lifespan** — Preferred over deprecated `@app.on_event`
- **Middleware order matters** — First added = outermost layer
- **WebSocket auth** — Validate before accepting connection
- **Stream large files** — Don't load entire file into memory
- **Cache strategically** — Cache expensive operations, invalidate properly
- **Rate limit public APIs** — Protect against abuse
