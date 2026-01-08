---
name: Bloomberg BLPAPI Python
description: This skill should be used when the user asks to "get Bloomberg data", "query reference data", "fetch historical prices", "subscribe to real-time market data", "manage BLPAPI sessions", or work with "Bloomberg Python bindings". Covers request-response and subscription patterns.
version: 1.0.0
---

# Bloomberg BLPAPI Python Skill

Equip LLM-powered coders to use Bloomberg Desktop API (BLPAPI) via Python for investment management workflows. This skill focuses on the official Python API and maps its event-driven model to practical tasks.

## Prerequisites and Installation

Bloomberg’s Python bindings are distributed via Bloomberg’s repository. A valid Bloomberg Terminal with API entitlement and Desktop API access is required.

- **Install**: `python -m pip install --index-url=https://blpapi.bloomberg.com/repository/releases/python/simple/ blpapi`
- **Setup**: Ensure the Bloomberg Terminal is running and authorized for the target services.

## Core Workflow

BLPAPI is event-driven. Follow this general procedure for all interactions:

1.  **Initialize**: Create `SessionOptions` and a `Session`.
2.  **Start**: Call `session.start()` to establish the connection.
3.  **Open Service**: Call `session.openService("//blp/...")` for the required data source.
4.  **Execute**:
    *   **Request/Response**: Create a `Request`, populate it, and call `session.sendRequest`.
    *   **Subscription**: Build a `SubscriptionList` and call `session.subscribe`.
5.  **Process**: Iterate through `Event`s and `Message`s to extract data.
6.  **Cleanup**: Call `session.stop()` when finished.

## Code Patterns

### Reference Data Request (Snapshot)
```python
import blpapi
from blpapi import Session, SessionOptions

session = Session(SessionOptions())
session.start()
session.openService("//blp/refdata")
service = session.getService("//blp/refdata")

request = service.createRequest("ReferenceDataRequest")
request.getElement("securities").appendValue("AAPL US Equity")
request.getElement("fields").appendValue("PX_LAST")

session.sendRequest(request)

while True:
    event = session.nextEvent()
    if event.eventType() in [blpapi.Event.PARTIAL_RESPONSE, blpapi.Event.RESPONSE]:
        for msg in event:
            print(msg.toString())
        if event.eventType() == blpapi.Event.RESPONSE:
            break
```

### Historical Data Request
```python
request = service.createRequest("HistoricalDataRequest")
request.set("security", "AAPL US Equity")
request.set("startDate", "20240101")
request.set("endDate", "20241231")
request.getElement("fields").appendValue("PX_LAST")
session.sendRequest(request)
```

### Market Data Subscription (Streaming)
```python
subs = blpapi.SubscriptionList()
subs.add("/AAPL US Equity", ["BID", "ASK", "LAST_PRICE"], "interval=1")
session.subscribe(subs)

while True:
    event = session.nextEvent()
    if event.eventType() == blpapi.Event.SUBSCRIPTION_DATA:
        for msg in event:
            print(msg.toString())
```

## Additional Resources

### Reference Files
Detailed documentation for advanced usage:
- **`references/core-concepts.md`** - Class hierarchy and event-driven model.
- **`references/services.md`** - Service types and operation schemas.
- **`references/deployment-production.md`** - Troubleshooting, threading, and production best practices.

### Examples
Working scripts in `examples/`:
- **`reference_data.py`** - Basic snapshot request.
- **`historical_data.py`** - Time-series data retrieval.
- **`intraday_bars.py`** - Intraday bar retrieval.
- **`subscribe_mktdata.py`** - Real-time subscription loop.
