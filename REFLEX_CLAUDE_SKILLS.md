# Claude Skills Reference: Reflex Framework

This document serves as a technical reference for LLMs generating code or assisting with the Reflex web framework (Python). It focuses on core API specifications, component structures, and state management patterns.

## 1. App Configuration (`reflex.app.App`)

**Capability Name**: Application Container

**Syntax/Usage**:
The `App` class is the entry point. It manages pages, styles, and global state configuration.
```python
app = rx.App(
    theme=rx.theme(appearance="dark"),
    style={"font_family": "Inter"},
    stylesheets=["/styles.css"],
    overlay_component=None
)
```

**Gotchas/Common Errors**:
- **State Enablement**: `enable_state=False` disables all backend communication; use only for purely static sites.
- **Page Routes**: If `component` is a function, the route defaults to the function name unless specified.
- **Overlay Conflicts**: Custom `overlay_component` replaces the default connection error banner; ensure your custom overlay handles connection states if needed.

**Minimal Code Example**:
```python
import reflex as rx

def index():
    return rx.text("Hello")

app = rx.App()
app.add_page(index, route="/", title="Home")
```

## 2. Base Components (`reflex.components.component.Component`)

**Capability Name**: UI Components

**Syntax/Usage**:
All UI elements inherit from `Component`. They are typically instantiated via `create` (often aliased to the component name like `rx.box()`).
```python
class MyComponent(rx.Component):
    def add_hooks(self) -> list[str]:
        return ["const [mounted, setMounted] = useState(false)"]
```

**Gotchas/Common Errors**:
- **Custom Code Duplication**: Strings returned by `add_custom_code` are deduplicated per page. Avoid defining generic variable names (e.g., `const data = ...`) that might collide if multiple components inject them.
- **Hooks**: Hooks must be valid raw JavaScript strings injected into the React component body.
- **Children vs Props**: Some components strictly separate positional arguments (children) from keyword arguments (props).

**Minimal Code Example**:
```python
# Standard usage
box = rx.box(rx.text("Content"), bg="blue.500")

# Custom component wrapper
def custom_card(text: str) -> rx.Component:
    return rx.box(rx.text(text), padding="4", border="1px solid #eaeaea")
```

## 3. State Management (`reflex.state.State`)

**Capability Name**: Global State

**Syntax/Usage**:
The `State` class holds application state. It acts as the backend for the frontend UI.
```python
class MyState(rx.State):
    count: int = 0

    def increment(self):
        self.count += 1
```

**Gotchas/Common Errors**:
- **JSON Serialization**: All state variables must be JSON-serializable (primitives, dicts, lists, Pydantic models). Sets and arbitrary Python objects (like generic classes) often fail.
- **Shared State**: `rx.State` instances are per-user session. Class attributes are NOT shared across users unless explicitly managed (e.g., via a database or global singleton outside the class).
- **Mutation**: State can ONLY be modified inside event handlers (methods). Modifying state in `__init__` or computed vars (`@rx.var`) has no effect or causes errors.

**Minimal Code Example**:
```python
class CounterState(rx.State):
    value: int = 0

    def toggle(self):
        self.value = 1 if self.value == 0 else 0

def index():
    return rx.button(
        f"Value: {CounterState.value}",
        on_click=CounterState.toggle
    )
```

## 4. Component State (`reflex.state.ComponentState`)

**Capability Name**: Per-Component State

**Syntax/Usage**:
Allows creating self-contained components with their own state instance, rather than a global singleton state.
```python
class Counter(rx.ComponentState):
    count: int = 0

    def increment(self):
        self.count += 1

    @classmethod
    def get_component(cls, **props):
        return rx.button(f"Count: {cls.count}", on_click=cls.increment, **props)
```

**Gotchas/Common Errors**:
- **Instantiation**: You must access the component via `cls.create()` or the aliased `get_component` logic.
- **Scope**: Unlike global `State`, `ComponentState` creates a unique state instance for *each usage* of the component in the UI if configured correctly, but often acts similar to a sub-state.

**Minimal Code Example**:
```python
# Usage in a page
def index():
    return rx.vstack(
        Counter.create(),
        Counter.create(), # Independent counter
    )
```

## 5. Database Models (`reflex.model.Model`)

**Capability Name**: SQLModel Integration

**Syntax/Usage**:
Reflex uses SQLModel (SQLAlchemy wrapper). Models map to database tables.
```python
class User(rx.Model, table=True):
    username: str
    email: str
```

**Gotchas/Common Errors**:
- **Migrations**: `rx.Model.migrate(autogenerate=True)` attempts to generate Alembic scripts. Requires `alembic` to be initialized.
- **Relationship Loading**: Lazy loading can be tricky in async contexts. Often requires explicit `.options(selectinload(...))` in queries.
- **Engine Access**: `rx.Model.get_db_engine()` gives access to the underlying SQLAlchemy engine.

**Minimal Code Example**:
```python
class Post(rx.Model, table=True):
    title: str
    content: str

def add_post(self):
    with rx.session() as session:
        session.add(Post(title="Hello", content="World"))
        session.commit()
```

## 6. Events (`reflex.event.Event`)

**Capability Name**: Event Handling

**Syntax/Usage**:
Events describe state changes. Handlers return `EventSpec` or `None`.
```python
def handle_event(self, args: dict):
    # args contains payload from frontend
    pass
```

**Gotchas/Common Errors**:
- **Payload Structure**: The `router_data` field in events contains current path info.
- **Chaining**: Event handlers can yield other event handlers (by name) to chain actions. `return MyState.other_handler`.

**Minimal Code Example**:
```python
# Triggering an event from UI with custom payload
rx.button("Click", on_click=lambda: MyState.handle_click({"custom": "data"}))
```

## 7. Configuration (`rxconfig.py` / `reflex.config.Config`)

**Capability Name**: Runtime Configuration

**Syntax/Usage**:
Controls ports, DB connections, and environment settings.
```python
config = rx.Config(
    app_name="my_app",
    db_url="sqlite:///reflex.db",
    frontend_port=3000
)
```

**Gotchas/Common Errors**:
- **Environment Overrides**: Any config field can be overridden by `REFLEX_<FIELD_UPPERCASE>`. E.g., `REFLEX_DB_URL`.
- **API URL**: In production, `api_url` must match the actual public backend URL, or the frontend won't connect.
- **App Name**: Must match the directory name of the main module.

**Minimal Code Example**:
```python
# rxconfig.py
import reflex as rx

config = rx.Config(
    app_name="my_app",
    telemetry_enabled=False,
)
```

## 8. Vars (`reflex.vars.base.Var`)

**Capability Name**: Reactive Variables

**Syntax/Usage**:
`Var` objects represent values that may change on the frontend. They are not static Python values during app composition.
```python
# Checking for None in the frontend
rx.cond(
    MyState.my_var.is_none(),
    rx.text("No data"),
    rx.text(MyState.my_var)
)
```

**Gotchas/Common Errors**:
- **Python Logic vs Var Logic**: You cannot use standard Python `if` statements on `Var` objects during UI definition. Use `rx.cond`.
- **String Conversion**: `Var.to_string()` creates a reactive string representation.
- **Types**: Use `.to(int)` or `.to(str)` to explicit cast if the inferred type is generic.

**Minimal Code Example**:
```python
rx.text("Value is: " + MyState.count.to_string())
```

## 9. CLI (`reflex` command)

**Capability Name**: Command Line Interface

**Syntax/Usage**:
Main entry point for dev and build tasks.
```bash
reflex init
reflex run
reflex export
```

**Gotchas/Common Errors**:
- **Run Mode**: `reflex run` defaults to dev mode (hot reload). Use `reflex run --env prod` for production simulation.
- **Export Limits**: `reflex export` only builds the static frontend. The backend must be deployed separately (e.g., via Docker).
- **Database Init**: `reflex db init` is required before migrations can track changes.

**Minimal Code Example**:
```bash
# Full reset and run
rm -rf .web
reflex init
reflex run
```
