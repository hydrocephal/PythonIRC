
**PythonIRC — IRC-style Chat**

A real-time IRC-style chat application built with FastAPI, WebSockets, and PostgreSQL.

---

**Stack**

- FastAPI + WebSockets
- PostgreSQL + asyncpg + SQLAlchemy (async)
- Alembic migrations
- JWT authentication (PyJWT)
- bcrypt password hashing
- Redis (pub/sub, multi-worker state)
- Sentry (error tracking)
- Prometheus + Grafana (metrics)
- asyncio CLI client

---

**Requirements**

- Python 3.10+
- Docker + Docker Compose (recommended)
- PostgreSQL
- Redis

---

**Installation**

Clone the repository:

bash

```bash
git clone https://github.com/hydrocephal/PythonIRC.git
cd PythonIRC
```

**Option A — Docker (recommended)**

bash

```bash
cp .env.example .env
# edit .env
docker compose up --build
```

**Option B — Local**

bash

```bash
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv sync

cp .env.example .env
```

Run migrations:

bash

```bash
alembic upgrade head
```

Start the server:

bash

```bash
uvicorn app.main:app --reload
```

In a separate terminal, start the client:

bash

```bash
python client/cli.py
```

---

**Configuration**

Edit `.env`:

```
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=postgresql+asyncpg://user:password@localhost/pythonirc
REDIS_URL=redis://localhost:6379
SENTRY_DSN=your-sentry-dsn-here
```

---

**Usage**

```
1. Register a new account or login
2. Start chatting

Commands:
  /online   — show online users
  /exit     — disconnect from chat
```

---

**Project Structure**

```
app/
  core/         — configuration
  db/           — database connection
  models/       — SQLAlchemy models
  routers/      — HTTP and WebSocket endpoints
  services/     — business logic
  schemas/      — Pydantic schemas
  main.py       — application entry point
client/
  cli.py        — terminal chat client
```

---

**CI/CD**

GitHub Actions pipeline with a self-hosted runner on VPS.

---

**Kubernetes (Minikube)**

The application is packaged as a Helm chart and deployed on Minikube as a horizontally scaled monolith — multiple FastAPI replicas behind an Nginx Ingress load balancer, sharing PostgreSQL and Redis.

```
Client ──→ Ingress ──→ Pod 1 (FastAPI)
                   ──→ Pod 2 (FastAPI)
                   ──→ Pod 3 (FastAPI)
                              ↕
                            Redis
                              ↕
                          PostgreSQL
```

Redis pub/sub synchronises state across pods — a client landing on any replica receives messages from all others.

WebSocket connections require sticky sessions (one annotation in Nginx Ingress):

yaml

```yaml
annotations:
  nginx.ingress.kubernetes.io/affinity: "cookie"
```

Helm `values.yaml` exposes `replicas`, `image.tag`, and env variables. Deploying a new version:

bash

```bash
helm upgrade pythonirc ./chart --set image.tag=v1.2
```

This gives:

- **Fault tolerance** — one pod down, two keep serving
- **Zero-downtime deploys** — rolling update, one pod at a time
- **Horizontal scaling** — `kubectl scale deployment pythonirc --replicas=5`

K8s manifests and the Helm chart are in the repository /k8s and /pythonirc-chart

---

**Development**

Pre-commit hooks with ruff (lint + format):

bash

```bash
pre-commit install
```

Run tests:

bash

```bash
pytest
```
