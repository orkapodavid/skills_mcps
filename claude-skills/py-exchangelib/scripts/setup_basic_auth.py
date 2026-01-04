#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from exchangelib import Credentials, Account, DELEGATE

load_dotenv()
username = os.getenv("EXCHANGE_USERNAME")
password = os.getenv("EXCHANGE_PASSWORD")
primary = os.getenv("PRIMARY_SMTP")

if not all([username, password, primary]):
    raise SystemExit("Missing env: EXCHANGE_USERNAME/EXCHANGE_PASSWORD/PRIMARY_SMTP")

creds = Credentials(username=username, password=password)
account = Account(primary_smtp_address=primary, credentials=creds, autodiscover=True, access_type=DELEGATE)
print(account.root.tree())
print("Connected as:", account.primary_smtp_address)
