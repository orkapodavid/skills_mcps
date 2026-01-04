import os
import atexit
import logging
from typing import Optional, Dict, Any, List
import msal

# Logger setup
logger = logging.getLogger(__name__)

class DataverseAuth:
    """
    Handles authentication with Microsoft Dataverse using MSAL.
    Supports both Confidential Client (Service Principal) and Public Client (User) flows.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the auth handler.

        Args:
            config: Dictionary containing config values. If None, uses environment variables.
                    Keys: TENANT_ID, CLIENT_ID, CLIENT_SECRET, AUTHORITY, TOKEN_CACHE_PATH, DATAVERSE_ORG
        """
        self.config = config or {}
        self._load_config_from_env()

        self.tenant_id = self.config.get("TENANT_ID")
        self.client_id = self.config.get("CLIENT_ID")
        self.client_secret = self.config.get("CLIENT_SECRET")
        self.org = self.config.get("DATAVERSE_ORG")

        if not self.org:
             # Try to construct or warn? For now, we need org to define scope.
             pass

        self.authority = self.config.get("AUTHORITY") or f"https://login.microsoftonline.com/{self.tenant_id}"
        self.token_cache_path = self.config.get("TOKEN_CACHE_PATH")

        # Scopes
        # If org is just name, construct url. If url, use as is?
        # Requirement says Scope: https://{org}.crm.dynamics.com/.default or user_impersonation
        self.resource_url = self._get_resource_url(self.org)

        self.app = None
        self.token_cache = msal.SerializableTokenCache()

        if self.token_cache_path and os.path.exists(self.token_cache_path):
            with open(self.token_cache_path, "r") as f:
                self.token_cache.deserialize(f.read())

        if self.token_cache_path:
            atexit.register(self._save_cache)

    def _load_config_from_env(self):
        """Load missing config from environment variables."""
        env_map = {
            "TENANT_ID": "TENANT_ID",
            "CLIENT_ID": "CLIENT_ID",
            "CLIENT_SECRET": "CLIENT_SECRET",
            "DATAVERSE_ORG": "DATAVERSE_ORG",
            "AUTHORITY": "AUTHORITY",
            "TOKEN_CACHE_PATH": "TOKEN_CACHE_PATH"
        }
        for key, env_var in env_map.items():
            if key not in self.config:
                val = os.getenv(env_var)
                if val:
                    self.config[key] = val

    def _get_resource_url(self, org: str) -> str:
        """Constructs the resource URL from org name if needed."""
        if not org:
            return ""
        if org.startswith("http"):
            return org.rstrip("/")
        # Assume it's just the org name
        # Determine region? Defaulting to crm.dynamics.com (North America/Global) if not specified isn't safe for all.
        # But requirement says: https://{org}.api.crm.dynamics.com/api/data/v9.2 (for API)
        # Scope usually uses https://{org}.crm.dynamics.com
        return f"https://{org}.crm.dynamics.com"

    def _save_cache(self):
        """Saves the token cache to disk."""
        if self.token_cache_path and self.token_cache.has_state_changed:
            with open(self.token_cache_path, "w") as f:
                f.write(self.token_cache.serialize())

    def _get_app(self):
        """Initializes the MSAL application."""
        if self.app:
            return self.app

        if self.client_secret:
            # Confidential Client
            self.app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=self.authority,
                client_credential=self.client_secret,
                token_cache=self.token_cache
            )
        else:
            # Public Client
            self.app = msal.PublicClientApplication(
                self.client_id,
                authority=self.authority,
                token_cache=self.token_cache
            )
        return self.app

    def get_access_token(self) -> str:
        """
        Acquires a token. Tries cache first, then client credentials or interactive flow.
        """
        if not self.client_id:
             raise ValueError("CLIENT_ID is required for authentication.")

        app = self._get_app()

        # Define scopes
        if self.client_secret:
             scopes = [f"{self.resource_url}/.default"]
        else:
             scopes = [f"{self.resource_url}/user_impersonation"]

        # Try silent acquisition
        accounts = app.get_accounts()
        result = None
        if accounts:
            result = app.acquire_token_silent(scopes, account=accounts[0])

        if not result:
            if self.client_secret:
                result = app.acquire_token_for_client(scopes=scopes)
            else:
                # Public client interactive
                # Note: In a headless agent environment, interactive login might hang or fail.
                # But requirement says "Public client (interactive)".
                # We assume this code might run locally by user.
                logger.info("Initiating interactive authentication...")
                result = app.acquire_token_interactive(scopes=scopes)

        if "access_token" in result:
            return result["access_token"]
        else:
            error = result.get("error")
            desc = result.get("error_description")
            raise Exception(f"Could not acquire token: {error} - {desc}")

def get_access_token(config: Optional[Dict[str, Any]] = None) -> str:
    """Helper function to get token quickly."""
    auth = DataverseAuth(config)
    return auth.get_access_token()
