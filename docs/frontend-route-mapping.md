# Frontend Route Mapping

## Principles

- Every real backend capability gets a frontend surface.
- Missing backend capabilities are documented, not faked.
- Guest mode is first-run default.

## Routes

### `/`

Purpose:

- landing page
- capability overview
- guest-first CTA
- links to admin, health, docs, and workspace

Backend mappings:

- `POST /api/v1/guest/bootstrap/`
- `GET /health/`

### `/workspace`

Purpose:

- primary integration-testing surface
- brand creation
- template creation
- generation form
- job history
- usage snapshot

Backend mappings:

- `POST /api/v1/guest/bootstrap/`
- `GET /api/v1/brands/`
- `POST /api/v1/brands/`
- `GET /api/v1/templates/`
- `POST /api/v1/templates/`
- `POST /api/v1/generate/`
- `POST /api/v1/generate/image/`
- `GET /api/v1/jobs/`
- `GET /api/v1/usage/`

### `/jobs/[jobId]`

Purpose:

- inspect a single generation job
- view payload, output, status, asset metadata
- trigger regenerate

Backend mappings:

- `GET /api/v1/jobs/{job_id}/`
- `POST /api/v1/regenerate/{job_id}/`

## Panels Inside Workspace

### Guest Session Panel

Displays:

- guest id
- session id
- device id
- expiry
- soft-limit counters

### Brand Library Panel

Displays:

- brand profiles
- search and sort
- create form

### Template Library Panel

Displays:

- content templates
- create form

### Generation Lab

Displays:

- selected brand/template
- campaign prompt inputs
- queued/running/succeeded state
- output variants
- image toggle

### Jobs Timeline

Displays:

- job status
- cache hits
- timestamps
- asset indicators

### Usage Analytics

Displays:

- event counts
- token usage
- cache hit distribution
- recent activity

### API Inspector

Displays:

- last request payload
- last response payload
- endpoint used
- error body when requests fail

## Explicitly Omitted Screens

These are not implemented because the backend does not support them:

- RAG playground
- memory dashboard
- agent playground
- workflow inspector
- knowledge base manager

If those backend systems are added later, they should become first-class routes rather than placeholder cards.
