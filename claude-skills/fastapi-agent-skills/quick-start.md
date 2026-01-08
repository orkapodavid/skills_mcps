# Quick Start: Building a Production‑Ready FastAPI Service

## Goal
Stand up a minimal, production‑ready FastAPI service with typed models, authentication, database access, and error handling—optimized for LLM coding workflows.

## Path A — Minimal REST API (60–90 minutes)
1) Project Initialization
   - Create virtual env and scaffold directories.
   - Add linters (`ruff`), type checks (`mypy`), tests (`pytest`).
   - Run dev server: `uvicorn app.main:app --reload`.
   - Refer: [Project Initialization](01-application-fundamentals/project-initialization.md)

2) Request & Validation
   - Define endpoints with path/query parameters.
   - Create Pydantic v2 models for request/response.
   - Refer: [Parameter Parsing](02-request-response-handling/parameter-parsing.md), [Pydantic Validation](02-request-response-handling/pydantic-validation.md)

3) Error & Response Strategy
   - Add exception handlers and a standard error schema.
   - Use `response_model` for consistent outputs.
   - Refer: [Error Handling](02-request-response-handling/error-handling.md), [Response Handling](02-request-response-handling/response-handling.md)

4) Authentication (Basic)
   - Implement OAuth2 password flow to issue tokens.
   - Secure a protected route using bearer tokens.
   - Refer: [OAuth2 Password Flow](03-security-authentication/oauth2-password-flow.md), [JWT Tokens](03-security-authentication/jwt-tokens.md)

5) Database Access (Async)
   - Configure SQLAlchemy async engine and session dependency.
   - Implement a simple CRUD list endpoint.
   - Refer: [SQLAlchemy Integration](04-data-persistence/sqlalchemy-integration.md), [Async Database Operations](04-data-persistence/async-database-operations.md)

6) CORS & Middleware
   - Add CORS for your frontend origin.
   - Add security headers and request timing middleware.
   - Refer: [CORS Configuration](03-security-authentication/cors-configuration.md), [Middleware Configuration](01-application-fundamentals/middleware-configuration.md)

## Path B — Real‑time & Background Tasks (90–120 minutes)
1) Background Tasks
   - Use `BackgroundTasks` for light work inside requests.
   - Queue heavy tasks to Celery/RQ workers.
   - Refer: (coming) Background Tasks, Task Queues

2) Real‑time Streaming
   - Add WebSocket or SSE endpoints for live updates.
   - Handle authentication for WebSocket connections.
   - Refer: (coming) WebSockets, Server‑Sent Events

## Enterprise Add‑Ons (Optional)
- Reverse proxy (Nginx/IIS) and health checks for production.
- Monitoring and structured logging with correlation IDs.
- Multi‑tenancy and audit logging for regulated workflows.
- Refer: (coming) Reverse Proxy Configuration, Health Checks, Monitoring & Logging, Multi‑tenancy, Audit Logging

## LLM Workflow Tips
- Keep dependencies small and well‑named; provide explicit import paths.
- Use typed settings/config to reduce ambiguity in prompts.
- Prefer clear function names that reflect responsibility (e.g., `issue_token`, `verify_token`).
- Write unit tests first; then ask the agent to implement passing code.

## Next Steps
Continue with advanced patterns and deployment guides. Update the README as new skills are generated.
