---
name: FastAPI Agent Skills
description: This skill should be used when the user wants to "create a fastapi app", "implement pydantic validation", "setup jwt authentication", "integrate sqlalchemy", "configure fastapi middleware", or needs guidance on production-ready FastAPI patterns and architecture.
version: 1.0.0
---

# FastAPI Agent Skills

This skill provides production-ready FastAPI patterns and best practices for building scalable, typed, and secure web services.

## Core Workflows

### 1. Initialize a New Project
To start a new FastAPI service, use the provided scaffolding script or follow the layout guidance in the references.

- **`scripts/scaffold_fastapi.py`** - Generate a production-ready directory layout.
- **`references/application-fundamentals.md`** - Detailed setup and architecture patterns.

### 2. Implement Request/Response Logic
Define endpoints, validate inputs with Pydantic v2, and handle errors consistently.

- **`references/request-response-handling.md`** - Guidance on parameters, validation, and error mapping.

### 3. Secure the Service
Add authentication (OAuth2/JWT/API Keys) and configure security headers.

- **`references/security-authentication.md`** - Implementation patterns for various auth flows.

### 4. Persist Data
Integrate with SQL databases using SQLAlchemy and asynchronous operations.

- **`references/data-persistence.md`** - ORM setup, dependency injection, and pooling.

## Key Principles

- **Explicit Typing**: Use Python type hints and Pydantic models for all data contracts.
- **Asynchronous I/O**: Prefer async drivers and `await` for all network and disk operations.
- **Dependency Injection**: Use FastAPI's `Depends` for shared resources like database sessions and authentication contexts.
- **Layered Architecture**: Separate API routes from business logic and data models.

## Additional Resources

### Reference Files
- **`references/application-fundamentals.md`** - Basics, Middleware, Lifecycle.
- **`references/request-response-handling.md`** - Parsing, Validation, Responses, Errors.
- **`references/security-authentication.md`** - JWT, OAuth2, API Keys, CORS.
- **`references/data-persistence.md`** - SQLAlchemy, Async Ops, Pooling.

### Utility Scripts
- **`scripts/scaffold_fastapi.py`** - Project bootstrapping tool.
