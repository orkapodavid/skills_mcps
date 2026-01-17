# Marimo Development Environment

Marimo treats notebooks as Directed Acyclic Graphs (DAGs), enforcing reproducibility.

## Key Concepts

- **DAG Execution**: Cell B re-runs automatically if Cell A (its dependency) changes.
- **No Hidden State**: Deleting a cell removes its variables.
- **Top-Level Await**: Natively supports `await` without `asyncio.run()`, ideal for testing Prefect flows and HTTPX.

## Refactoring Strategy

- Remove side effects dependent on execution order.
- Refactor global mutations into functional transformations.
- Use Marimo for interactive validation of refactored components before deploying to production pipelines.
