# Build Checklist

## Phase 0 — Repo bootstrap
- [ ] Create Django project layout
- [ ] Add dependency management
- [ ] Add Docker and Docker Compose
- [ ] Add `.env.example`
- [ ] Add health endpoint
- [ ] Add README

## Phase 1 — Core data model
- [ ] Create User/auth layer
- [ ] Create BrandProfile model
- [ ] Create ContentTemplate model
- [ ] Create GenerationJob model
- [ ] Create Asset model
- [ ] Create UsageEvent model
- [ ] Run migrations

## Phase 2 — API foundation
- [ ] Add DRF
- [ ] Add serializers
- [ ] Add viewsets / API views
- [ ] Add authentication
- [ ] Add permissions
- [ ] Add throttling

## Phase 3 — Generation engine
- [ ] Build prompt normalization and hashing
- [ ] Build OpenAI Responses API wrapper
- [ ] Define structured output schema
- [ ] Implement text generation service
- [ ] Implement image generation service
- [ ] Add output validation

## Phase 4 — Async pipeline
- [ ] Configure Redis broker
- [ ] Configure Celery worker
- [ ] Enqueue jobs after DB commit
- [ ] Add retries / backoff
- [ ] Store job state transitions
- [ ] Store generated assets

## Phase 5 — Caching and performance
- [ ] Add Redis caching for repeated prompts
- [ ] Add status cache
- [ ] Add rate counter keys
- [ ] Add deduplication for identical jobs
- [ ] Add latency / token metrics

## Phase 6 — UX and admin
- [ ] Add job history endpoints
- [ ] Add template CRUD
- [ ] Register models in Django admin
- [ ] Add useful admin filters/search
- [ ] Add demo fixtures if needed

## Phase 7 — Safety and reliability
- [ ] Validate all request payloads
- [ ] Guard against malformed model output
- [ ] Add retry/error handling
- [ ] Add request logging
- [ ] Add basic moderation/safety checks
- [ ] Add idempotency support where practical

## Phase 8 — Testing
- [ ] Unit tests for hashing and validation
- [ ] Unit tests for OpenAI wrapper
- [ ] API tests for CRUD endpoints
- [ ] API tests for generation flow
- [ ] Celery task tests
- [ ] Cache hit/miss tests
- [ ] Throttling tests

## Phase 9 — Deployment readiness
- [ ] Add production settings split
- [ ] Add environment variable validation
- [ ] Add static/media handling
- [ ] Add container health checks
- [ ] Add startup docs
- [ ] Verify `docker compose up` works end-to-end

## Done when
- [ ] A user can create a brand profile
- [ ] A user can submit a brief
- [ ] The system creates a queued job
- [ ] The worker generates validated JSON output
- [ ] Cached requests return faster
- [ ] Image generation runs asynchronously
- [ ] The project is ready for iteration
