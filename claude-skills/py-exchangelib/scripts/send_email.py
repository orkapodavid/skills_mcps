#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from exchangelib import Credentials, Account, DELEGATE, Message, Mailbox, HTMLBody

load_dotenv()
username = os.getenv("EXCHANGE_USERNAME")
password = os.getenv("EXCHANGE_PASSWORD")
primary = os.getenv("PRIMARY_SMTP")

if not all([username, password, primary]):
    raise SystemExit("Missing env: EXCHANGE_USERNAME/EXCHANGE_PASSWORD/PRIMARY_SMTP")

account = Account(primary_smtp_address=primary, credentials=Credentials(username, password), autodiscover=True, access_type=DELEGATE)

m = Message(
    account=account,
    subject="LLM Test Message",
    body=HTMLBody("<html><body>Hello from exchangelib skill</body></html>"),
    to_recipients=[Mailbox(email_address=primary)],
)
m.send_and_save()
print("Sent to", primary)
