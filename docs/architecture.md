# Architecture

## Purpose

This document explains how the backend is structured, how requests move through the system, and where the main responsibilities live in the codebase.

The platform is designed around a simple rule: keep the synchronous API path thin, and move expensive or failure-prone work into explicit service and task layers.

## High-Level System

Core runtime components:
- Django application server
- PostgreSQL for durable state
- Redis for cache, broker, and transient coordination
- Celery workers for background execution
- OpenAI Responses API for structured text generation and image generation

High-level flow:

```text
Client
  -> Django API
  -> DRF serializer validation
  -> Generation service
  -> PostgreSQL job record
  -> transaction.on_commit()
  -> Celery task
  -> OpenAI Responses API
  -> validated output
  -> PostgreSQL + Redis cache
  -> optional image task
  -> Asset record
```

## Sequence Diagrams

### Text Generation Flow

```text
Client
  -> API view
  -> serializer validation
  -> generation service
  -> Postgres: create GenerationJob
  -> on_commit enqueue
  -> Celery worker
  -> OpenAI Responses API
  -> JSON schema validation
  -> Postgres: persist output
  -> Redis: cache result
  -> UsageEvent
```

### Image Generation Flow

```text
Completed copy job
  -> Celery image task
  -> OpenAI Responses API with image_generation tool
  -> local storage backend
  -> Asset row
  -> UsageEvent
```

### Cached Repeat Request

```text
Client
  -> API view
  -> serializer validation
  -> generation service
  -> Redis cache lookup
  -> cache hit
  -> Postgres: create succeeded GenerationJob
  -> immediate response
```

## Design Principles

- Views validate and delegate; they do not contain generation logic.
- External API responses are treated as untrusted until validated.
- Long-running work is asynchronous.
- Cached responses are keyed by a normalized prompt hash.
- Data is auditable through job and usage records.
- Failure paths should be explicit and observable.

## Project Structure

```text
apps/
  authentication/   user model, bearer tokens, auth endpoints
  brands/           brand profile CRUD
  common/           shared helpers, env parsing, middleware, throttling
  generation/       jobs, assets, serializers, services, tasks
  integrations/     OpenAI integration client
  templates/        content template CRUD
  usage/            usage event tracking

config/
  settings/         base, local, production, test settings
  celery.py         Celery app bootstrap
  urls.py           root routing
```

## Request Lifecycle

## 1. API boundary

Relevant files:
- [config/urls.py](/Users/sanskar/dev/ContentGen/config/urls.py)
- [apps/generation/views.py](/Users/sanskar/dev/ContentGen/apps/generation/views.py)
- [apps/generation/serializers.py](/Users/sanskar/dev/ContentGen/apps/generation/serializers.py)

Responsibilities:
- authenticate the caller
- validate request shape
- resolve foreign keys such as `brand_profile_id` and `template_id`
- return consistent response bodies

Views call the serializer first, then pass validated data into the service layer.

## 2. Service orchestration

Relevant file:
- [apps/generation/services.py](/Users/sanskar/dev/ContentGen/apps/generation/services.py)

The service layer is the core coordination point. It:
- builds the canonical request payload
- normalizes it
- computes a stable hash
- checks for running duplicate jobs
- checks Redis for a cached result
- creates the `GenerationJob`
- enqueues the background task with `transaction.on_commit()`

This layer exists to keep business behavior independent from HTTP transport and Celery implementation details.

## 3. Persistence model

Relevant files:
- [apps/generation/models.py](/Users/sanskar/dev/ContentGen/apps/generation/models.py)
- [apps/brands/models.py](/Users/sanskar/dev/ContentGen/apps/brands/models.py)
- [apps/templates/models.py](/Users/sanskar/dev/ContentGen/apps/templates/models.py)
- [apps/usage/models.py](/Users/sanskar/dev/ContentGen/apps/usage/models.py)

Primary entities:
- `User`
- `APIToken`
- `BrandProfile`
- `ContentTemplate`
- `GenerationJob`
- `Asset`
- `UsageEvent`

`GenerationJob` is the main operational record. It keeps:
- normalized input payload
- prompt hash
- status
- output payload
- error message
- cache hit state
- whether image generation was requested

## 4. Background execution

Relevant file:
- [apps/generation/tasks.py](/Users/sanskar/dev/ContentGen/apps/generation/tasks.py)

Celery is responsible for:
- copy generation
- image generation
- retries with backoff

Execution flow:

```text
submit job
  -> run_copy_generation_task
  -> validate structured output
  -> persist result
  -> cache result
  -> record usage
  -> optionally enqueue run_image_generation_task
```

The image task is intentionally separate so the copy path can complete without waiting on image latency.

## 5. OpenAI integration

Relevant file:
- [apps/integrations/openai_client.py](/Users/sanskar/dev/ContentGen/apps/integrations/openai_client.py)

The wrapper exposes two operations:
- structured text generation
- image generation

Text generation:
- uses the Responses API
- supplies a strict JSON schema
- parses `response.output_text`
- returns usage metadata when available

Image generation:
- uses the Responses API `image_generation` tool
- uses a text-capable model such as `gpt-5`
- extracts the base64 image payload from tool output

## 6. Output validation

Relevant files:
- [apps/generation/schemas.py](/Users/sanskar/dev/ContentGen/apps/generation/schemas.py)
- [apps/generation/services.py](/Users/sanskar/dev/ContentGen/apps/generation/services.py)

The structured response is validated twice conceptually:
- constrained at generation time through the schema passed to OpenAI
- validated again server-side before persistence

This avoids accepting malformed model output into the database or cache.

## 7. Caching and deduplication

Relevant files:
- [apps/generation/prompting.py](/Users/sanskar/dev/ContentGen/apps/generation/prompting.py)
- [apps/generation/services.py](/Users/sanskar/dev/ContentGen/apps/generation/services.py)

Caching strategy:
- normalize request payload
- hash normalized JSON
- use hash as the cache key namespace

Deduplication strategy:
- if an identical job is already `queued` or `running`, return that job instead of creating another
- if a completed result exists in Redis cache, persist a new `GenerationJob` marked as `cache_hit=true`

## 8. Asset persistence

Relevant file:
- [apps/generation/storage.py](/Users/sanskar/dev/ContentGen/apps/generation/storage.py)

Current backend:
- local filesystem under `MEDIA_ROOT`

Abstraction intent:
- keep asset persistence behind a storage boundary
- allow later replacement with S3, R2, GCS, or similar object storage

## 9. Observability

Relevant files:
- [apps/common/middleware.py](/Users/sanskar/dev/ContentGen/apps/common/middleware.py)
- [config/settings/base.py](/Users/sanskar/dev/ContentGen/config/settings/base.py)
- [apps/usage/services.py](/Users/sanskar/dev/ContentGen/apps/usage/services.py)

Current observability includes:
- request IDs
- structured console logging
- usage event records
- job status and error persistence
- health endpoint for DB and Redis

## 10. Security model

Authentication:
- session auth
- bearer API token auth

Controls:
- DRF permissions
- throttling
- request validation
- banned phrase screening in the generation service

Current limits:
- moderation is intentionally basic
- no tenant isolation beyond user ownership
- no external secrets manager integration in code

## Failure Modes

Expected failure classes:
- invalid input
- duplicate running job
- cache miss
- OpenAI request failure
- malformed OpenAI output
- image generation failure
- Redis unavailable
- database unavailable

Behavior:
- input failures stay at the API boundary
- generation failures are persisted to the job record
- Celery retries transient upstream failures
- image failures do not erase successful text output

## Why This Shape

This codebase avoids unnecessary abstraction layers. There is no agent framework in the application core, and no model logic inside views. The architecture is intentionally conservative:
- Django handles API and admin
- Celery handles background work
- Redis handles ephemeral coordination
- PostgreSQL handles source-of-truth state

That keeps the project understandable, testable, and straightforward to operate.
