---
name: reflex-refactoring
description: This skill should be used when the user asks to "refactor a Reflex app", "clean up Reflex code", "optimize Reflex performance", "fix Reflex architecture", "migrate Reflex code", "improve Reflex app structure", or "modernize Reflex codebase".
version: 0.1.0
---

# Reflex Refactoring Expert

## Overview

This skill provides a structured approach to refactoring applications built with Reflex (reflex.dev). It guides the transformation of prototype-level code into production-grade, maintainable, and performant architectures.

## Refactoring Workflow

Follow this four-step process when refactoring Reflex applications:

### 1. Audit & Analysis
Before making changes, analyze the codebase for architectural violations using the **Dual-Phase Execution Model** (Compile-time vs Runtime).

*   **Check for Runtime-Logic Contamination:** Ensure no dynamic Python operations (e.g., `datetime.now()`, database queries) exist inside UI component definitions.
*   **Identify "God Objects":** Look for `State` classes that have grown too large and handle unrelated concerns.
*   **Detect Blocking Handlers:** Find event handlers doing synchronous heavy lifting (blocking the main thread).
*   **Review Project Structure:** Check if the project is a single file or poorly organized.

### 2. Planning the Refactor
Develop a plan based on the audit.
*   **Architecture:** Propose a **Domain-Driven Package Structure** (separate folders for `state`, `pages`, `components`, `models`).
*   **State Decomposition:** Plan how to split the monolithic state into **Flat Substates** (preferred) or **Component States**.
*   **Verification Strategy:** Define how you will verify changes (Unit Tests, Playwright E2E).

### 3. Execution (The Refactor)
Execute the changes incrementally.
*   **Structural Changes:** Move files to the new package structure. Resolve circular dependencies.
*   **State Extraction:** Create `substate.py` files. Use `get_state` for inter-state communication and `get_var_value` for performance.
*   **UI Optimization:** Extract repeating UI patterns into components. Use `rx.ComponentState` for isolated widget logic.
*   **Event Optimization:** Convert blocking handlers to `async` and use background tasks where appropriate.

### 4. Verification
Ensure the refactor didn't break functionality.
*   **Run Tests:** Execute unit tests for logic and Playwright tests for UI interaction.
*   **Static Analysis:** Run `ruff` and `mypy` to enforce type safety and code style.

## Modern Backend Practices

Reflex event handlers run on the backend (FastAPI). Apply modern Python asynchronous patterns:

*   **Async-Safe Wrappers:** Offload blocking I/O (like `pyodbc` or `sqlalchemy` sync calls) to threads using `await asyncio.to_thread(sync_func)`.
*   **Non-Blocking Networking:** Replace `requests` with `httpx.AsyncClient` for external API calls within event handlers.
*   **Strict Validation:** Use Pydantic V2 models (`model_validate_json`) to validate data entering the system from external APIs before loading it into State.
*   **Performance:** Use `get_var_value(State.var)` instead of `get_state(State)` when only reading a single value to avoid loading the entire state object.

## Resources

### Core Refactoring Guide
*   **`references/refactoring_guide.md`**: The comprehensive guide covering:
    *   Dual-Phase Execution Model details.
    *   State Decomposition strategies (Substates, Mixins, SharedState).
    *   UI Component Refactoring (Functional decomposition, `rx.ComponentState`).
    *   Event Handling Optimization (Concurrency, Debouncing).
    *   Verification Strategies (Testing, Linting).

### Reflex Development Reference
For specific syntax, component usage, or standard patterns, refer to the **reflex-dev** skill.
*   **`../reflex-dev/SKILL.md`**: Topic Router for specific documentation.
*   **`../reflex-dev/references/reflex-state-structure.mdc`**: **Critical** for understanding Substates, ComponentState, and performance.
*   **`../reflex-dev/references/patterns.md`**: Standard patterns for Auth, CRUD, and Real-time updates.

## Expert Persona & Guidelines

Adopt the role of a **Principal Software Architect** specializing in Reflex.

*   **Strictly enforce** the separation of Compile-Time UI and Runtime State.
*   **Never allow** Python runtime logic in UI functions.
*   **Always decompose** monolithic States into Substates or Mixins.
*   **Prefer** "Flat Substates" (inheriting from `rx.State`) over deep inheritance hierarchies.
*   **Always verify** changes with a defined testing strategy.
*   **Enforce types** using `rx.Field` and standard Python type hints.
