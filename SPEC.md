# AI-Powered Marketing Content Generator — Specification

## 1. Product overview

Build a production-grade AI content generation platform for marketing teams that can create:
- social posts
- ad copy
- email copy
- landing page copy
- campaign variations
- AI-generated supporting images

The system should support brand-aware generation, sentiment/tone control, fast reuse via caching, and asynchronous media generation so the user does not wait on long-running tasks.

## 2. Recommended stack

### Backend
- Python 3.12+
- Django
- Django REST Framework

### AI layer
- OpenAI Responses API for all text generation and tool-using flows
- Structured Outputs / JSON schema for deterministic payloads
- OpenAI image generation for image assets when needed

### Async and performance
- Redis as cache and task broker
- Celery workers for background generation jobs
- Django cache backend backed by Redis for hot prompt/result caching

### Storage
- PostgreSQL for durable relational data
- Object storage for generated images and exported assets

### Frontend
- React / Next.js if a separate frontend is needed
- Server-rendered Django admin can be used for internal operations

## 3. Why this stack

Use the OpenAI Responses API as the main model interface because it supports text and image inputs, text outputs, stateful interactions, function calling, and structured outputs in a single flow. Structured Outputs are the safer choice when the app must return machine-readable JSON. citeturn952495search20turn952495search2turn952495search11

Use Django REST Framework for the API surface because it is a mature toolkit for building web APIs, with built-in authentication, permissions, and throttling support. citeturn952495search6turn952495search21turn952495search0

Use Redis for low-latency caching and as a broker for background tasks. Redis is commonly used for cache and queue-style workloads, and Redis docs explicitly describe cache and event-driven / streaming use cases. citeturn297857search10turn297857search22turn297857search6

Use Celery for background jobs because it is a dedicated task queue with retries and multiple workers, which fits image generation, bulk campaign generation, and export jobs. Django’s `transaction.on_commit()` is ideal for kicking off tasks only after a DB write succeeds. citeturn952495search7turn952495search1turn952495search5

LangChain can be used selectively for prompt/tool abstractions or evaluation, but the core production path should stay direct and explicit unless a later phase truly needs agent orchestration. LangChain positions itself as an agent engineering platform, but this project does not need extra abstraction on day one. citeturn297857search3turn297857search11turn297857search7

## 4. Product goals

### Primary goals
1. Generate brand-consistent marketing copy from a brief.
2. Allow users to pick tone, channel, audience, and objective.
3. Produce multiple variants with quality differences.
4. Generate supporting images or visual concepts asynchronously.
5. Cache repeated requests to reduce latency and cost.
6. Track every generation request, result, and usage event.

### Secondary goals
1. Build a review/edit/retry workflow.
2. Support templates for common marketing use cases.
3. Provide a reusable prompt library.
4. Expose admin analytics for generation volume and cache hit rate.

## 5. Non-goals for v1

- Multi-tenant enterprise SSO
- Live collaborative editing
- Full CRM integrations
- Multi-model orchestration across many providers
- Complex fine-tuning pipelines

## 6. Core user flows

### Flow A: Generate copy from a brief
1. User submits product, audience, tone, channel, and goal.
2. API validates the request.
3. System checks cache using a normalized prompt hash.
4. If cache miss, the request is stored and a generation job is queued.
5. Worker calls OpenAI Responses API.
6. Model returns structured JSON with headlines, copy variants, CTAs, and rationale.
7. Results are stored and returned to the user.

### Flow B: Generate image asset
1. User chooses “generate image”.
2. Copy generation completes immediately or first.
3. Image job runs asynchronously in Celery.
4. Generated image URL is stored once uploaded to object storage.
5. UI shows generation status and the final asset.

### Flow C: Regenerate with edits
1. User edits brand brief, tone, or length.
2. System computes a fresh prompt fingerprint.
3. New version is created while prior versions stay visible.

## 7. Functional requirements

### Content generation
- Generate text for social, ad, email, blog intro, and landing page sections
- Support tone controls such as professional, playful, premium, urgent, friendly, and empathetic
- Support length controls such as short, medium, and long
- Support audience targeting and objective targeting
- Return multiple variants per request
- Return reasoning fields only as internal metadata, not as user-visible chain-of-thought

### Brand safety and quality
- Respect brand voice rules
- Block disallowed or unsafe content
- Detect missing inputs and ask for clarification only when necessary
- Reject malformed generation requests early

### Media generation
- Create image prompts from campaign context
- Generate image assets asynchronously
- Store asset metadata and generation status
- Support retry on temporary failures

### System features
- Authentication
- Rate limiting / throttling
- Request history
- Version history
- Admin dashboard
- Observability with logs and metrics
- Cache hit tracking

## 8. Data model

### User
- id
- email
- name
- role
- created_at

### BrandProfile
- id
- user_id
- brand_name
- brand_voice
- banned_phrases
- preferred_tone
- example_copy
- product_description
- target_audience
- created_at
- updated_at

### ContentTemplate
- id
- user_id
- name
- channel
- objective
- prompt_template
- created_at

### GenerationJob
- id
- user_id
- brand_profile_id
- template_id nullable
- input_payload jsonb
- prompt_hash
- status: queued | running | succeeded | failed
- model_name
- output_payload jsonb
- error_message
- cache_hit boolean
- created_at
- updated_at

### Asset
- id
- generation_job_id
- asset_type: image | export
- storage_url
- mime_type
- metadata jsonb
- created_at

### UsageEvent
- id
- user_id
- event_type
- tokens_in
- tokens_out
- latency_ms
- cache_hit
- created_at

## 9. API design

### Authentication
- Session auth for internal admin
- Token auth or JWT for public API clients

### Endpoints
- `POST /api/v1/generate/`
- `POST /api/v1/generate/image/`
- `POST /api/v1/regenerate/{job_id}/`
- `GET /api/v1/jobs/{job_id}/`
- `GET /api/v1/jobs/`
- `GET /api/v1/templates/`
- `POST /api/v1/templates/`
- `GET /api/v1/brands/`
- `POST /api/v1/brands/`
- `GET /api/v1/usage/`

### Example request payload
```json
{
  "brand_profile_id": "uuid",
  "channel": "linkedin",
  "objective": "lead_generation",
  "tone": "professional",
  "audience": "startup founders",
  "product_description": "AI assistant for sales teams",
  "key_points": ["faster outreach", "better personalization"],
  "cta": "Book a demo",
  "output_count": 3,
  "include_image": true
}
```

### Example response payload
```json
{
  "job_id": "uuid",
  "status": "queued",
  "cache_hit": false
}
```

### Job result payload
```json
{
  "job_id": "uuid",
  "status": "succeeded",
  "results": [
    {
      "variant_id": "v1",
      "headline": "...",
      "body": "...",
      "cta": "...",
      "tone_score": 0.91
    }
  ],
  "image_url": "https://..."
}
```

## 10. AI behavior contract

The system prompt should enforce:
- strong brand alignment
- concise outputs when requested
- factual caution when the user provides uncertain claims
- no invented product features
- no unsafe or deceptive marketing claims
- JSON-only output when the API requests structured responses

The model should produce a stable schema such as:
- `variants`
- `primary_copy`
- `alt_copy`
- `hashtags`
- `subject_lines`
- `cta_options`
- `image_prompt`
- `quality_notes`

## 11. Caching strategy

Cache keys should be derived from:
- normalized user brief
- brand profile version
- template version
- model name
- output format
- generation parameters

Use Redis for:
- short-lived request caching
- job status caching
- rate limit counters
- deduplication of repeated requests

## 12. Async workflow

Recommended pattern:
1. API writes GenerationJob.
2. Use `transaction.on_commit()` to enqueue Celery job only after persistence succeeds.
3. Worker processes generation.
4. Worker updates job status and stores output.
5. Optional follow-up worker handles image generation and exports.

## 13. Reliability and safety

- Validate schema at API boundary
- Use retries with backoff for model and storage failures
- Add circuit breakers for external API failures
- Never trust raw model text without validation
- Keep audit logs for generation and moderation events

## 14. Observability

Track:
- request latency
- model latency
- cache hit ratio
- generation success rate
- worker retry count
- image generation failures
- token usage

## 15. Testing strategy

- Unit tests for prompt normalization and schema validation
- API tests for all endpoints
- Celery task tests
- Integration tests for OpenAI call wrappers
- Cache and rate limit tests
- Smoke tests for deployment

## 16. Deployment targets

Minimum production shape:
- Django app container
- Celery worker container
- Celery beat container if scheduling is needed
- Redis
- PostgreSQL
- Object storage
- Reverse proxy

## 17. Acceptance criteria

- A user can submit a brief and get multiple variants back
- Cached repeated requests return quickly
- Image generation runs asynchronously
- Job history is visible
- API rejects invalid payloads cleanly
- System is testable and deployable from a fresh repo
