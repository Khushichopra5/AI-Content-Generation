# Testing

## Purpose

This document describes how the project is tested, what is currently covered, and how to verify the system locally.

## Test Stack

- `pytest`
- `pytest-django`
- Django test database
- DRF test client

Configured in:
- [pytest.ini](../pytest.ini)

## Current Coverage Areas

Automated tests currently cover:
- prompt normalization and hashing
- auth registration/login/token flow
- bearer token behavior
- brand and template CRUD
- generation submission
- queue/dedup behavior
- cached response behavior
- usage endpoint behavior

Relevant test files:
- [tests/test_prompting.py](../tests/test_prompting.py)
- [tests/test_auth_api.py](../tests/test_auth_api.py)
- [tests/test_domain_and_generation_api.py](../tests/test_domain_and_generation_api.py)

## Run Tests

Local:

```bash
pytest
```

Docker:

```bash
docker compose run --rm web pytest
```

## Test Strategy

### Unit-style coverage

Used for:
- hash normalization behavior
- serializer and small service logic

### API coverage

Used for:
- auth endpoints
- CRUD endpoints
- generation submission semantics
- pagination-driven list responses

### Task-path coverage

Used for:
- Celery-backed copy generation logic
- image follow-up logic
- usage event recording

The tests intentionally stub OpenAI calls for deterministic local behavior.

## Live Verification

Automated tests are necessary but not sufficient for this project because the core path depends on:
- PostgreSQL
- Redis
- Celery
- OpenAI

When validating a full environment, verify:
1. `python manage.py check`
2. migrations apply cleanly
3. `/health/` reports database and Redis as healthy
4. a generation request reaches `succeeded`
5. repeated identical request returns a cache hit
6. image task creates an `Asset`

## Known Test Limitations

- tests do not use a live OpenAI API call by default
- tests do not require a live Redis server because cache/task behavior is partially simulated
- tests do not validate remote object storage behavior

## Recommended Next Coverage

High-value future additions:
- moderation rejection cases
- serializer edge cases around optional template usage
- failure-path assertions for malformed model responses
- end-to-end smoke command or management command
- admin integration tests
