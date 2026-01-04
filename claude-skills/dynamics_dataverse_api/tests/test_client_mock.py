import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# We need to import the package properly.
# Assume claude-skills is in PYTHONPATH, we import dynamics_dataverse_api.client
# But wait, if I run from here, I need to make sure I can import the package.
# Adding claude-skills to path.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from dynamics_dataverse_api.client import DataverseClient
from dynamics_dataverse_api.auth import DataverseAuth

class TestDataverseClient(unittest.TestCase):
    def setUp(self):
        self.config = {
            "DATAVERSE_ORG": "test-org",
            "CLIENT_ID": "test-client-id",
            "CLIENT_SECRET": "test-secret",
            "TENANT_ID": "test-tenant-id"
        }

    @patch("dynamics_dataverse_api.auth.DataverseAuth.get_access_token")
    def test_client_init(self, mock_get_token):
        client = DataverseClient(self.config)
        self.assertEqual(client.api_base_url, "https://test-org.api.crm.dynamics.com/api/data/v9.2")

    @patch("dynamics_dataverse_api.auth.DataverseAuth.get_access_token")
    @patch("requests.Session.request")
    def test_create(self, mock_request, mock_get_token):
        mock_get_token.return_value = "fake-token"

        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"accountid": "123", "name": "New Account"}
        mock_request.return_value = mock_response

        client = DataverseClient(self.config)
        result = client.create("accounts", {"name": "New Account"})

        self.assertEqual(result["accountid"], "123")
        mock_request.assert_called()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["json"], {"name": "New Account"})
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer fake-token")

    @patch("dynamics_dataverse_api.auth.DataverseAuth.get_access_token")
    @patch("requests.Session.request")
    def test_query(self, mock_request, mock_get_token):
        mock_get_token.return_value = "fake-token"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "value": [{"accountid": "1", "name": "A1"}, {"accountid": "2", "name": "A2"}],
            "@odata.nextLink": None
        }
        mock_request.return_value = mock_response

        client = DataverseClient(self.config)
        results = client.query("accounts", select=["name"], top=5)

        self.assertEqual(len(results), 2)
        # Verify query params were handled?
        # The URL in mock call should be checked if we want deep verification.
        args, kwargs = mock_request.call_args
        url = args[1]
        self.assertIn("$top=5", url)
        self.assertIn("$select=name", url)

if __name__ == "__main__":
    unittest.main()
