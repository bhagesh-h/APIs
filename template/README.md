# FastAPI Starter Template

This is a reusable, production-minded FastAPI starter template designed for building new API services with minimal setup.

## Why This Template
- **Automatic Docs**: FastAPI automatically provides OpenAPI docs and interactive documentation.
- **Multi-File Architecture**: Multi-file organization scales better for real production projects.
- **Docker Read**y: Docker makes the template reproducible, consistent, and easy to deploy.

## Features
- Scalable app structure
- Versioned API routing (`/api/v1`)
- Health checks and readiness endpoints
- Example CRUD routes with dependency injection
- Example API key security for protected endpoints
- Consistent, centralized error handling
- Pre-configured logging
- Docker and Docker Compose setup for local development
- Full test suite via `pytest`
- Code quality tools (`ruff`, `black`, `mypy`)
- Render deployment configuration
- Interactive docs available at `/docs` and `/redoc`

## Folder Walkthrough
- `app/`: The core application logic.
  - `core/`: Configurations, logging, and security definitions.
  - `api/v1/`: Version 1 API routers and endpoints.
  - `schemas/`: Pydantic models for input validation and output formatting.
  - `services/`: Business logic, keeping handlers thin.
  - `utils/`: Shared utilities.
- `tests/`: Pytest suite covering endpoints and business logic.
- `scripts/`: Development and CI bash scripts.
- `Dockerfile` / `docker-compose.yml`: Containerization configuration.

## Quick Start

### Create a Virtual Environment

**Linux / macOS:**
```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install Dependencies
```bash
pip install -r requirements.txt -r requirements-dev.txt
```

### Setup Configuration
```bash
cp .env.example .env
```

### Run Locally
```bash
uvicorn app.main:app --reload
```

## Available Commands

```bash
# Run tests
pytest

# Lint the codebase
ruff check .

# Format code
black .

# Type checking
mypy app
```

## Scripts Usage

Convenient bash scripts are located in `scripts/`:

```bash
# Run local dev server with auto-reload
bash scripts/dev.sh

# Run full test suite
bash scripts/test.sh

# Lint with Ruff
bash scripts/lint.sh

# Format with Black and Ruff
bash scripts/format.sh

# Run MyPy
bash scripts/typecheck.sh

# Build and run Docker locally
bash scripts/run_docker.sh
```

## Makefile Usage

You can use Make for streamlined execution if you have it installed:
- `make dev`: Run dev server.
- `make test`: Run pytest.
- `make lint`: Run ruff.
- `make format`: Run black & ruff fix.
- `make typecheck`: Run mypy.
- `make docker-build`: Build image.
- `make docker-run`: Run container.

## API Documentation

FastAPI dynamically generates the OpenAPI schema:
- **Swagger UI**: Interactive UI at `/docs`
- **ReDoc**: Static, highly readable docs at `/redoc`
- **OpenAPI Schema**: Raw JSON schema at `/api/v1/openapi.json`

## Example API Usage

**Root and Health Info**
```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/ready
```

**Sample Ping**
```bash
curl http://127.0.0.1:8000/api/v1/examples/ping
```

**Protected Endpoint**
```bash
curl -H "X-API-Key: change_this_secret_key_in_production" \
  http://127.0.0.1:8000/api/v1/examples/protected
```

**Item CRUD Flow**
```bash
# Create Item
curl -X POST http://127.0.0.1:8000/api/v1/items/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Apple", "description": "Fresh fruit"}'

# List Items
curl http://127.0.0.1:8000/api/v1/items/

# Update Item
curl -X PUT http://127.0.0.1:8000/api/v1/items/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Green Apple"}'

# Delete Item
curl -X DELETE http://127.0.0.1:8000/api/v1/items/1
```

## How to Create a New Service from the Template

To easily bootstrap a new project based on this template, you can run:

```bash
bash scripts/new_service_checklist.sh
```

**Step-by-Step:**
1. Copy the `template/` folder.
2. Rename project-specific values in `.env.example`, `pyproject.toml`, and `render.yaml`.
3. Update the app name and version in `app/core/config.py`.
4. Delete exampleroutes (`examples.py`, `items.py`) and replace them with your business-specific routes.
5. Add new internal services to `app/services/` and schemas to `app/schemas/`.
6. Update your test suite in `tests/`.
7. Adjust Dockerfile details if you have unique operating system dependencies.
8. Commit to Git.

## Deployment & Docker

Containerized deployment is standard for FastAPI applications. This template includes a slim and production-minded `Dockerfile` using the official `python:3.11-slim` image alongside layered caching best practices. 

### Local Docker

**Using standard Docker:**
```bash
docker build -t fastapi-template .
docker run -p 8000:8000 --env-file .env fastapi-template
```

**Using Docker Compose:**
```bash
docker compose up --build
```

You can then test the running container on your host machine:
```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/docs
curl http://127.0.0.1:8000/redoc
```

### Render Deployment
This template includes `render.yaml` for infrastructure-as-code deployment on Render using their native Python environments. Set your `APP_ENV` and `APP_DEBUG` variables on your Render dashboard securely.

Expected startup command used in Render configuration: 
`uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Testing and Quality

Strong test coverage and static analysis ensure a service doesn't break in production. This reusable starter provides you with the right tools preconfigured:
- Tests: Use `pytest` for unit and integration testing.
- Linting: Use `ruff` to identify structural rule violations.
- Formatting: Use `black` to keep all developers writing visually unified code.
- Typing: Use `mypy` to detect implicit runtime type errors before you ever deploy it.

## Extension Guide

You can confidently scale this setup by extending it with:
- **Databases**: Add SQLAlchemy models in an `app/models/` folder and implement database sessions in `app/api/deps.py`.
- **Authentication**: Swap the X-API-Key approach for OAuth2 with JWT tokens utilizing FastAPI's native security features.
- **Background Tasks**: Pass FastAPI's `BackgroundTasks` via dependency injection into handlers, or implement Celery for robust async messaging.
- **File Uploads**: Include `UploadFile` schemas and map mounted volumes via `docker-compose.yml` into your runtime container.

## Best Practices Checklist

When building new services, aim to adhere to the following principles:
- Keep route handlers thin. Call services.
- Keep services decoupled and reusable.
- Validate inputs rigorously with Pydantic schemas. Corrupt data must fail early.
- Document endpoint parameters explicitly for Swagger UI.
- Never commit secrets to Git. Always inject configuration via environment variables.
- Write tests for every core flow.
- Ensure health routes remain fast and do not rely on slow external resources.

---
Built with ❤️ with FastAPI.
