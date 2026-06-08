# Frontend Architecture

## Purpose

This document describes the PROMPT2-driven frontend layer added on top of the existing Django backend.

The key constraint is scope honesty:

- the repository already contains a working content-generation backend
- it does **not** contain LangGraph, RAG orchestration, vector retrieval, agent routing, or memory dashboards
- the frontend therefore exposes the real backend capabilities instead of inventing unsupported systems

## Product Surface

The frontend lives under `frontend/` and uses:

- Next.js 15 App Router
- React 19
- TypeScript
- Tailwind CSS
- TanStack Query
- Zustand
- React Hook Form
- Zod
- Recharts

## Route Map

- `/`
  - landing page
  - positions the product as a guest-first demo surface
  - routes users toward the real workspace
- `/workspace`
  - main guest workspace
  - bootstraps anonymous identity
  - manages brands, templates, jobs, usage visibility, and request inspection
- `/jobs/[jobId]`
  - focused inspector for one generation job
  - shows status, raw output, assets, and regenerate action

## State Model

The frontend intentionally keeps state simple.

### Server state

TanStack Query handles:

- health status
- brands
- templates
- jobs
- usage events
- regenerate and create mutations

### Client state

Zustand handles:

- current guest bootstrap payload
- last request inspector payload
- last response inspector payload

### Browser persistence

Local storage stores the guest bootstrap envelope under:

- `contentgen.guest-session`

That payload is replayed into `POST /api/v1/guest/bootstrap/` on subsequent visits so the backend can refresh or recreate the guest mapping safely.

## Guest Flow

1. user lands on `/workspace`
2. frontend checks local storage for `guest_id`, `session_id`, and `device_id`
3. frontend calls `POST /api/v1/guest/bootstrap/`
4. backend returns a normalized guest session and current soft-limit summary
5. frontend persists that response locally
6. all later API requests attach:
   - `X-Guest-Id`
   - `X-Session-Id`
   - `X-Device-Id`

This keeps the frontend aligned with the backend guest-auth implementation instead of introducing a second identity system.

## Workspace Sections

### Session and limits

Shows:

- guest id
- session id
- device id
- session expiry
- current soft-limit usage

### Brand library

Creates and lists `BrandProfile` records owned by the guest backing user.

### Template library

Creates and lists `ContentTemplate` records owned by the guest backing user.

### Generation lab

Submits real generation jobs against:

- `POST /api/v1/generate/`

The form mirrors the actual serializer contract rather than an imagined future API.

### Jobs timeline

Polls:

- `GET /api/v1/jobs/`

and links into the detail inspector.

### Usage telemetry

Reads:

- `GET /api/v1/usage/`

and visualizes token and latency activity using Recharts.

### Request and response inspector

Captures the most recent frontend API request and response to make demos and debugging easier.

## Job Detail Design

The job detail page emphasizes inspection over decoration.

It shows:

- job metadata
- current status
- model used
- raw output payload
- normalized variants view when available
- attached generated assets
- regenerate action via `POST /api/v1/regenerate/<job_id>/`

It also polls while the job is still queued or running.

## Django Root Route

The backend deployment previously returned `404` at `/`.

To remove that dead-end:

- Django now serves a lightweight marketing/ops landing page at `/`
- it explains what is deployed
- it links to `/admin/` and `/health/`
- it makes the split between backend deployment and frontend repo surface explicit

## Build and Deployment Notes

- Google-hosted fonts were removed from the frontend layout
- this avoids CI or PaaS build failures when outbound font fetches are blocked
- `typedRoutes` is enabled using the current Next.js config shape
- `outputFileTracingRoot` is set to the repo root to avoid multi-lockfile workspace confusion

## Known Limits

The frontend still reflects backend reality:

- no chat transcript UI
- no document upload UI
- no vector retrieval UI
- no memory dashboard
- no multi-agent orchestration console

Those features should only be added if the corresponding backend systems are actually implemented.
