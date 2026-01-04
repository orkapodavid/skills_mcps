# Dynamics Dataverse API Skill

This skill provides a Python client library for interacting with the Microsoft Dataverse Web API (OData v4) using Microsoft Entra ID (MSAL) authentication.

## Features

- **Authentication**: Supports Confidential Client (Service Principal) and Public Client (Interactive) flows with token caching.
- **CRUD Operations**: Create, Read, Update, Delete for any entity set.
- **Querying**: Support for `$select`, `$filter`, `$expand`, `$orderby`, `$top`, `$skip` and automatic pagination.
- **Functions & Actions**: Generic invoker for bound and unbound operations.
- **Batching**: Helper for OData `$batch` requests.
- **Retries**: Automatic retry with backoff for 429 and 503 errors.

## Installation

This skill is designed to be used within the Claude environment or as a standalone Python package.

Prerequisites:
- `requests`
- `msal`

```bash
pip install requests msal
```

## Configuration

The client relies on environment variables or a configuration dictionary.

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATAVERSE_ORG` | The organization name (e.g., `contoso`) or full URL. | Yes |
| `CLIENT_ID` | Azure App Client ID. | Yes |
| `TENANT_ID` | Azure Tenant ID. | Yes (usually) |
| `CLIENT_SECRET` | Client Secret (for Service Principal). | No (if using Public Client) |
| `AUTHORITY` | Custom Authority URL. | No |
| `TOKEN_CACHE_PATH` | Path to save token cache (e.g., `token_cache.bin`). | No |

## Usage

### 1. Authentication & Setup

You can initialize the client with environment variables automatically:

```python
from dynamics_dataverse_api.client import DataverseClient

# Uses os.environ
client = DataverseClient()
```

Or pass a config dictionary:

```python
config = {
    "DATAVERSE_ORG": "contoso",
    "CLIENT_ID": "...",
    "CLIENT_SECRET": "...",
    "TENANT_ID": "..."
}
client = DataverseClient(config)
```

### 2. CRUD Operations

```python
# Create
response = client.create("accounts", {
    "name": "Contoso Ltd",
    "telephone1": "555-0100"
})
account_id = response.get("accountid") # Extract ID from response

# Read
account = client.get("accounts", account_id, select=["name", "telephone1"])

# Update
client.update("accounts", account_id, {"telephone1": "555-0101"})

# Delete
client.delete("accounts", account_id)
```

### 3. Queries

```python
accounts = client.query(
    "accounts",
    filter="startswith(name, 'Contoso')",
    select=["name", "accountid"],
    orderby="name asc",
    top=10
)
```

### 4. Functions & Actions

```python
# Unbound Function (WhoAmI)
user_info = client.invoke_function("WhoAmI")

# Bound Action (e.g., on an incident)
client.invoke_action("CloseIncident",
    payload={...},
    bound_entity=f"incidents({incident_id})"
)
```

## Examples

Runnable examples are located in the `examples/` directory.

- `examples/basic_whoami.py`: Authenticates and calls the `WhoAmI` function.
- `examples/crud_accounts.py`: Demonstrates full lifecycle of an Account record.

To run them:

```bash
export DATAVERSE_ORG="contoso"
export CLIENT_ID="your-client-id"
export CLIENT_SECRET="your-secret"
export TENANT_ID="your-tenant-id"

python examples/basic_whoami.py
```

## Azure App Registration

1. Go to Azure Portal > App Registrations.
2. Register a new app.
3. **API Permissions**: Add `Dynamics CRM` > `user_impersonation` (for Public Client) or `.default` (for Service Principal).
4. Grant Admin Consent if required.
5. Create a Client Secret (for Confidential Client).
6. Create an Application User in the Dataverse Environment (Power Platform Admin Center) associated with this App ID and assign roles (e.g., System Administrator).
