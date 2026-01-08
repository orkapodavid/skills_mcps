# FastAPI Agent Skills

## Overview
This repository provides production-ready FastAPI patterns and best practices, organized as a **Claude Code Skill**. It is designed to help LLM agents and developers build scalable, typed, and secure web services.

## Standard Skill Structure
This project follows the "Skill Development" standard:
- **`SKILL.md`**: Master instruction file with trigger phrases and core workflows.
- **`references/`**: Detailed documentation on application fundamentals, security, data persistence, and more.
- **`scripts/`**: Utility scripts for automation and scaffolding.
- **`examples/`**: (Coming soon) Working code examples.

## Key Topics
- **Project Initialization**: Layered architecture and developer tooling.
- **Request/Response**: Pydantic validation, parameter parsing, and error handling.
- **Security**: OAuth2, JWT, API Key auth, and CORS.
- **Data Persistence**: Async SQLAlchemy, session management, and pooling.

## How to Use
1. **As a Claude Skill**: Point Claude to this directory to activate the skill instructions in `SKILL.md`.
2. **Project Scaffolding**: Run `python scripts/scaffold_fastapi.py [project_name]` to generate a new service skeleton.

## Quick Links
- [SKILL.md](SKILL.md)
- [Quick Start](quick-start.md)
- [References](references/)
