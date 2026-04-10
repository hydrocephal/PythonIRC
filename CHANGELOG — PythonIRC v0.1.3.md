****Changelog**

**[0.1.3] — 2026-04-10**

*2026-04-10*

- Replaced `python-jose` with `PyJWT`, patched related CVEs
- Added Kubernetes manifests (Deployment, Service, Ingress, ConfigMap, Secret)
- Added Helm chart with configurable `replicas`, `image.tag`, env via `values.yaml`
- Deployed on Minikube as horizontally scaled monolith (3 FastAPI replicas + Redis pub/sub + Nginx Ingress with sticky sessions)

*2026-04-08*

- Added Dockerfile + Docker Compose for full app containerisation
- Added `entrypoint.sh` for VPS deployment
- Migrated from `pip` to `uv`
- CI/CD pipeline via GitHub Actions with self-hosted runner
- Integrated Sentry for error tracking
- Integrated Prometheus + Grafana for metrics
- Fixed Alembic migrations

*2026-04-05*

- Integrated Redis for multi-worker shared state (pub/sub + Redis Set)
- Added `fakeredis` + `unittest.mock` for test isolation

*2026-04-02*

- Migrated from SQLite to PostgreSQL + asyncpg
- Added Alembic for migrations
- Fixed unit and integration tests for async stack
- Added `ruff` + `pre-commit` hooks (lint + format)
- Refreshed dependencies, fixed CI issues

*2026-03-20*

- Added `ruff` linting
- Added unit + integration test suite

*2026-03-17*

- patch: 6 bug fixes, auth unit tests
