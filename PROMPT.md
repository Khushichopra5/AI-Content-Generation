You are Codex. Build this project from scratch as a production-quality monorepo.

Project: AI-Powered Marketing Content Generator

Goal:
Create a Django-based backend that accepts marketing briefs and generates brand-aware content variants using the OpenAI Responses API, with Redis-backed caching and Celery background jobs for async text/image generation.

Use this stack unless a file already exists that strongly contradicts it:
- Python 3.12+
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- OpenAI Responses API
- OpenAI Structured Outputs / JSON schema
- Object storage abstraction for generated images
- pytest for tests

Important product requirements:
- Generate copy for social posts, ads, email, landing page sections, and campaign variants.
- Support tone, audience, channel, objective, length, CTA, and brand profile inputs.
- Return multiple variants per request.
- Support asynchronous image generation.
- Cache repeated requests using a normalized prompt hash.
- Keep request history, job status, and generated asset metadata.
- Implement auth, throttling, logs, and basic admin visibility.
- Keep the system simple and reliable; avoid unnecessary agent frameworks in the core path.

Architecture rules:
1. Put the generation logic behind a single service layer, not directly in views.
2. Use DRF serializers for validation.
3. Use Celery for any task that can take more than a few hundred milliseconds.
4. Use `transaction.on_commit()` before enqueueing jobs.
5. Use Redis for cache, rate counters, and queue broker.
6. Use OpenAI Responses API for model calls.
7. Use Structured Outputs so the model returns strict JSON.
8. Treat model output as untrusted until validated.
9. Add retry logic with exponential backoff for transient model/storage errors.
10. Add tests for every important branch.

Deliverables:
- Working backend project.
- Clean repository structure.
- Docker support.
- Env template.
- API docs or a concise OpenAPI-friendly design.
- Migrations.
- Tests.
- Seed/demo fixtures if useful.

Suggested repo structure:
- `config/`
- `apps/authentication/`
- `apps/brands/`
- `apps/generation/`
- `apps/templates/`
- `apps/usage/`
- `apps/common/`
- `apps/integrations/openai_client.py`
- `apps/tasks/`
- `tests/`

Implement these features first:
1. Project setup, settings, URLs, health check.
2. Authentication.
3. Brand profile CRUD.
4. Content template CRUD.
5. GenerationJob model and API.
6. OpenAI service wrapper.
7. Celery task for copy generation.
8. Redis cache layer.
9. Image generation task.
10. Job status endpoint.
11. Rate limiting / throttling.
12. Admin-friendly model registration.
13. Tests and Docker setup.

For the model contract:
- Input: brand profile, channel, objective, tone, audience, product description, key points, CTA, output count, include_image flag.
- Output: JSON with `variants`, `hashtags`, `subject_lines`, `cta_options`, `image_prompt`, and `quality_notes`.
- The schema must be enforced by validation.
- Do not expose internal chain-of-thought.

Coding standards:
- Write readable, production-grade code.
- Add comments only where they clarify non-obvious logic.
- Prefer small, testable functions.
- Keep dependencies minimal.
- Use type hints where reasonable.
- Include error handling around external calls.
- Make APIs idempotent where practical.
- Ensure responses are consistent and predictable.

Operational requirements:
- Use settings driven by environment variables.
- Support local development with Docker Compose.
- Include a README with setup steps.
- Include a `.env.example`.
- Add `pytest.ini` or equivalent.
- Add basic logging configuration.
- Add simple health endpoint and DB/Redis connectivity checks.

Acceptance criteria:
- `docker compose up` starts the app, Redis, PostgreSQL, and worker stack.
- Migrations run cleanly.
- Tests pass.
- A request to generate copy creates a job and returns structured results.
- Repeated identical requests hit cache.
- Image jobs run asynchronously.
- All important code paths are covered by tests.

Implementation order:
1. Create the project skeleton and dependency files.
2. Implement settings, models, and migrations.
3. Implement serializers, views, URLs, and auth.
4. Implement OpenAI client and structured-output parsing.
5. Implement Celery tasks and Redis caching.
6. Add throttling and observability basics.
7. Add tests and Docker files.
8. Polish docs and clean up.

Do not stop after scaffolding. Build the full working backend end-to-end.
