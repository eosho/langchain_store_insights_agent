# Deployment

## Docker

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run with production server
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

### docker-compose.yml

```yaml
version: "3.8"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/app
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=app

volumes:
  postgres_data:
```

## Production Server (Gunicorn + Uvicorn)

```bash
# Install
pip install gunicorn uvicorn[standard]

# Run with 4 workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# With config file
gunicorn main:app -c gunicorn.conf.py
```

### gunicorn.conf.py

```python
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = "info"
```

## Environment Configuration

### pydantic-settings

```python
# config.py
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "My API"
    debug: bool = False

    # Database
    database_url: str

    # Security
    secret_key: SecretStr
    access_token_expire_minutes: int = 30

    # External services
    redis_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
```

### .env file

```env
DATABASE_URL=postgresql://user:password@localhost:5432/app
SECRET_KEY=your-super-secret-key-change-in-production
DEBUG=false
```

## Health Check Endpoint

```python
from enum import StrEnum

from pydantic import BaseModel


class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthResponse(BaseModel):
    status: HealthStatus
    database: HealthStatus
    version: str


@app.get("/health", response_model=HealthResponse)
async def health_check(db: DBDep):
    db_status = HealthStatus.HEALTHY
    try:
        db.execute("SELECT 1")
    except Exception:  # noqa: BLE001
        db_status = HealthStatus.UNHEALTHY

    overall = (
        HealthStatus.HEALTHY
        if db_status == HealthStatus.HEALTHY
        else HealthStatus.DEGRADED
    )

    return HealthResponse(
        status=overall,
        database=db_status,
        version="1.0.0",
    )
```

## Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/api
upstream api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://api/health;
        access_log off;
    }
}
```

## Azure Container Apps

See the `azd-deployment` skill for full Azure deployment patterns.

```bash
# Quick deploy with azd
azd init
azd up
```

## Kubernetes (Basic)

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-app
  template:
    metadata:
      labels:
        app: fastapi-app
    spec:
      containers:
        - name: api
          image: myregistry/fastapi-app:latest
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: api-secrets
                  key: database-url
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  selector:
    app: fastapi-app
  ports:
    - port: 80
      targetPort: 8000
  type: ClusterIP
```

## Best Practices

- **Use multi-stage Docker builds** — Reduce image size
- **Never hardcode secrets** — Use environment variables or secret managers
- **Health checks** — Required for orchestrators (K8s, ACA)
- **Structured logging** — JSON format for log aggregation
- **Graceful shutdown** — Handle SIGTERM properly
- **Connection pooling** — Configure DB pool for production load
- **Rate limiting** — Protect public endpoints
- **HTTPS only** — Terminate TLS at load balancer
