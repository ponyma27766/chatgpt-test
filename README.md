# Python Project Skeleton (Beginner-Friendly)

Lightweight, reproducible, and deployable skeleton for Ubuntu 22.04 + Docker Compose.

## Project Structure

```
.
├── docker-compose.yml
├── .env.example
├── pipeline/        # Data / ingestion artifacts
├── experiments/     # Training and evaluation notebooks/scripts
├── monitor/         # Health checks
├── scripts/         # start/stop/status/smoke_test
├── tests/           # Smoke tests
└── .github/
    └── workflows/   # CI
```

## Quick Start (Definition of Done)

### 1) One-click start

```bash
cp .env.example .env
./scripts/start.sh
```

### 2) Verify status

```bash
./scripts/status.sh
```

### 3) Run smoke test (inside container)

```bash
docker compose run --rm app
```

Expected output:

```
Smoke test passed.
```

### 4) One-click stop

```bash
./scripts/stop.sh
```

If all commands above work without errors, the skeleton is ready for D/E/F tasks.

## Notes

- The smoke test ensures required directories exist and checks the basic layout.
- The container uses the official `python:3.11-slim` image with the repo mounted at `/app`.
