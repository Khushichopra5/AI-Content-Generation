# API Notes

## Base URL

All application endpoints are mounted under:

```text
/api/v1/
```

## Authentication

Primary API authentication is bearer token based.

Header format:

```text
Authorization: Bearer <token>
```

## cURL Examples

### Register

```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "Example User",
    "password": "StrongPass123!"
  }'
```

### Create a brand profile

```bash
curl -X POST http://localhost:8000/api/v1/brands/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "brand_name": "Northwind",
    "brand_voice": "Direct, confident, clear.",
    "banned_phrases": ["guaranteed profit"],
    "preferred_tone": "professional",
    "example_copy": "Move faster without sacrificing consistency.",
    "product_description": "AI content operations platform.",
    "target_audience": "B2B SaaS marketing leaders"
  }'
```

### Create a content template

```bash
curl -X POST http://localhost:8000/api/v1/templates/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lead Gen Email",
    "channel": "email",
    "objective": "lead_generation",
    "prompt_template": "Write concise, credible, conversion-focused outbound copy."
  }'
```

### Submit a generation job

```bash
curl -X POST http://localhost:8000/api/v1/generate/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

### Poll a job

```bash
curl http://localhost:8000/api/v1/jobs/<job_id>/ \
  -H "Authorization: Bearer <token>"
```

### Regenerate from an existing job

```bash
curl -X POST http://localhost:8000/api/v1/regenerate/<job_id>/ \
  -H "Authorization: Bearer <token>"
```

### List usage events

```bash
curl http://localhost:8000/api/v1/usage/ \
  -H "Authorization: Bearer <token>"
```

Token lifecycle endpoints:
- `POST /api/v1/auth/register/`
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/logout/`
- `GET /api/v1/auth/me/`
- `PATCH /api/v1/auth/me/`
- `GET /api/v1/auth/tokens/`
- `POST /api/v1/auth/tokens/`
- `POST /api/v1/auth/tokens/{id}/revoke/`

## Domain Endpoints

Brands:
- `GET /api/v1/brands/`
- `POST /api/v1/brands/`
- `GET /api/v1/brands/{id}/`
- `PATCH /api/v1/brands/{id}/`
- `DELETE /api/v1/brands/{id}/`

Templates:
- `GET /api/v1/templates/`
- `POST /api/v1/templates/`
- `GET /api/v1/templates/{id}/`
- `PATCH /api/v1/templates/{id}/`
- `DELETE /api/v1/templates/{id}/`

Generation:
- `POST /api/v1/generate/`
- `POST /api/v1/generate/image/`
- `POST /api/v1/regenerate/{job_id}/`
- `GET /api/v1/jobs/`
- `GET /api/v1/jobs/{job_id}/`

Usage:
- `GET /api/v1/usage/`

Health:
- `GET /health/`

## Generation Semantics

### Submit

`POST /api/v1/generate/` creates or reuses a job.

Possible outcomes:
- new queued job
- deduplicated reference to an already-running job
- immediate succeeded job from cache

Response shape:

```json
{
  "job_id": "uuid",
  "status": "queued",
  "cache_hit": false,
  "deduplicated": false
}
```

### Poll

`GET /api/v1/jobs/{job_id}/` returns the current job record, including:
- status
- output payload
- error message
- linked assets

### Status meanings

- `queued`
- `running`
- `succeeded`
- `failed`

## Output Contract

Successful generation output contains:
- `variants`
- `hashtags`
- `subject_lines`
- `cta_options`
- `image_prompt`
- `quality_notes`

This structure is schema-constrained and validated before persistence.

## Pagination

List endpoints use DRF page number pagination.

Typical response shape:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": []
}
```

## Error Behavior

Typical failure categories:
- `400` invalid input or moderation rejection
- `401` invalid authentication
- `403` authenticated but not allowed
- `404` resource not found
- `429` throttle exceeded
- `500` unexpected server error

Generation failures caused by upstream model issues are usually reflected in the job record rather than surfacing synchronously as a request failure.
