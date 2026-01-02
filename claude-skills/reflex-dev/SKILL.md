---
name: reflex-dev
description: Guide for building full-stack web applications using Reflex, a Python framework that compiles to React frontend and FastAPI backend. Use when creating, modifying, or debugging Reflex apps - covers state management, event handlers, components, routing, styling, and data integration patterns.
---

# Reflex Development

## Overview

Reflex is a full-stack Python framework for building web applications without writing JavaScript. Apps compile to a React frontend and FastAPI backend, with state management and event handlers running entirely in Python.

**Architecture:**
- **Frontend**: Compiled to React (JavaScript) for UI rendering
- **Backend**: FastAPI server running Python event handlers
- **Communication**: WebSockets for real-time state updates
- **State**: Server-side Python state synchronized to frontend

## Core Concepts

### State Management

State is a Python class that holds all mutable data and event handlers. All state variables must be JSON-serializable.

```python
import reflex as rx

class AppState(rx.State):
    # State variables (any JSON-serializable type)
    count: int = 0
    items: list[str] = []
    user_name: str = ""

    # Event handlers - the ONLY way to modify state
    def increment(self):
        self.count += 1

    def add_item(self, item: str):
        self.items.append(item)

    # Computed vars (derived state)
    @rx.var
    def item_count(self) -> int:
        return len(self.items)
```

**Key Rules:**
- State vars MUST be JSON-serializable (int, str, list, dict, bool, float)
- Only event handlers can modify state
- Use `@rx.var` decorator for computed/derived values
- State is per-user session (isolated between users)

### Components

Components are UI building blocks. Reflex provides 60+ built-in components.

```python
import reflex as rx

def header() -> rx.Component:
    return rx.heading("My App", size="lg")

def counter_component(state: AppState) -> rx.Component:
    return rx.vstack(
        rx.text(f"Count: {state.count}"),
        rx.button("Increment", on_click=state.increment),
        spacing="4"
    )
```

**Common Components:**
- Layout: `rx.vstack`, `rx.hstack`, `rx.box`, `rx.container`
- Text: `rx.heading`, `rx.text`, `rx.code`
- Input: `rx.input`, `rx.text_area`, `rx.select`, `rx.checkbox`
- Interactive: `rx.button`, `rx.link`, `rx.icon_button`
- Data: `rx.table`, `rx.data_table`, `rx.list`
- Charts: `rx.recharts.line_chart`, `rx.recharts.bar_chart`, etc.

### Event Handlers

Event handlers respond to user interactions and are the ONLY way to modify state.

```python
class FormState(rx.State):
    form_data: dict[str, str] = {}

    # Simple event handler
    def handle_submit(self):
        print(f"Submitted: {self.form_data}")

    # Event handler with argument
    def update_field(self, field: str, value: str):
        self.form_data[field] = value

    # Async event handler (for API calls, DB queries)
    async def fetch_data(self):
        # Can use any Python library
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.example.com/data")
            self.data = response.json()
```

**Event Triggers** (connect components to handlers):
- `on_click`: Button clicks
- `on_change`: Input field changes
- `on_submit`: Form submissions
- `on_mount`: Component first renders
- `on_blur`, `on_focus`: Input focus events

## Project Structure

Standard Reflex app structure:

```
my_app/
├── my_app/
│   ├── __init__.py         # Empty
│   └── my_app.py           # Main app file (State + pages)
├── assets/                 # Static files (images, fonts, etc.)
├── .web/                   # Auto-generated frontend (don't edit)
├── rxconfig.py             # Reflex configuration
└── requirements.txt        # Python dependencies
```

### Main App File Pattern

```python
import reflex as rx

# 1. Define State
class State(rx.State):
    count: int = 0

    def increment(self):
        self.count += 1

# 2. Define Pages
def index() -> rx.Component:
    return rx.container(
        rx.heading("Welcome"),
        rx.button("Click", on_click=State.increment),
        rx.text(f"Count: {State.count}")
    )

def about() -> rx.Component:
    return rx.container(
        rx.heading("About"),
        rx.link("Home", href="/")
    )

# 3. Create App and Add Routes
app = rx.App()
app.add_page(index, route="/")
app.add_page(about, route="/about")
```

## Common Patterns

### Form Handling

```python
class FormState(rx.State):
    name: str = ""
    email: str = ""

    def handle_submit(self, form_data: dict):
        self.name = form_data.get("name", "")
        self.email = form_data.get("email", "")

def form_page():
    return rx.form(
        rx.vstack(
            rx.input(name="name", placeholder="Name"),
            rx.input(name="email", placeholder="Email"),
            rx.button("Submit", type="submit"),
        ),
        on_submit=FormState.handle_submit,
    )
```

### Data Tables

```python
class DataState(rx.State):
    data: list[dict] = [
        {"id": 1, "name": "Alice", "age": 25},
        {"id": 2, "name": "Bob", "age": 30},
    ]

def data_table_page():
    return rx.data_table(
        data=DataState.data,
        columns=["id", "name", "age"],
        sort=True,
        search=True,
        pagination=True,
    )
```

### File Upload

```python
class UploadState(rx.State):
    async def handle_upload(self, files: list[rx.UploadFile]):
        for file in files:
            upload_data = await file.read()
            # Process file data
            outfile = f"./uploads/{file.filename}"
            with open(outfile, "wb") as f:
                f.write(upload_data)

def upload_page():
    return rx.vstack(
        rx.upload(
            rx.button("Select Files"),
            id="upload1",
        ),
        rx.button(
            "Upload",
            on_click=UploadState.handle_upload(rx.upload_files(upload_id="upload1"))
        ),
    )
```

### Database Integration (with DuckDB)

```python
import duckdb
import polars as pl

class DBState(rx.State):
    records: list[dict] = []

    async def load_data(self):
        # Use existing database connection
        conn = duckdb.connect("data/mydb.duckdb")
        df = conn.execute("SELECT * FROM mytable").pl()
        self.records = df.to_dicts()
        conn.close()

    async def insert_record(self, data: dict):
        conn = duckdb.connect("data/mydb.duckdb")
        conn.execute(
            "INSERT INTO mytable (name, value) VALUES (?, ?)",
            [data["name"], data["value"]]
        )
        conn.close()
        await self.load_data()  # Refresh
```

## Styling & Layout

### Inline Styling

```python
rx.box(
    rx.text("Styled text"),
    bg="#1a5f9e",
    color="white",
    padding="4",
    border_radius="md",
)
```

### Responsive Layout

```python
rx.container(
    rx.responsive_grid(
        rx.box("Item 1", bg="blue"),
        rx.box("Item 2", bg="green"),
        rx.box("Item 3", bg="red"),
        columns=[1, 2, 3],  # 1 col mobile, 2 tablet, 3 desktop
        spacing="4",
    ),
    max_width="1200px",
)
```

### Common Style Props

- Layout: `width`, `height`, `padding`, `margin`, `display`
- Colors: `bg` (background), `color` (text)
- Typography: `font_size`, `font_weight`, `text_align`
- Borders: `border`, `border_radius`, `border_color`
- Spacing: `spacing` (for stacks), `gap`

## Routing

### Multiple Pages

```python
app = rx.App()

# Route with parameters
@rx.page(route="/user/[id]")
def user_page() -> rx.Component:
    return rx.text(f"User ID: {State.router.page.params.get('id')}")

# Simple routes
app.add_page(index, route="/")
app.add_page(about, route="/about")
```

### Navigation

```python
# Links
rx.link("Go to About", href="/about")

# Programmatic navigation
def go_home(self):
    return rx.redirect("/")
```

## Development Workflow

### Initialize New App

```bash
pip install reflex
reflex init
```

### Run Development Server

```bash
reflex run
```

App runs on `http://localhost:3000` with auto-reload.

### Common Commands

```bash
reflex run          # Start dev server
reflex export       # Build production bundle
reflex db init      # Initialize database (if using Reflex DB)
reflex db migrate   # Run migrations
```

## Best Practices

1. **State Organization**: Split large states into substates
   ```python
   class AuthState(rx.State):
       user: str = ""

   class DataState(rx.State):
       items: list = []
   ```

2. **Component Reusability**: Create reusable component functions
   ```python
   def card(title: str, content: str) -> rx.Component:
       return rx.box(
           rx.heading(title, size="md"),
           rx.text(content),
           padding="4",
           border="1px solid #ddd",
       )
   ```

3. **Event Handler Performance**: Use async for I/O operations
   ```python
   async def fetch_data(self):
       # Async I/O won't block other users
       self.data = await some_api_call()
   ```

4. **Type Hints**: Always type-hint state vars and event handlers
   ```python
   count: int = 0
   items: list[str] = []

   def update_count(self, value: int) -> None:
       self.count = value
   ```

## Core API Reference

### App (`reflex.app.App`)

**Capability**: Application container, routing, and global theming.

**Key Fields**:
- `theme: Component | None` – Global theme component for the app.
- `style: ComponentStyle` – Global style configuration applied across pages.
- `stylesheets: list[str]` – Additional stylesheets to include.
- `reset_style: bool = True` – Toggles CSS reset (margin and padding).
- `overlay_component: Component | ComponentCallable | None` – Overlay component rendered on every page (defaults to connection error banner).
- `head_components: list[Component]` – Components injected into `<head>` on every page.
- `html_lang: str | None` – Language attribute for the root `<html>` tag.
- `html_custom_attrs: dict[str, str] | None` – Extra attributes for root `<html>` tag.
- `enable_state: bool = True` – Enables or disables Reflex state system.
- `frontend_exception_handler` / `backend_exception_handler` – Custom error handlers.

**Routing Methods**:
- `app.add_page(component, route=None, title=None, description=None, image='favicon.ico', on_load=None, meta=[], context=None)`
  - If `component` is a function, `route` defaults to the function name.
  - If `component` is a component instance, `route` must be provided.

```python
import reflex as rx


class IndexState(rx.State):
    visits: int = 0

    def increment(self):
        self.visits += 1


def index() -> rx.Component:
    return rx.vstack(
        rx.text(f"Visits: {IndexState.visits}"),
        rx.button("Increment", on_click=IndexState.increment),
    )


app = rx.App(
    theme=rx.theme(appearance="dark"),
    style={"font_family": "Inter"},
    stylesheets=["/static/styles.css"],
)
app.add_page(index, route="/", title="Home")
```

### State (`reflex.state.State`) and Component State (`reflex.state.ComponentState`)

**Global State (`State`)**:
- Base class for application-level state.
- State variables must be JSON-serializable (int, str, bool, float, list, dict, Pydantic models).
- All mutations occur inside event handler methods.
- Selected built-in helpers:
  - `set_is_hydrated(*args, **kwargs) -> EventSpec` – Internal hydration flag event.
  - `setvar(*args: Any) -> EventSpec` – Generic setter used by generated setters.

```python
class CounterState(rx.State):
    value: int = 0

    def increment(self):
        self.value += 1


def index() -> rx.Component:
    return rx.button(
        f"Value: {CounterState.value}",
        on_click=CounterState.increment,
    )
```

**Component-local State (`ComponentState`)**:
- Encapsulates state and UI per usage of a component.
- Each `MyComponentState.create()` call yields an independent instance.

```python
class Counter(rx.ComponentState):
    count: int = 0

    def increment(self):
        self.count += 1

    @classmethod
    def get_component(cls, **props) -> rx.Component:
        return rx.button(
            f"Count: {cls.count}",
            on_click=cls.increment,
            **props,
        )


def index() -> rx.Component:
    return rx.vstack(
        Counter.create(),
        Counter.create(),
    )
```

**State Gotchas**:
- Mutate only inside event handlers; avoid direct mutation at import time.
- Treat state as per-session; use databases or caches for shared data.
- Use `rx.cond` and Var helpers when branching on state-derived reactive values.

### Component (`reflex.components.component.Component`)

**Capability**: Base class for all UI elements.

**Key Methods**:
- `create(*children, **props) -> Component` – Factory used by `rx.box`, `rx.text`, etc.
- `add_imports(self) -> ImportDict | list[ImportDict]` – JS imports required by the component.
- `add_hooks(self) -> list[str | Var]` – Raw JavaScript hooks (e.g. `useEffect`) injected into the React component.
- `add_custom_code(self) -> list[str]` – Module-level JS snippets (deduplicated per page).
- `get_event_triggers(cls) -> dict[str, ArgsSpec | Sequence[ArgsSpec]]` – Declares event props such as `on_click`, `on_change`, etc.
- `get_props(cls) -> Iterable[str]` – Declares available props.
- `get_initial_props(cls) -> set[str]` – Declares props to initialize.
- `add_style(self) -> dict[str, Any] | None` – Returns additional style for this component instance.

```python
class MountedComponent(rx.Component):
    def add_hooks(self) -> list[str]:
        return ["const [mounted, setMounted] = React.useState(false);"]


def index() -> rx.Component:
    return rx.fragment(
        MountedComponent.create(),
        rx.text("Mounted component above"),
    )
```

**Component Gotchas**:
- `add_hooks` and `add_custom_code` strings are deduplicated by literal value; keep different behaviors in distinct strings.
- Positional arguments are children, keyword arguments are props; mixing these incorrectly can distort the layout hierarchy.
- When defining new components with event props, ensure `get_event_triggers` is correct so event handlers bind properly.

### Var (`reflex.vars.base.Var`)

**Capability**: Represents reactive values in the UI tree.

**Key Methods**:
- `equals(other: Var) -> bool`
- `create(value, _var_data=None) -> Var`
- `to(output_type, var_type=None) -> Var` – Casts to another type (e.g. `.to(int)`, `.to(str)`).
- `guess_type()` – Infers the var type.
- `bool() -> BooleanVar` – Boolean conversion.
- `is_none() -> BooleanVar` / `is_not_none() -> BooleanVar`
- `to_string(use_json=True) -> StringVar` – String representation.
- `js_type() -> StringVar` – JavaScript `typeof`.
- `range(first_endpoint, second_endpoint=None, step=None)` – Produces numeric ranges.

```python
class CounterState(rx.State):
    count: int = 0

    def increment(self):
        self.count += 1


def index() -> rx.Component:
    return rx.button(
        "Count: " + CounterState.count.to_string(),
        on_click=CounterState.increment,
    )
```

**Var Gotchas**:
- Avoid Python `if` on `Var` values in component trees; use `rx.cond` and Var predicates (`is_none`, etc.).
- Cast types explicitly when concatenating or performing numeric operations.

### Model (`reflex.model.Model`)

**Capability**: SQLModel/SQLAlchemy integration for database tables and migrations.

**Core Methods**:
- `create_all()` – Create all tables.
- `get_db_engine()` – Access underlying SQLAlchemy engine.
- `alembic_init()` – Initialize Alembic for migrations.
- `get_migration_history()` – Inspect migration history.
- `alembic_autogenerate(connection, message=None, write_migration_scripts=True) -> bool` – Autogenerate migration scripts.
- `migrate(autogenerate: bool = False) -> bool | None` – Apply Alembic migrations.
- `select()` – Build a query for the model.

```python
class Post(rx.Model, table=True):
    title: str
    content: str


class BlogState(rx.State):
    def add_post(self, title: str, content: str):
        with rx.session() as session:
            session.add(Post(title=title, content=content))
            session.commit()
```

### Event (`reflex.event.Event`)

**Capability**: Low-level representation of state change requests.

**Fields**:
- `token: str` – Identifies the client.
- `name: str` – Event name (e.g. `state.method_name`).
- `router_data: dict` – Routing info at the time of the event.
- `payload: dict` – Payload from the frontend.

LLM usage typically focuses on declaring event handlers on state classes and wiring them via component props such as `on_click`, `on_change`, and `on_submit`.

### Config (`reflex.config.Config` / `rxconfig.py`)

**Capability**: Central configuration for runtime behavior and deployment.

**Key Areas**:
- App settings: `app_name`, `loglevel`, `telemetry_enabled`.
- Server: `frontend_port`, `frontend_path`, `backend_port`, `api_url`, `deploy_url`, `backend_host`.
- Database: `db_url`, `async_db_url`, `redis_url`.
- Frontend: `frontend_packages`, `react_strict_mode`, `show_built_with_reflex`.
- State management: `state_manager_mode`, `state_auto_setters`, Redis lock/token settings.
- Plugins: `plugins`, `disable_plugins`.
- Misc: `env_file`, `transport`, `bun_path`, `static_page_generation_timeout`.

**Environment Overrides**:
- Any config field can be overridden by environment variables in the form `REFLEX_<FIELD_NAME_IN_UPPERCASE>`, e.g. `REFLEX_DB_URL`, `REFLEX_FRONTEND_PORT`.

```python
# rxconfig.py
import reflex as rx


config = rx.Config(
    app_name="blog_app",
    db_url="sqlite:///blog.db",
    telemetry_enabled=False,
    cors_allowed_origins=["http://localhost:3000"],
)
```

### CLI (`reflex` command)

**Capability**: Project scaffolding, dev server, export, and cloud tools.

**Common Commands**:
- `reflex init` – Initialize or update a Reflex app in the current directory.
- `reflex run` – Run the app (dev mode by default with hot reload).
- `reflex export` – Build exportable frontend/backend bundles.
- `reflex rename` – Rename the app based on config.
- `reflex cloud ...` – Manage Reflex Cloud apps, projects, secrets.
- `reflex script ...` – Run helper scripts.

```bash
reflex init
reflex run
reflex export
```

**CLI Gotchas**:
- `reflex run` uses development mode by default; use appropriate flags (e.g. `--env prod`) for production-like runs.
- `reflex export` builds a static frontend and a backend bundle; deployment still requires hosting the backend.
- CLI commands depend on a valid `rxconfig.py` and `app_name` matching the app directory.

## References

### Documentation
- Official Docs: https://reflex.dev/docs/getting-started/introduction/
- Component Library: https://reflex.dev/docs/library
- Tutorials: https://reflex.dev/docs/getting-started/tutorial/

### Example Apps
See `examples/` directory for complete working examples:
- Simple counter app
- Data table with CRUD operations
- Form with validation
- File upload and processing

### Common Patterns Reference
See `references/patterns.md` for detailed examples of:
- Authentication flows
- Real-time updates
- Complex form validation
- Multi-step workflows
- Data visualization with charts

## Additional Resources

### Reference Files

For comprehensive technical specifications and advanced patterns, consult the following reference files in `references/`:

**Core Framework & Configuration:**
- **`reflex-framework-base.mdc`** – Core framework concepts, architecture, and initialization patterns
- **`reflex-app-config.mdc`** – Application configuration, rxconfig.py settings, and deployment options
- **`reflex-cli-env-utils.mdc`** – CLI commands, environment management, and build utilities

**State & Data Management:**
- **`reflex-state-model.mdc`** – State management patterns, computed vars, and state composition
- **`reflex-state-structure.mdc`** – State architecture, substates, and state organization strategies
- **`reflex-var-system.mdc`** – Var system, reactive values, type conversions, and Var operations

**Components & UI:**
- **`reflex-components-base.mdc`** – Base component APIs, custom components, and component composition
- **`reflex-layout.mdc`** – Layout components (Box, Stack, Grid, Flex, Container)
- **`reflex-typography.mdc`** – Text components (Heading, Text, Code, Markdown)
- **`reflex-forms.mdc`** – Form components, validation patterns, and form state management
- **`reflex-data-display.mdc`** – Data display components and visualization patterns
- **`reflex-tables.mdc`** – Table components, data tables, and tabular data patterns
- **`reflex-overlay.mdc`** – Modal, Dialog, Popover, Tooltip, and overlay components
- **`reflex-disclosure-media-utils.mdc`** – Accordion, Tabs, Collapse, Image, Video, and media components
- **`reflex-browser-apis.mdc`** – Browser APIs, local storage, cookies, and client-side utilities

**Events & Interactions:**
- **`reflex-events-handlers.mdc`** – Event handler patterns, async events, and event chaining
- **`reflex-dynamic-rendering.mdc`** – Conditional rendering, dynamic components, and rx.cond patterns

**Charts & Visualization:**
- **`reflex-charts.mdc`** – Chart components and data visualization patterns
- **`reflex-agchart.mdc`** – AG Charts integration and advanced charting
- **`reflex-aggrid.mdc`** – AG Grid integration for enterprise data tables

**Advanced Topics:**
- **`reflex-dashboard.mdc`** – Dashboard patterns, layouts, and best practices
- **`reflex-azure-auth.mdc`** – Azure authentication integration patterns
- **`reflex-enterprise.mdc`** – Enterprise patterns, scalability, and production deployment
- **`reflex-tests.mdc`** – Testing strategies, unit tests, and integration testing patterns

**Common Patterns:**
- **`patterns.md`** – Curated collection of authentication flows, real-time updates, form validation, multi-step workflows, and data visualization examples
