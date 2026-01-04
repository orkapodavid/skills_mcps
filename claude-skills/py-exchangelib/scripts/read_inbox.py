#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from exchangelib import Credentials, Account, DELEGATE

load_dotenv()
username = os.getenv("EXCHANGE_USERNAME")
password = os.getenv("EXCHANGE_PASSWORD")
primary = os.getenv("PRIMARY_SMTP")

account = Account(primary_smtp_address=primary, credentials=Credentials(username, password), autodiscover=True, access_type=DELEGATE)

for msg in account.inbox.filter(subject__icontains="LLM").order_by("-datetime_received")[:10]:
    print(msg.subject, "from", getattr(msg.sender, "email_address", None))
