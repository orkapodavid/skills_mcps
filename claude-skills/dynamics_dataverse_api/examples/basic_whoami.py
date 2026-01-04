import os
import sys

# Add parent directory to path to allow importing from local module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from client import DataverseClient
except ImportError:
    # If running from root without package install
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from dynamics_dataverse_api.client import DataverseClient

def main():
    # Ensure env vars are set
    required_env = ["DATAVERSE_ORG", "CLIENT_ID"]
    missing = [v for v in required_env if not os.environ.get(v)]
    if missing:
        print(f"Error: Missing environment variables: {', '.join(missing)}")
        print("Please set DATAVERSE_ORG, CLIENT_ID (and CLIENT_SECRET for confidential client).")
        return

    print("Initializing Dataverse Client...")
    client = DataverseClient()

    print("Calling WhoAmI...")
    # WhoAmI is a function or action. Usually Unbound Function: WhoAmI()
    try:
        response = client.invoke_function("WhoAmI")
        print(f"Success! User ID: {response.get('UserId')}")
        print(f"Business Unit ID: {response.get('BusinessUnitId')}")
    except Exception as e:
        print(f"Error calling WhoAmI: {e}")

if __name__ == "__main__":
    main()
