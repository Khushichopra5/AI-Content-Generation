# Data Model

## Purpose

This document explains the persistent entities in the system, their responsibilities, and how they relate to each other.

## Entity Overview

Primary models:
- `User`
- `APIToken`
- `BrandProfile`
- `ContentTemplate`
- `GenerationJob`
- `Asset`
- `UsageEvent`

## User

Defined in:
- [apps/authentication/models.py](../apps/authentication/models.py)

Role:
- top-level owner for user-scoped records
- authentication subject
- administrative boundary for API and admin visibility

Important fields:
- `id`
- `email`
- `name`
- `role`
- `created_at`
- `updated_at`

Notes:
- email is the login identifier
- the project uses a custom user model

## APIToken

Defined in:
- [apps/authentication/models.py](../apps/authentication/models.py)

Role:
- bearer token for API access

Important fields:
- `user`
- `name`
- `prefix`
- `key_digest`
- `last_used_at`
- `expires_at`
- `revoked_at`

Notes:
- raw token values are not stored directly
- lookups are performed via SHA-256 digest
- revoked or expired tokens are considered inactive

## BrandProfile

Defined in:
- [apps/brands/models.py](../apps/brands/models.py)

Role:
- source-of-truth brand context for generation

Important fields:
- `user`
- `brand_name`
- `brand_voice`
- `banned_phrases`
- `preferred_tone`
- `example_copy`
- `product_description`
- `target_audience`

Notes:
- owned by a single user
- used to build the generation context block
- influences hashing because brand content affects output

## ContentTemplate

Defined in:
- [apps/templates/models.py](../apps/templates/models.py)

Role:
- reusable prompt framing for common content patterns

Important fields:
- `user`
- `name`
- `channel`
- `objective`
- `prompt_template`

Notes:
- optional during generation
- included in prompt hashing when supplied

## GenerationJob

Defined in:
- [apps/generation/models.py](../apps/generation/models.py)

Role:
- main execution and audit record for each generation request

Important fields:
- `user`
- `brand_profile`
- `template`
- `input_payload`
- `prompt_hash`
- `status`
- `model_name`
- `output_payload`
- `error_message`
- `cache_hit`
- `include_image`
- `moderation_notes`
- `completed_at`

Status values:
- `queued`
- `running`
- `succeeded`
- `failed`

Notes:
- this is the primary unit of job history
- repeated cached requests still create a new `GenerationJob`
- image generation is attached to the same job

## Asset

Defined in:
- [apps/generation/models.py](../apps/generation/models.py)

Role:
- persisted output artifact linked to a generation job

Important fields:
- `generation_job`
- `asset_type`
- `storage_url`
- `mime_type`
- `metadata`

Current asset usage:
- generated image outputs

Notes:
- current storage backend is local media storage
- metadata stores provider response details and revised prompt context

## UsageEvent

Defined in:
- [apps/usage/models.py](../apps/usage/models.py)

Role:
- lightweight operational telemetry persisted in the database

Important fields:
- `user`
- `event_type`
- `tokens_in`
- `tokens_out`
- `latency_ms`
- `cache_hit`
- `metadata`

Current event examples:
- `cache_hit`
- `cache_miss`
- `generate_text`
- `generate_image`

## Relationships

```text
User
  -> APIToken
  -> BrandProfile
  -> ContentTemplate
  -> GenerationJob
  -> UsageEvent

GenerationJob
  -> BrandProfile
  -> ContentTemplate (optional)
  -> Asset
```

## Ownership Rules

- users can only access their own brands, templates, jobs, tokens, and usage rows
- admin users can view broader data through admin and queryset branches
- assets inherit access rules from their parent job

## Lifecycle Notes

### GenerationJob lifecycle

```text
queued
  -> running
  -> succeeded
or
queued/running
  -> failed
```

### Cache lifecycle

- request arrives
- normalized payload is hashed
- Redis cache is checked
- if cache hit exists, a succeeded job is created immediately

### Image lifecycle

- text generation succeeds
- image task is enqueued if requested
- asset row is created on success

## Schema Evolution Guidance

If the model layer changes:
- keep migrations explicit
- avoid storing opaque logic-critical blobs without structure
- preserve compatibility for job history where possible
- consider how new fields affect prompt hashing and cache semantics
