# PROMPT2 Backend Audit

## Reality Check

This repository is a Django backend for AI marketing content generation.

It is not currently an agent orchestration platform.

It does not contain:

- LangGraph flows
- LangChain chains
- Weaviate integration
- RAG ingestion pipelines
- document chunking/indexing
- multi-agent routing systems
- memory retrieval pipelines
- workflow traces
- tool calling registries

`PROMPT2.md` assumes a broader AI platform than the codebase actually contains. The correct implementation path for this repo is to expose the backend capabilities that do exist, while documenting the mismatch clearly.

## Repository Inventory

### Django apps

- `apps.authentication`
- `apps.brands`
- `apps.guests`
- `apps.templates`
- `apps.generation`
- `apps.usage`
- `apps.common`
- `apps.integrations`

### Core infrastructure

- Django 5.x
- DRF
- PostgreSQL
- Redis cache
- Celery task layer
- OpenAI Responses API integration
- Django admin

## Endpoint Inventory

### Public / optional-auth endpoints

- `GET /health/`
- `POST /api/v1/guest/bootstrap/`
- `POST /api/v1/auth/register/`
- `POST /api/v1/auth/login/`

### Authenticated endpoints

Authenticated here means either:

- bearer token / session auth
- guest session headers

Endpoints:

- `POST /api/v1/auth/logout/`
- `GET /api/v1/auth/me/`
- `PATCH /api/v1/auth/me/`
- `GET /api/v1/auth/tokens/`
- `POST /api/v1/auth/tokens/`
- `DELETE /api/v1/auth/tokens/{id}/`
- `POST /api/v1/auth/tokens/{id}/revoke/`
- `GET /api/v1/brands/`
- `POST /api/v1/brands/`
- `GET /api/v1/brands/{id}/`
- `PATCH /api/v1/brands/{id}/`
- `DELETE /api/v1/brands/{id}/`
- `GET /api/v1/templates/`
- `POST /api/v1/templates/`
- `GET /api/v1/templates/{id}/`
- `PATCH /api/v1/templates/{id}/`
- `DELETE /api/v1/templates/{id}/`
- `POST /api/v1/generate/`
- `POST /api/v1/generate/image/`
- `POST /api/v1/regenerate/{job_id}/`
- `GET /api/v1/jobs/`
- `GET /api/v1/jobs/{job_id}/`
- `GET /api/v1/usage/`

### Admin

- `GET /admin/`

## Data Model Inventory

### User

Purpose:

- authenticated account
- staff/admin access
- guest backing identity when `is_guest=true`

Key properties:

- email
- name
- role
- is_staff
- is_superuser
- is_guest

### GuestSession

Purpose:

- anonymous primary identity
- maps browser identity to a backing user row
- enables guest persistence across refreshes and browser restarts

Key properties:

- guest_id
- session_id
- device_id
- backing_user
- claimed_by
- status
- expires_at
- last_seen_at

### BrandProfile

Purpose:

- reusable brand context for generation

### ContentTemplate

Purpose:

- reusable channel/objective prompt template

### GenerationJob

Purpose:

- durable record of text or image generation requests

### Asset

Purpose:

- generated media attached to a job

### UsageEvent

Purpose:

- analytics/event log for generation and cache behavior

## Existing User Journeys

### Journey: Guest demo

1. Bootstrap guest session
2. Create brand
3. Create template
4. Submit generation request
5. Inspect jobs
6. Inspect usage analytics
7. Optionally convert into real account

### Journey: Authenticated user

1. Register or log in
2. Manage brands/templates
3. Run generations
4. Inspect jobs and usage
5. Manage personal API tokens

### Journey: Guest conversion

1. Guest accumulates resources under backing guest user
2. Guest registers or logs in with guest headers attached
3. Guest resources migrate to real account automatically

## Workflow Inventory

### Generation flow

1. validate brand/template/request payload
2. normalize payload
3. hash prompt
4. deduplicate queued/running jobs
5. check content cache
6. create `GenerationJob`
7. enqueue or execute text generation task
8. persist structured output
9. optionally trigger image task
10. write usage events

### Guest bootstrap flow

1. create guest ids if absent
2. create backing guest user
3. persist `GuestSession`
4. cache Redis mapping
5. return session ids and soft-limit summary

## Capability Inventory

### Present

- guest-first identity bootstrap
- content generation
- brand profile management
- template management
- job history
- cache-aware repeat requests
- usage analytics
- Django admin

### Missing relative to PROMPT2

- chat transcript system
- conversation branching
- message regeneration UI semantics
- multi-agent routing
- RAG retrieval
- document upload/index/search
- memory dashboard backed by actual memory stores
- workflow inspector with state transitions
- queue/redis/celery live console

## Route-To-Screen Mapping

See [frontend-route-mapping.md](./frontend-route-mapping.md).

## Database Impact Assessment

Changes introduced for PROMPT2:

- `authentication.User.is_guest`
- new `guests.GuestSession`

No existing content models were structurally rewritten. Guest support is implemented by attaching guest sessions to backing user rows, which preserves current foreign keys and avoids a full ownership refactor.

## Implementation Direction

The frontend should expose the real backend as a developer demo platform:

- landing page
- guest bootstrap
- generation workspace
- jobs explorer
- usage analytics
- API inspector
- admin handoff

It should not pretend to demonstrate RAG or multi-agent behavior that the backend does not implement.
