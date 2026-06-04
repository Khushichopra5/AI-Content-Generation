# Deployment

## Purpose

This document outlines the intended deployment shape and the minimum requirements for running the service in a stable environment.

## Deployment Shape

Minimum recommended components:
- web application container
- Celery worker container
- PostgreSQL database
- Redis instance
- reverse proxy or ingress

Optional:
- Celery beat
- remote object storage
- centralized logs/metrics

## Container Artifacts

Primary files:
- [Dockerfile](../Dockerfile)
- [docker-compose.yml](../docker-compose.yml)
- [render.yaml](../render.yaml)
- [scripts/entrypoint.sh](../scripts/entrypoint.sh)
- [scripts/start-web.sh](../scripts/start-web.sh)
- [scripts/start-worker.sh](../scripts/start-worker.sh)
- [scripts/start-beat.sh](../scripts/start-beat.sh)

## Required Environment Variables

- `DJANGO_SECRET_KEY`
- `DATABASE_URL`
- `REDIS_URL`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`
- `OPENAI_API_KEY`

Usually also set:
- `DJANGO_SETTINGS_MODULE`
- `OPENAI_TEXT_MODEL`
- `OPENAI_IMAGE_MODEL`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`

## Startup Checklist

1. Provision PostgreSQL.
2. Provision Redis.
3. Set environment variables.
4. Run migrations.
5. Start web process.
6. Start worker process.
7. Confirm `/health/` is healthy.

## Deployment Verification

Basic post-deploy checks:

```bash
curl https://your-host/health/
```

Then verify:
- auth endpoint works
- job submission works
- worker consumes tasks
- generation succeeds
- image asset record is created when requested

## Production Concerns

### Database

- use managed PostgreSQL where possible
- ensure backups and restore procedures exist
- monitor connection count and long-running queries

### Redis

- use a persistent or managed instance appropriate for broker/cache needs
- protect against accidental public exposure

### Secrets

- do not store secrets in the repository
- use environment variables or a secrets manager

### Media storage

Current implementation uses local disk abstraction.

For production, strongly consider:
- S3
- Cloudflare R2
- GCS

### Concurrency

Tune separately for:
- web workers
- Celery worker count
- Celery pool type

### Logging

Current logging is console-based.

For production, consider:
- structured JSON logs
- centralized aggregation
- error alerting

## Rollback Strategy

If a deploy fails:
- stop routing traffic to the new app version
- revert application image/code
- only roll back migrations if they were designed to be reversible and you understand the data impact

## Current Gaps Before Higher-Confidence Production Use

- remote object storage backend
- formal metrics endpoint
- stronger moderation/abuse controls
- more explicit operational alerting
