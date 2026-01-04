#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from exchangelib import Credentials, Account, DELEGATE
from exchangelib.properties import NewMailEvent

load_dotenv()
username = os.getenv("EXCHANGE_USERNAME")
password = os.getenv("EXCHANGE_PASSWORD")
primary = os.getenv("PRIMARY_SMTP")

account = Account(primary_smtp_address=primary, credentials=Credentials(username, password), autodiscover=True, access_type=DELEGATE)

subscription_id = account.inbox.subscribe_to_streaming()
print("Streaming subscription:", subscription_id)

for notification in account.inbox.get_streaming_events(subscription_id, connection_timeout=1):
    for event in notification.events:
        if isinstance(event, NewMailEvent):
            print("New mail arrived")

account.inbox.unsubscribe(subscription_id)
