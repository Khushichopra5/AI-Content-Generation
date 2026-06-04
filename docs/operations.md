# Operations Notes

## Runtime Components

Required services:
- PostgreSQL
- Redis
- Django web process
- Celery worker

Optional:
- Celery beat

## Health Checks

Application health endpoint:

```text
GET /health/
```

The response includes:
- overall status
- database connectivity
- Redis connectivity

## Startup Order

Recommended order:

1. PostgreSQL
2. Redis
3. Django migrations
4. Django web process
5. Celery worker
6. Celery beat, if used

## Important Environment Variables

- `DATABASE_URL`
- `REDIS_URL`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`
- `OPENAI_API_KEY`
- `OPENAI_TEXT_MODEL`
- `OPENAI_IMAGE_MODEL`
- `DJANGO_SECRET_KEY`
- `DJANGO_SETTINGS_MODULE`

## Operational Expectations

### Text generation

- runs in Celery
- persists structured output to `GenerationJob`
- records usage events
- writes cached results to Redis

### Image generation

- runs after successful text generation
- may take substantially longer than text generation
- creates an `Asset` row on success

## Common Failure Cases

### Jobs stay queued

Check:
- Redis broker is reachable
- Celery worker is running
- task queue name matches the worker queue

### Jobs fail with OpenAI authentication errors

Check:
- `OPENAI_API_KEY` is valid
- key has access to the required models/tools

### Image generation fails with model errors

Check:
- `OPENAI_IMAGE_MODEL` is set to a text-capable Responses API model, such as `gpt-5`
- do not set `gpt-image-1` as the top-level Responses API model in this flow

### Cache does not hit

Check:
- payloads are actually identical after normalization
- Redis cache URL is correct
- cache TTL is not too low for the test scenario

## Data Cleanup

For operational cleanup, useful targets include:
- failed `GenerationJob` rows
- unused `Asset` rows
- accumulated local media files in non-production environments

If production cleanup is needed, prefer management commands or explicit admin tasks rather than ad hoc SQL.

## Production Hardening Gaps

Current project is operational, but these are still logical next steps for production maturity:
- remote object storage backend
- formal metrics endpoint
- structured log shipping
- secrets manager integration
- backup/retention policy documentation
- finer moderation and abuse controls
