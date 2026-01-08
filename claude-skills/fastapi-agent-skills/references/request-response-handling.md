# Request & Response Handling

This guide covers parameter parsing, data validation with Pydantic, response formatting, and error handling.

## Parameter Parsing

Define and validate path, query, and body parameters using clear types and constraints.

### Path and Query Parameters
Use function parameters for path/query values. Prefer enums and explicit defaults:
```python
from fastapi import FastAPI, Query
from enum import Enum

class SortBy(str, Enum):
    created = "created"
    amount = "amount"

@app.get("/deals/{deal_id}")
async def get_deal(deal_id: int, sort: SortBy = Query(default=SortBy.created)) -> dict:
    return {"id": deal_id, "sort": sort}
```

### Body Parameters
Define complex inputs using Pydantic models:
```python
from pydantic import BaseModel, conint

class DealFilter(BaseModel):
    page: conint(ge=1) = 1
    size: conint(ge=1, le=200) = 50
    issuer: str | None = None
```

## Pydantic Validation (v2)

Validate and serialize data using Pydantic models and field constraints.

### Model Definition
Use `Annotated` and `Field` for detailed constraints:
```python
from pydantic import BaseModel, Field
from typing import Annotated

class Deal(BaseModel):
    id: int
    issuer: str = Field(min_length=1, max_length=200)
    amount: float = Field(gt=0)
```

## Response Handling

Return structured responses using models, status codes, and media types.

### Standard Response
Use `response_model` for automatic serialization and filtering:
```python
@app.get("/info", response_model=Info)
async def info() -> Info:
    return Info(service="api", version="1.0.0")
```

### Streaming Response
Return large payloads or logs using `StreamingResponse`:
```python
from fastapi.responses import StreamingResponse

@app.get("/export")
async def export_log() -> StreamingResponse:
    return StreamingResponse(iter_bytes(), media_type="text/plain")
```

## Error Handling

Provide consistent error structures and map exceptions to HTTP responses.

### Global Exception Handler
Register handlers to normalize errors:
```python
from fastapi import Request
from fastapi.responses import JSONResponse

class NotFoundError(Exception):
    pass

@app.exception_handler(NotFoundError)
async def not_found_handler(_: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"type": "not_found", "detail": str(exc)})
```

## Critical Considerations
- Validate limits for pagination to prevent resource abuse.
- Distinguish between input models (`In`) and output models (`Out`) to avoid leaking internal data.
- Stream large payloads instead of loading them into memory.
- Avoid leaking sensitive system details in error messages.

## Integration with LLM Agents
- Provide example payloads (both valid and invalid).
- Use descriptive names for parameters and fields.
- Document domain-specific exceptions and their intended HTTP status codes.
