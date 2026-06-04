# AI-Powered Marketing Content Generator

Production-oriented Django backend for generating brand-aware marketing content and async image assets with OpenAI, PostgreSQL, Redis, and Celery.

This repository implements the backend described in `PROMPT.md`, `SPEC.md`, and `CHECKLIST.md`:
- brand profile management
- reusable content templates
- structured AI copy generation
- async image generation
- request history and job tracking
- Redis-backed caching and deduplication
- admin visibility
- test coverage and Docker-based local development

## Documentation

Extended project documentation lives in [docs/README.md](docs/README.md).

Useful starting points:
- [docs/architecture.md](docs/architecture.md)
- [docs/api.md](docs/api.md)
- [docs/data-model.md](docs/data-model.md)
- [docs/operations.md](docs/operations.md)

## Overview

The system accepts a marketing brief, validates it through DRF serializers, hashes a normalized request payload, checks Redis for prior results, persists a `GenerationJob`, and pushes long-running work to Celery. Text generation uses the OpenAI Responses API with a strict JSON schema. Image generation runs asynchronously after copy generation succeeds.

Core guarantees:
- generation logic is isolated in a service layer
- model output is validated before being trusted
- async work is queued with `transaction.on_commit()`
- repeated prompts can reuse cached results
- job history is queryable through the API

## Feature Set

- Custom email-based user model with bearer API tokens
- Auth endpoints for register, login, logout, profile, token create, token revoke
- Brand profile CRUD
- Content template CRUD
- Generation job submission and status tracking
- Regeneration endpoint
- Usage event tracking
- Redis-backed content cache and status cache
- Celery retry/backoff for model failures
- Async image generation and persisted asset metadata
- Django admin registrations with useful filters/search
- Health endpoint with DB and Redis checks

## Stack

- Python 3.12+
- Django 5
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- OpenAI Responses API
- JSON Schema validation
- pytest
- Docker Compose

## Repository Layout

```text
.
├── apps/
│   ├── authentication/
│   ├── brands/
│   ├── common/
│   ├── generation/
│   ├── integrations/
│   ├── templates/
│   └── usage/
├── config/
│   ├── settings/
│   ├── celery.py
│   ├── urls.py
│   └── wsgi.py
├── scripts/
├── tests/
├── docker-compose.yml
├── Dockerfile
├── manage.py
└── pyproject.toml
```

## Architecture

### Request Flow

1. Client submits a generation request.
2. DRF serializer validates the payload.
3. The service layer normalizes the request and computes a prompt hash.
4. Redis is checked for a cached result.
5. If there is no cache hit, a `GenerationJob` is created in PostgreSQL.
6. `transaction.on_commit()` enqueues the Celery task.
7. Worker calls OpenAI Responses API for structured text output.
8. Validated JSON output is stored on the job and cached.
9. If `include_image=true`, a follow-up image task runs asynchronously.
10. Job status and assets are available through the API.

### Main Components

- `apps/generation/services.py`
  - orchestration logic for submission, caching, prompt building, and validation
- `apps/integrations/openai_client.py`
  - OpenAI client wrapper for structured text and image tool calls
- `apps/generation/tasks.py`
  - Celery tasks for copy and image generation
- `apps/generation/models.py`
  - `GenerationJob` and `Asset`
- `apps/usage/models.py`
  - audit-style usage tracking

## API Surface

Base path: `/api/v1/`

### Authentication

- `POST /auth/register/`
- `POST /auth/login/`
- `POST /auth/logout/`
- `GET /auth/me/`
- `PATCH /auth/me/`
- `GET /auth/tokens/`
- `POST /auth/tokens/`
- `POST /auth/tokens/{id}/revoke/`

### Brands

- `GET /brands/`
- `POST /brands/`
- `GET /brands/{id}/`
- `PATCH /brands/{id}/`
- `DELETE /brands/{id}/`

### Templates

- `GET /templates/`
- `POST /templates/`
- `GET /templates/{id}/`
- `PATCH /templates/{id}/`
- `DELETE /templates/{id}/`

### Generation

- `POST /generate/`
- `POST /generate/image/`
- `POST /regenerate/{job_id}/`
- `GET /jobs/`
- `GET /jobs/{job_id}/`

### Usage

- `GET /usage/`

### Health

- `GET /health/`

## Example Generation Request

```json
{
  "brand_profile_id": "uuid",
  "template_id": "uuid",
  "channel": "email",
  "objective": "lead_generation",
  "tone": "professional",
  "audience": "VPs of marketing at B2B SaaS companies",
  "product_description": "AI-powered content operations platform for marketing teams.",
  "key_points": [
    "brand-aware content generation",
    "async image generation",
    "cache repeated briefs"
  ],
  "cta": "Book a demo",
  "output_count": 1,
  "include_image": true,
  "length": "medium"
}
```

## Example Job Response

```json
{
  "job_id": "uuid",
  "status": "queued",
  "cache_hit": false,
  "deduplicated": false
}
```

## Environment

Start from `.env.example`.

Important variables:
- `DJANGO_SETTINGS_MODULE`
- `DJANGO_SECRET_KEY`
- `DATABASE_URL`
- `REDIS_URL`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`
- `OPENAI_API_KEY`
- `OPENAI_TEXT_MODEL`
- `OPENAI_IMAGE_MODEL`

Notes:
- default local settings module is `config.settings.local`
- the image generation path uses a text-capable Responses API model such as `gpt-5` with the hosted `image_generation` tool
- `gpt-image-1` should not be used as the top-level `model` field for the Responses API image tool flow

## Local Development

### Option 1: Docker Compose

1. Create your env file:

```bash
cp .env.example .env
```

2. Fill in real secrets.

3. Start the stack:

```bash
docker compose up --build
```

4. Verify health:

```bash
curl http://localhost:8000/health/
```

Default services:
- `web`
- `worker`
- `beat`
- `db`
- `redis`

### Option 2: Local Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

In a second terminal:

```bash
source .venv/bin/activate
celery -A config.celery:app worker --loglevel info
```

If you want scheduled tasks too:

```bash
source .venv/bin/activate
celery -A config.celery:app beat --loglevel info
```

## Common Commands

Run tests:

```bash
pytest
```

Run migrations:

```bash
python manage.py migrate
```

Create a superuser:

```bash
python manage.py createsuperuser
```

Run Docker-based tests:

```bash
docker compose run --rm web pytest
```

## Testing

Current automated coverage includes:
- prompt normalization and hashing
- auth/token API flow
- brand/template CRUD
- generation submission
- deduplication and cache behavior
- Celery-backed generation flow
- usage endpoint behavior

Run the full suite with:

```bash
pytest
```

## Admin

Django admin is enabled and includes registrations for:
- users
- API tokens
- brand profiles
- content templates
- generation jobs
- assets
- usage events

This is intended for internal operational visibility, debugging, and light moderation/review workflows.

## Operational Notes

- Health check confirms both database and Redis connectivity.
- Celery tasks use retry/backoff on transient OpenAI failures.
- Request IDs are attached through middleware.
- API throttling is enabled through DRF throttle classes.
- Source is environment-driven and suitable for containerized deployment.

## Current Limitation

Generated images are persisted through a local media storage backend abstraction. The abstraction exists, but a remote object storage backend such as S3, R2, or GCS is not implemented yet.

That means:
- local and containerized development work correctly
- metadata and asset records are persisted
- production-grade remote media storage still needs a backend implementation

## Troubleshooting

If startup fails, check:
- `.env` exists and contains valid secrets
- `DATABASE_URL` is reachable
- Redis is reachable
- `DJANGO_SETTINGS_MODULE` matches the actual settings path
- `OPENAI_API_KEY` is valid

If image generation fails, check:
- `OPENAI_IMAGE_MODEL` is a text-capable Responses API model such as `gpt-5`
- you are not setting `gpt-image-1` as the top-level Responses API model

If jobs stay queued, check:
- Celery worker is running
- Redis broker URL is correct
- `transaction.on_commit()` is not being bypassed by your local test harness

## GitHub Push Checklist

Before pushing:
- keep real secrets only in `.env`, never in the repository
- confirm `.gitignore` is respected
- do not commit generated media, virtualenvs, caches, or SQLite files

The repository has already been cleaned for GitHub-safe publication:
- no real OpenAI key in tracked files
- no real Neon connection string in tracked files
- no local runtime artifacts in the working tree
