# Pydantic V2 Migration Guide

## Key Architectural Changes

Pydantic V2 shifts validation to `pydantic-core` (Rust), offering 4x-50x performance gains but requiring strict type adherence.

### SerDes Debt & Performance

- **Anti-pattern**: Using Pydantic models for internal data passing where validation isn't needed. Use dataclasses or TypedDicts for internal "hot paths".
- **Optimization**: `model_validate_json` passes raw JSON bytes to Rust, bypassing Python dictionary creation.
  - **Old**: `MyModel.parse_obj(json.loads(data))`
  - **New**: `MyModel.model_validate_json(data)`

## Migration Table (V1 -> V2)

| V1 Concept | V2 Replacement | Notes |
| :--- | :--- | :--- |
| `parse_obj(obj)` | `model_validate(obj)` | Strict validation. |
| `parse_raw(json)` | `model_validate_json(json)` | Bypasses `json.loads`. |
| `dict()` | `model_dump()` | Use `mode='json'` for serialization. |
| `json()` | `model_dump_json()` | Optimized Rust JSON generation. |
| `class Config:` | `model_config = ConfigDict(...)` | Better inheritance merging. |
| `@validator` | `@field_validator` | Requires explicit signature. |
| `@root_validator` | `@model_validator` | Supports `mode='before'`/`'after'`. |
| `__fields__` | `model_fields` | Metadata access. |
| `const=True` | `Literal` | Enforce using `Literal` type hint. |

## Validator Refactoring

### Field Validators

Legacy validators using `values` dict must be rewritten to use `ValidationInfo` or `self`.

**V1 (Legacy):**
```python
@validator('end_date')
def check_dates(cls, v, values):
    if 'start_date' in values and v < values['start_date']:
        raise ValueError("End date before start date")
    return v
```

**V2 (Modern):**
```python
@model_validator(mode='after')
def check_dates(self):
    if self.start_date and self.end_date and self.end_date < self.start_date:
        raise ValueError("End date before start date")
    return self
```

### TypeAdapter

Do not instantiate `TypeAdapter` inside functions or loops. Cache it globally.

**Correct:**
```python
_int_list_adapter = TypeAdapter(List[int])

def validate_list(data):
    return _int_list_adapter.validate_python(data)
```
