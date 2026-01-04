#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from exchangelib import Account, DELEGATE, O365InteractiveConfiguration

load_dotenv()
client_id = os.getenv("MSAL_CLIENT_ID")
username = os.getenv("MSAL_USERNAME")

if not all([client_id, username]):
    raise SystemExit("Missing env: MSAL_CLIENT_ID/MSAL_USERNAME")

account = Account(primary_smtp_address=username,
                  config=O365InteractiveConfiguration(client_id=client_id, username=username),
                  access_type=DELEGATE,
                  autodiscover=False)
print(account.root.tree())
print("Connected via MSAL interactive:", account.primary_smtp_address)
