import os
import sys
import uuid
import time

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from client import DataverseClient
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from dynamics_dataverse_api.client import DataverseClient

def main():
    client = DataverseClient()

    # 1. Create an Account
    account_name = f"Test Account {uuid.uuid4().hex[:8]}"
    print(f"Creating account: {account_name}")

    # Assuming 'accounts' is the entity set name.
    # Note: OData often returns the ID in the header or body.
    # Our client.create returns the full response JSON if available.
    try:
        # Some Dataverse configs require more fields. This is minimal.
        create_response = client.create("accounts", {"name": account_name})

        # We need the ID.
        # Usually Dataverse returns the created entity if Prefer: return=representation is used (which we do).
        # But requests.post might not return JSON if status is 204.
        # With return=representation, it should be 201 Created with Body.

        if create_response and "accountid" in create_response:
             account_id = create_response["accountid"]
             print(f"Created Account ID: {account_id}")
        else:
             # Fallback: Query for it? Or maybe the client logic for create needs to be robust about extracting ID from Location header if body is empty?
             # For now, let's assume we got it or fail.
             print("Could not retrieve Account ID from response.")
             return

        # 2. Retrieve (Read)
        print("Retrieving account...")
        fetched_account = client.get("accounts", account_id, select=["name", "accountnumber"])
        print(f"Fetched: {fetched_account.get('name')}")

        # 3. Update
        print("Updating account...")
        client.update("accounts", account_id, {"name": f"{account_name} Updated"})

        # Verify Update
        updated_account = client.get("accounts", account_id, select=["name"])
        print(f"Updated Name: {updated_account.get('name')}")

        # 4. Query with Filter
        print("Querying accounts...")
        results = client.query(
            "accounts",
            filter=f"accountid eq '{account_id}'",
            select=["name"]
        )
        print(f"Query found {len(results)} records.")

        # 5. Delete
        print("Deleting account...")
        client.delete("accounts", account_id)
        print("Deleted.")

    except Exception as e:
        print(f"Operation failed: {e}")

if __name__ == "__main__":
    main()
