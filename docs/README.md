# Documentation Index

This folder contains implementation and operations documentation for the project.

## Documents

- [architecture.md](architecture.md)
  - system structure, request flow, service boundaries, async pipeline
- [api.md](api.md)
  - endpoint layout, auth behavior, generation semantics, error patterns
- [operations.md](operations.md)
  - runtime components, health checks, worker behavior, operational failure modes
- [data-model.md](data-model.md)
  - entity definitions, ownership rules, lifecycle expectations
- [testing.md](testing.md)
  - test strategy, current coverage, local verification workflow
- [deployment.md](deployment.md)
  - deployment shape, environment requirements, rollout checklist
- [development.md](development.md)
  - local development conventions and implementation guidance
- [frontend-architecture.md](frontend-architecture.md)
  - guest workspace structure, state model, route layout, and PROMPT2 scope handling

## Suggested Reading Order

For new engineers:

1. [architecture.md](architecture.md)
2. [data-model.md](data-model.md)
3. [api.md](api.md)
4. [development.md](development.md)
5. [frontend-architecture.md](frontend-architecture.md)
6. [testing.md](testing.md)

For operators:

1. [deployment.md](deployment.md)
2. [operations.md](operations.md)
