---
name: reflex-dev
description: This skill should be used when the user asks to "create a Reflex app", "fix a Reflex error", "add a feature to Reflex app", "explain Reflex concepts", or "deploy a Reflex app". It serves as a router to specific documentation for State, Events, Components, Styling, and Deployment.
version: 1.0.0
---

# Reflex Development Guide

## Overview

Reflex is a full-stack Python framework that allows you to build web applications without writing JavaScript. It compiles Python code to a React frontend and a FastAPI backend.

**Key Architecture:**
*   **Frontend (Compile-time):** Python components are compiled to React/Next.js. They run in the browser.
*   **Backend (Runtime):** Event handlers run on the server (FastAPI) in Python.
*   **Communication:** State updates are sent via WebSockets.

## When to Use This Skill

Use this skill to guide the user through:
1.  **Scaffolding & Configuration:** Creating new apps, configuring `rxconfig.py`.
2.  **State Management:** Designing the app state, substates, and vars.
3.  **UI Construction:** Building layouts with components.
4.  **Interactivity:** Handling events (`on_click`, `on_change`).
5.  **Deployment:** Preparing for production.

## Mental Model for LLMs

To write effective Reflex code, you must distinguish between **Compile-time** and **Runtime**:

| Concept | Where it runs | Language | What it does | Restrictions |
| :--- | :--- | :--- | :--- | :--- |
| **Components** | Browser | Python $\to$ JS | Defines UI structure | No arbitrary Python logic (loops/ifs) inside rendering. Use `rx.cond` and `rx.foreach`. |
| **State** | Server | Python | Holds data | Must be JSON-serializable. |
| **Event Handlers** | Server | Python | Modifies State | Full Python power (DB access, API calls). |
| **Vars** | Both | Python $\to$ JS | Reactive data | Can be used in components to display data. |

## Topic Router (How to Handle Requests)

Use this table to decide which reference file to load. **Do not load all files at once.**

| User Intent / Topic | Primary Reference | Secondary Reference |
| :--- | :--- | :--- |
| **"Create a new app", "Project structure", "Config"** | `reflex-framework-base.mdc` | `reflex-app-config.mdc`, `reflex-cli-env-utils.mdc` |
| **"State", "Vars", "Reactive variables"** | `reflex-state-model.mdc` | `reflex-var-system.mdc`, `reflex-state-structure.mdc` |
| **"Events", "Click handlers", "Async tasks"** | `reflex-events-handlers.mdc` | `reflex-events-args.mdc` |
| **"Layout", "Styling", "CSS"** | `reflex-layout.mdc` | `reflex-components-base.mdc`, `reflex-typography.mdc` |
| **"Forms", "Inputs", "Validation"** | `reflex-forms.mdc` | `reflex-events-handlers.mdc` |
| **"Data Tables", "Grids", "Charts"** | `reflex-data-display.mdc` | `reflex-tables.mdc`, `reflex-charts.mdc`, `reflex-aggrid.mdc` |
| **"Custom Components", "React Wrapping"** | `reflex-custom-components.mdc` | |
| **"Deployment", "Hosting", "Docker"** | `reflex-hosting.mdc` | `reflex-app-config.mdc` |
| **"Database", "SQLModel"** | `reflex-state-model.mdc` | `patterns.md` |
| **"Auth", "Login", "Security"** | `reflex-azure-auth.mdc` | `patterns.md` (has auth examples) |
| **"Tests", "Testing"** | `reflex-tests.mdc` | |
| **"Multiple Pages", "Routing"** | `reflex-framework-base.mdc` | |

## Common Workflows

### 1. Defining State
State is the core of any Reflex app. It holds the data that changes over time.
*   **Reference:** `reflex-state-model.mdc`
*   **Key Concept:** All state must be in a class inheriting from `rx.State`.

### 2. Building UI
UI is built using Python functions that return `rx.Component`.
*   **Reference:** `reflex-components-base.mdc`, `reflex-layout.mdc`
*   **Key Concept:** Use `rx.vstack`, `rx.hstack`, and `rx.box` for layout.

### 3. Handling Interactions
Connect UI events to State methods.
*   **Reference:** `reflex-events-handlers.mdc`
*   **Key Concept:** `on_click=State.method_name`.

### 4. Displaying Data
Use `rx.foreach` for lists and `rx.cond` for conditionals.
*   **Reference:** `reflex-framework-base.mdc`, `reflex-var-system.mdc`
*   **Key Concept:** You cannot use Python `for` loops or `if` statements inside the UI definition for reactive data.

## Additional Resources

*   **`examples/`**: Contains full working examples of simple apps.
*   **`patterns.md`**: A cookbook of common patterns (Auth, CRUD, Dashboards).
