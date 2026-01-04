---
name: Dynamics Dataverse API
description: This skill should be used when the user wants to interact with Microsoft Dataverse (Dynamics 365) via Web API. It provides a clean, testable Python client for authentication, CRUD operations, queries, and executing functions/actions using MSAL and OData v4.
version: 0.1.0
---

# Dynamics Dataverse API Skill

This skill provides a Python client library for interacting with the Microsoft Dataverse Web API.

## capabilities

- **Authentication**: Microsoft Entra ID (Azure AD) via MSAL (Confidential and Public Client).
- **CRUD**: Create, Retrieve, Update, Delete entities.
- **Query**: OData query support ($select, $filter, $expand, $orderby, $top, $skip).
- **Functions & Actions**: Invoke bound and unbound functions and actions.
- **Batching**: Support for OData $batch operations.

## Usage

Import the client and auth modules to build scripts for Dataverse interaction.

### Authentication (`auth.py`)

Handles acquiring tokens from Microsoft Entra ID.

```python
from auth import get_access_token, DeviceCodeConfig
# or use the DataverseAuth class directly
```

### Client (`client.py`)

The main entry point for Dataverse operations.

```python
from client import DataverseClient

client = DataverseClient(config={...})
account = client.create("accounts", {"name": "New Account"})
```

### Batch (`batch.py`)

Helpers for batch operations.

## Configuration

The client can be configured via environment variables or a dictionary.

### Environment Variables

- `DATAVERSE_ORG`: Organization name (e.g., `contoso` for `https://contoso.api.crm.dynamics.com`).
- `TENANT_ID`: Azure Tenant ID.
- `CLIENT_ID`: Client (App) ID.
- `CLIENT_SECRET`: Client Secret (for Confidential Client).
- `AUTHORITY`: (Optional) Authority URL.
- `TOKEN_CACHE_PATH`: (Optional) Path to serializable token cache.

## Files

- `__init__.py`: Package initialization.
- `auth.py`: MSAL authentication logic.
- `client.py`: `DataverseClient` implementation.
- `batch.py`: OData batch request builder.
- `examples/`: Runnable examples.
