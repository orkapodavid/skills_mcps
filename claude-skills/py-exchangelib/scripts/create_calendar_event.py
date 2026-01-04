#!/usr/bin/env python3
import os, datetime, zoneinfo
from dotenv import load_dotenv
from exchangelib import Credentials, Account, DELEGATE, CalendarItem

load_dotenv()
username = os.getenv("EXCHANGE_USERNAME")
password = os.getenv("EXCHANGE_PASSWORD")
primary = os.getenv("PRIMARY_SMTP")

account = Account(primary_smtp_address=primary, credentials=Credentials(username, password), autodiscover=True, access_type=DELEGATE)

tz = zoneinfo.ZoneInfo("UTC")
start = datetime.datetime.now(tz) + datetime.timedelta(hours=1)
end = start + datetime.timedelta(hours=1)
item = CalendarItem(account=account, folder=account.calendar, subject="LLM Meeting", start=start, end=end, location="Online")
item.save()
print("Created event:", item.id)
