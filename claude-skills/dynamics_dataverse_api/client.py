import requests
import time
import logging
from typing import Optional, Dict, Any, List, Union
from urllib.parse import urlencode

from .auth import DataverseAuth
from .batch import BatchRequestBuilder

# Logger setup
logger = logging.getLogger(__name__)

class DataverseClient:
    """
    Client for interacting with Microsoft Dataverse Web API.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Dataverse client.

        Args:
            config: Configuration dictionary.
                    Must include DATAVERSE_ORG or API_URL.
                    Also passed to DataverseAuth.
        """
        self.config = config or {}
        self.auth = DataverseAuth(self.config)

        self.org = self.config.get("DATAVERSE_ORG") or os.getenv("DATAVERSE_ORG")

        # Base URL construction
        # Pattern: https://{org}.api.crm.dynamics.com/api/data/v9.2
        if self.org and not self.org.startswith("http"):
            self.api_base_url = f"https://{self.org}.api.crm.dynamics.com/api/data/v9.2"
        elif self.org:
             # If full URL provided, assume it might lack api/data/v9.2
             if "api/data" not in self.org:
                 self.api_base_url = f"{self.org.rstrip('/')}/api/data/v9.2"
             else:
                 self.api_base_url = self.org
        else:
            raise ValueError("DATAVERSE_ORG config or env var is required.")

        self.session = requests.Session()
        self.session.headers.update({
            "OData-Version": "4.0",
            "OData-MaxVersion": "4.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

    def _get_headers(self) -> Dict[str, str]:
        """Gets headers with fresh token."""
        token = self.auth.get_access_token()
        return {
            "Authorization": f"Bearer {token}"
        }

    def _handle_response(self, response: requests.Response) -> Any:
        """
        Handles the HTTP response, checks for errors, and parses JSON.
        """
        if response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get("error", {}).get("message", response.text)
            except ValueError:
                message = response.text

            logger.error(f"Dataverse API Error: {response.status_code} - {message}")
            response.raise_for_status() # Raises Requests HTTPError

        if response.status_code == 204: # No Content
            return None

        try:
            return response.json()
        except ValueError:
            return response.content

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Any:
        """
        Internal helper to make HTTP requests with retry logic.
        """
        url = f"{self.api_base_url}/{endpoint.lstrip('/')}" if not endpoint.startswith("http") else endpoint
        headers = self._get_headers()
        # Merge with any custom headers
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        retries = 3
        backoff = 1

        for attempt in range(retries):
            try:
                response = self.session.request(method, url, headers=headers, **kwargs)

                # Retry on 429 (Too Many Requests) or 503 (Service Unavailable)
                if response.status_code in [429, 503]:
                    retry_after = response.headers.get("Retry-After")
                    sleep_time = int(retry_after) if retry_after else backoff * (2 ** attempt)
                    logger.warning(f"Rate limited or service unavailable. Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                    continue

                return self._handle_response(response)

            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                if attempt == retries - 1:
                    raise
                time.sleep(backoff * (2 ** attempt))

    def create(self, entity_set: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new entity record.
        Returns the full response dictionary (the created entity), which includes the ID.
        """
        headers = {"Prefer": "return=representation"}
        return self._make_request("POST", entity_set, json=data, headers=headers)

    def get(self, entity_set: str, entity_id: str, select: Optional[List[str]] = None, expand: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Retrieves a single entity by ID.
        """
        params = {}
        if select:
            params["$select"] = ",".join(select)
        if expand:
            params["$expand"] = ",".join(expand)

        query_string = urlencode(params, safe="$(),'")
        endpoint = f"{entity_set}({entity_id})"
        if query_string:
            endpoint += f"?{query_string}"

        return self._make_request("GET", endpoint)

    def update(self, entity_set: str, entity_id: str, data: Dict[str, Any]) -> None:
        """
        Updates an entity (PATCH).
        """
        endpoint = f"{entity_set}({entity_id})"
        self._make_request("PATCH", endpoint, json=data)

    def delete(self, entity_set: str, entity_id: str) -> None:
        """
        Deletes an entity.
        """
        endpoint = f"{entity_set}({entity_id})"
        self._make_request("DELETE", endpoint)

    def query(self, entity_set: str, select: Optional[List[str]] = None, filter: Optional[str] = None,
              expand: Optional[List[str]] = None, orderby: Optional[str] = None,
              top: Optional[int] = None, skip: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Queries for entities. Handles pagination automatically.
        """
        params = {}
        if select:
            params["$select"] = ",".join(select)
        if filter:
            params["$filter"] = filter
        if expand:
            params["$expand"] = ",".join(expand)
        if orderby:
            params["$orderby"] = orderby
        if top:
            params["$top"] = top
        if skip:
            params["$skip"] = skip

        endpoint = entity_set
        results = []

        while endpoint:
            # If endpoint is full URL (nextLink), _make_request handles it
            query_string = urlencode(params, safe="$(),'") if not endpoint.startswith("http") and params else ""
            if query_string and "?" not in endpoint:
                url = f"{endpoint}?{query_string}"
            elif query_string:
                url = f"{endpoint}&{query_string}"
            else:
                url = endpoint

            # Clear params after first request if we are following nextLink
            # Actually nextLink usually contains params.
            if endpoint.startswith("http"):
                 url = endpoint
                 params = {} # Clear params so we don't append them again

            response = self._make_request("GET", url)

            if "value" in response:
                results.extend(response["value"])

            endpoint = response.get("@odata.nextLink")

            # If user specified top, we might stop?
            # But OData server side paging might return nextLink even if top is satisfied?
            # Usually top is per page or total?
            # If the user asks for Top 10, and server returns 10, there is no next link usually.
            # If server enforces max page size, it returns nextLink.
            # We will follow nextLink until done or if we don't want to fetch all?
            # For now, let's fetch all available pages (standard client behavior).
            # But be careful with huge datasets.

        return results

    def invoke_function(self, name: str, params: Optional[Dict[str, Any]] = None, bound_entity: Optional[str] = None) -> Any:
        """
        Invokes a Dataverse function.

        Args:
            name: Name of the function.
            params: Dictionary of parameters.
            bound_entity: If bound, provide path like "accounts(id)".
        """
        # Functions are GET requests. Parameters are passed in parentheses or as query params?
        # Specification says: FunctionName(Param1=@p1,Param2=@p2)?@p1=Value1&@p2=Value2
        # Or inline: FunctionName(Param1='Value1',Param2=2)

        param_str = ""
        if params:
            # Simple parameter serialization
            parts = []
            for k, v in params.items():
                if isinstance(v, str):
                    parts.append(f"{k}='{v}'")
                else:
                    parts.append(f"{k}={v}")
            param_str = "(" + ",".join(parts) + ")"
        else:
            param_str = "()"

        endpoint = f"{bound_entity}/{name}{param_str}" if bound_entity else f"{name}{param_str}"

        # If function is unbound, it is at root.
        # But wait, if it's Unbound, we just call name(params).

        return self._make_request("GET", endpoint)

    def invoke_action(self, name: str, payload: Optional[Dict[str, Any]] = None, bound_entity: Optional[str] = None) -> Any:
        """
        Invokes a Dataverse action (POST).

        Args:
            name: Name of the action.
            payload: JSON payload for the action.
            bound_entity: If bound, provide path like "accounts(id)".
        """
        endpoint = f"{bound_entity}/Microsoft.Dynamics.CRM.{name}" if bound_entity else name
        # Note: Unbound actions often don't need the Microsoft.Dynamics.CRM prefix if strictly using action name,
        # but bound ones often do. However, the user might provide the full name.
        # Let's assume user provides the name they want to call.
        # Re-reading requirement: "POST /{actionName} with parameters payload"

        endpoint = f"{bound_entity}/{name}" if bound_entity else name

        return self._make_request("POST", endpoint, json=payload)

    def batch(self, operations: List[Dict[str, Any]]) -> Any:
        """
        Execute a batch request using BatchRequestBuilder.

        Args:
            operations: List of operation dictionaries. Each dict should have:
                        - method: "POST", "PATCH", "DELETE", etc.
                        - url: Relative URL (e.g. "accounts")
                        - body: (Optional) JSON body
                        - content_id: (Optional) Int for referencing in changeset
        """
        builder = BatchRequestBuilder(self)
        for op in operations:
            builder.add_request(
                method=op.get("method"),
                url=op.get("url"),
                body=op.get("body"),
                content_id=op.get("content_id")
            )
        return builder.execute()
