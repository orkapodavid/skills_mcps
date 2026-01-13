"""
Requires: pip install authlib httpx
Demonstrates OAuth2 client credentials flow with Authlib for httpx.
"""
import os
from authlib.integrations.httpx_client import OAuth2Client

TOKEN_URL = os.getenv("TOKEN_URL", "https://example.com/oauth/token")
CLIENT_ID = os.getenv("CLIENT_ID", "your_client_id")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "your_client_secret")
API_URL = os.getenv("API_URL", "https://api.example.com/data")

with OAuth2Client(client_id=CLIENT_ID, client_secret=CLIENT_SECRET) as client:
    token = client.fetch_token(TOKEN_URL, grant_type="client_credentials")
    r = client.get(API_URL)
    r.raise_for_status()
    print(r.json())
