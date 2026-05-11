---
agent: Planner
description: "Design REST API endpoints with OpenAPI spec, schemas, and task breakdown"
argument-hint: "API domain or feature name (e.g., 'user management', 'orders')"
---

# API Design

Design RESTful API endpoints for the specified domain.

## Input

Use the argument to determine the API scope:

- **Domain name**: Design endpoints for that business capability
- **Backlog task ID**: Read the task for requirements, then design the API

## Process

1. **Clarify scope** — Identify resources (nouns), consumers (frontend/mobile/external), and auth requirements. Use `@Explore` to find existing API patterns in the codebase.
2. **Define resources & operations** — Map HTTP methods to endpoints with request/response schemas.
3. **Design schemas** — Write Pydantic models (Python) or Zod schemas (TypeScript) for request/response types.
4. **Standardize errors** — Use consistent error response format across endpoints.
5. **Generate OpenAPI spec** — Produce a valid [OpenAPI 3.1](https://spec.openapis.org/oas/v3.1.1.html) YAML spec.
6. **Break down tasks** — Create backlog tasks for the Builder to implement.

## OpenAPI Spec Location

- Full-Stack layout: `backend/openapi.yaml`
- Multi-domain: `backend/openapi/{domain}.yaml`

The spec is the **source of truth** for the API contract. The Builder uses it to implement endpoints, write contract tests (`tests/contract/`), and generate typed frontend clients.

## Output Artifacts

| Artifact | Location | Format |
|----------|----------|--------|
| Design document | `.copilot-tracking/agents/planner/plans/` | Markdown |
| OpenAPI spec | `backend/openapi.yaml` | OpenAPI 3.1 YAML |
| Pydantic/Zod schemas | Inline in design doc | Code blocks |
| Task breakdown | Backlog.md | CLI tasks |
