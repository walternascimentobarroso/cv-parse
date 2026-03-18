# Doc-to-Text API – Development Environment

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=walternascimentobarroso_cv-parse&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=walternascimentobarroso_cv-parse)

This repository contains a small Doc-to-Text API and an improved development environment focused on fast onboarding and simple workflows.

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package/dependency manager)
- Docker and Docker Compose

## Getting started

From the repo root:

```bash
cp .env.example .env
make install
make up
```

This installs dependencies with uv and starts the API and MongoDB. The API is available at `http://localhost:8000`.

## Makefile commands

- `make install` – Install dependencies from `pyproject.toml` / `uv.lock`
- `make up` – Start services with Docker Compose
- `make down` – Stop and remove containers
- `make logs` – Follow service logs
- `make run` – Run the app locally with uv
- `make test` – Run tests (requires local Docker access; run directly on your machine)
- `make lint` – Run Ruff
- `make typecheck` – Run Pyright inside the API container (rebuild the image after Dockerfile changes: `make recreate`)

## Environment configuration

Environment variables are defined in `.env` (not committed) with `.env.example` as the template. Both the app and Docker Compose read from `.env` so configuration is consistent.

See `specs/002-dev-env-tooling/quickstart.md` and `specs/002-dev-env-tooling/contracts/env.md` for details.

## Debug (VS Code / Cursor)

The project is set up to debug the FastAPI app and pytest tests. Follow the steps below to enable debugging later.

**In any API debug mode (local or Docker), the API stays at http://localhost:8000** — debugpy only uses port 5678 for the IDE; uvicorn keeps serving on 8000.

### 1. Prerequisites

- **Python**: Python extension (or Pylance) installed in the editor.
- **Dependencies**: environment created with `make install` (or `uv sync`).
- **MongoDB** (API debugging only): services running with `make up` so the API can reach the database.

### 2. Python interpreter

The debugger uses the project virtual environment:

1. Command palette: `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux).
2. Run **Python: Select Interpreter**.
3. Pick the project `.venv` interpreter (e.g. `./.venv/bin/python`).

If `.venv` is missing, run `make install` at the repo root and try again.

### 3. Environment variables for API debugging

When you run the **API on your machine** (via debug), it must reach MongoDB. With `make up`, MongoDB runs in Docker at `localhost:27017`.

In `.env`:

```bash
MONGODB_URI=mongodb://localhost:27017
```

That lets a locally debugged API talk to Docker MongoDB. (Inside Docker, Compose uses `mongodb:27017`; for local debug use `localhost:27017`.)

### 4. Starting a debug session

1. Open **Run and Debug** (sidebar or `Cmd+Shift+D` / `Ctrl+Shift+D`).
2. In the dropdown, pick:
   - **FastAPI (debug)** – API with debugger on your machine (best for API breakpoints).
   - **FastAPI (debug + reload)** – same, with reload on save (reload may briefly disconnect the debugger).
   - **FastAPI (attach to Docker)** – attach to the API **inside Docker** (see [Debug with API in Docker](#6-debug-with-api-in-docker)).
   - **Pytest: current file** – run/debug only the open test file.
   - **Pytest: all** – run/debug all tests under `tests/`.
3. Press **F5** (or **Start Debugging**).

### 5. Day-to-day usage

- **Breakpoints**: click the gutter (or use the context menu) to set breakpoints.
- **API**: after **FastAPI (debug)**, call `http://localhost:8000` (browser, curl, Postman, etc.); execution stops at breakpoints.
- **Tests**: open a file under `tests/`, choose **Pytest: current file** and F5; or **Pytest: all** for the full suite.

### 6. Debug with API in Docker

To debug the API **inside the container** (debugpy listen mode):

1. Set `DEBUGPY=1` in `.env` (or `export DEBUGPY=1`).
2. **Rebuild** so the image includes debugpy: `docker compose build api` (or `make recreate`).
3. Start services: `make up` (or `docker compose up -d`).
4. In the editor: **Run and Debug** → **FastAPI (attach to Docker)** → **F5**.
5. Debugger attaches on port **5678**. The API is still at **http://localhost:8000**.

The **Dockerfile** installs `debugpy` via `uv sync`. **docker-compose** exposes **5678** (debugger) and **8000** (API). With `DEBUGPY=1`, the entrypoint runs `debugpy --listen 0.0.0.0:5678` and uvicorn on 8000.

**If http://localhost:8000 does not respond** with Docker debug: check the container (`docker compose ps`, `docker compose logs api`). Rebuild if it crashes or errors on imports: `docker compose build api` and `docker compose up -d`. Ensure nothing else is bound to port 8000.

### 7. Quick recap (re-enable debug later)

**API on your machine (no Docker for the app):**

1. `make install` if needed.
2. `make up` (MongoDB only, if debugging the API).
3. `.env` with `MONGODB_URI=mongodb://localhost:27017` for local API debug.
4. **Python: Select Interpreter** → project `.venv`.
5. **Run and Debug** → **FastAPI (debug)** or **Pytest: current file** / **Pytest: all** → **F5**.

**API inside Docker:**

1. `.env`: `DEBUGPY=1`.
2. `make up`.
3. **Run and Debug** → **FastAPI (attach to Docker)** → **F5**.

