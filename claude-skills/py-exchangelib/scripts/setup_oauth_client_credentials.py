#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from exchangelib import Account, Configuration, OAuth2Credentials, OAUTH2, Identity

load_dotenv()
client_id = os.getenv("OAUTH_CLIENT_ID")
client_secret = os.getenv("OAUTH_CLIENT_SECRET")
tenant_id = os.getenv("OAUTH_TENANT_ID")
identity_primary = os.getenv("OAUTH_IDENTITY_PRIMARY_SMTP")
primary = os.getenv("PRIMARY_SMTP")

if not all([client_id, client_secret, tenant_id, primary]):
    raise SystemExit("Missing env: OAUTH_CLIENT_ID/OAUTH_CLIENT_SECRET/OAUTH_TENANT_ID/PRIMARY_SMTP")

creds = OAuth2Credentials(client_id=client_id, client_secret=client_secret, tenant_id=tenant_id,
                          identity=Identity(primary_smtp_address=identity_primary) if identity_primary else None)
config = Configuration(credentials=creds, auth_type=OAUTH2)
account = Account(primary_smtp_address=primary, config=config, autodiscover=True)
print("Connected (app impersonation) to:", account.primary_smtp_address)
