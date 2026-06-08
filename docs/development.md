# Development

## Purpose

This document captures day-to-day development conventions for contributors working on the backend and the guest-first frontend.

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

Start a worker in another terminal:

```bash
source .venv/bin/activate
celery -A config.celery:app worker --loglevel info
```

## Frontend Setup

The guest-first frontend lives in `frontend/`.

```bash
cd frontend
npm install
npm run dev
```

Useful environment variable:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Where To Put Code

Use these rules:

- HTTP validation and response formatting:
  - app `views.py` and `serializers.py`
- domain logic:
  - service layer
- external API wrappers:
  - `apps/integrations/`
- async execution:
  - Celery tasks
- shared cross-app helpers:
  - `apps/common/`

## Development Conventions

- keep views thin
- avoid placing business logic in serializers when a service is clearer
- validate model output before persistence
- prefer explicit behavior over hidden magic
- keep async boundaries obvious

## Generation Path Guidance

If you change generation behavior:
- update prompt construction carefully
- consider whether hashing inputs changed
- consider cache invalidation impact
- update the JSON schema if the output contract changes
- add tests for both success and failure branches

## Model Change Guidance

If you update models:
- add migrations immediately
- think through admin display/search impact
- think through queryset ownership and permissions

## API Change Guidance

If you change endpoints:
- update serializers
- update tests
- update [docs/api.md](api.md)
- update README examples if the request/response contract changed

## Environment Discipline

- keep real secrets only in `.env`
- do not commit local runtime artifacts
- keep `.env.example` generic and safe to publish

## Suggested Dev Workflow

1. make the code change
2. run targeted tests
3. run full `pytest`
4. run `python manage.py check`
5. if relevant, test the real async path with Redis and Celery

## Common Local Debug Targets

- `/health/`
- `/api/v1/auth/*`
- `/api/v1/guest/bootstrap/`
- `/api/v1/generate/`
- `/api/v1/jobs/{id}/`
- Django admin
- Next.js `/workspace`
- Next.js `/jobs/[jobId]`

## Documentation Discipline

When you materially change architecture or behavior, update:
- [README.md](../README.md)
- [docs/architecture.md](architecture.md)
- [docs/api.md](api.md)
- [docs/frontend-architecture.md](frontend-architecture.md)
- tests
