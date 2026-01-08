# Bloomberg BLPAPI Python Skill (v3.16)

## Mission and Scope
This skill equips LLM-powered coders to use Bloomberg Desktop API (BLPAPI) via Python 3.16 for investment management workflows. It focuses on the official Python API documentation and maps its core classes and event-driven model to practical tasks such as reference data retrieval, historical time series, intraday bars/ticks, and real-time market data subscriptions. It also includes authorization, entitlements, error handling, and production concerns.

## Prerequisites and Installation
Bloomberg’s Python bindings are distributed via Bloomberg’s repository. You need a valid Bloomberg Terminal with API entitlement and access to the Desktop API.

- Install: `python -m pip install --index-url=https://blpapi.bloomberg.com/repository/releases/python/simple/ blpapi` [1]
- Requires Bloomberg Terminal running and appropriate entitlements. Authorization may be needed for restricted data.

## Core Concepts and Class Map
BLPAPI is event-driven. You construct a `Session`, open `Service`s, create `Request`s, send them, and iterate `Event`s and `Message`s.

- `Session`: Consumer session for requests or subscriptions; synchronous (poll `nextEvent()`) or asynchronous (event handler callbacks) [2]
- `Service`: Describes service operations and schemas; creates `Request`s for operations [3]
- `Request`: Encapsulates parameters for one operation; populated via element interface; sent via `Session.sendRequest()` [4]
- `Event`: Container of messages with types such as `RESPONSE`, `PARTIAL_RESPONSE`, `SUBSCRIPTION_DATA`, `SESSION_STATUS`, etc. [5]
- `Message`: The payload in an event; associated with service and correlation IDs; element-based accessors [6]
- `SubscriptionList`: Defines topics, fields, and options for real-time subscriptions [7]
- Supporting classes: `Identity`, `AuthOptions`, `CorrelationId`, `Element`, `Name`, etc. [2][3][4][5][6][7]

## Session Modes and Event Handling
- Synchronous: Call `session.nextEvent(timeout_ms)` and iterate messages per event. Timeouts yield `Event.TIMEOUT`. [2]
- Asynchronous: Provide `eventHandler(session, event)` at construction; the SDK invokes the handler from its threads. Prefer user-supplied `CorrelationId`s to avoid race conditions when callbacks arrive before API calls return. [2]

## Typical Services and Operations
Common consumer services (namespaces provided by Bloomberg):
- `//blp/refdata` (reference, historical, bulk, field search)
- `//blp/intraday` (intraday bars/ticks)
- `//blp/mktdata` (real-time subscriptions)

Operation names are created via `service.createRequest(operationName)`. Examples include:
- `ReferenceDataRequest`
- `HistoricalDataRequest`
- `IntradayBarRequest`
- `IntradayTickRequest`
- `FieldSearchRequest`
These names and request schemas are defined by their respective services; inspect with `service.getOperation(Name("..."))` or `service.toString()` to discover schemas. [3]

## Request/Response Pattern
1) Start session (sync or async) and open service (blocking `openService()` or `openServiceAsync()`). [2]
2) Get `Service` via `getService("//blp/refdata")`. [2][3]
3) Create `Request` with `service.createRequest("HistoricalDataRequest")` (for example). [3][4]
4) Populate request using `Request.set(name, value)` or `Element` methods: securities, fields, date ranges, periodicity, etc. [4]
5) Send with `session.sendRequest(request, identity=?, correlationId=?, eventQueue=?)`. Handle `PARTIAL_RESPONSE` followed by `RESPONSE`. [2]
6) Iterate `Event`s and `Message`s, read elements via getters (e.g., `getElementAsString`). [5][6]

## Subscription Pattern (Real-time)
1) Build `SubscriptionList` and add topic strings (security + field list + options). [7]
2) Call `session.subscribe(subscriptions, identity=?, requestLabel=?)`. [2][7]
3) Process `SUBSCRIPTION_STATUS` and `SUBSCRIPTION_DATA` events via sync `nextEvent()` or async callback. [5]
4) Manage correlation IDs and unsubscribe/resubscribe with updated options when needed. [2][7]

## Authorization and Identity
- Create an `Identity`: `session.createIdentity()` or `generateAuthorizedIdentity(AuthOptions, cid)`; monitor `AUTHORIZATION_STATUS`, `TOKEN_STATUS`, and `SERVICE_STATUS` events. [2]
- Send authorization requests if service requires: `session.sendAuthorizationRequest(service.createAuthorizationRequest(...), identity, cid, queue)`. [2][3]
- Use `getAuthorizedIdentity(correlationId)` to retrieve authorized identities for requests or subscriptions. [2]

## Error Handling and Correlation IDs
- For requests: Expect `PARTIAL_RESPONSE` then final `RESPONSE`; failures yield `REQUEST_STATUS`. Correlation ID may be reused after final event. [2]
- For subscriptions: Watch `SUBSCRIPTION_STATUS` and handle `CANCELLED`, `PENDING_CANCELLATION`, `SUBSCRIBED`, `SUBSCRIBING`, `UNSUBSCRIBED` states. [2]
- Prefer user-generated `CorrelationId`s in async mode to avoid interpretation issues if events arrive before calls return. [2]

## Examples
Below are condensed patterns; see `examples/` for runnable scripts.

### Reference Data Request (refdata)
```python
import blpapi
from blpapi import Session, SessionOptions, Name

options = SessionOptions()
session = Session(options)
session.start()
session.openService("//blp/refdata")
service = session.getService("//blp/refdata")

# e.g., request security descriptive fields
request = service.createRequest("ReferenceDataRequest")
securities = request.getElement("securities")
securities.appendValue("AAPL US Equity")
fields = request.getElement("fields")
fields.appendValue("PX_LAST")
fields.appendValue("DS002")  # Description field example

cid = blpapi.CorrelationId(1)
session.sendRequest(request, correlationId=cid)

while True:
    event = session.nextEvent()
    if event.eventType() == blpapi.Event.PARTIAL_RESPONSE or event.eventType() == blpapi.Event.RESPONSE:
        for msg in event:
            # Access elements from message
            print(msg.toString())
        if event.eventType() == blpapi.Event.RESPONSE:
            break
```

### Historical Data Request
```python
session.openService("//blp/refdata")
service = session.getService("//blp/refdata")
request = service.createRequest("HistoricalDataRequest")
request.set(Name("security"), "AAPL US Equity")
request.set(Name("startDate"), "20240101")
request.set(Name("endDate"), "20241231")
request.set(Name("periodicitySelection"), "DAILY")
fields = request.getElement("fields")
fields.appendValue("PX_LAST")

cid = blpapi.CorrelationId(2)
session.sendRequest(request, correlationId=cid)
# Iterate events/messages as above
```

### Intraday Bars
```python
session.openService("//blp/intraday")
service = session.getService("//blp/intraday")
request = service.createRequest("IntradayBarRequest")
request.set(Name("security"), "AAPL US Equity")
request.set(Name("eventType"), "TRADE")
request.set(Name("interval"), 5)  # minutes
request.set(Name("startDateTime"), blpapi.Datetime(2024,1,2,9,30))
request.set(Name("endDateTime"), blpapi.Datetime(2024,1,2,16,0))
request.set(Name("gapFillInitialBar"), True)

cid = blpapi.CorrelationId(3)
session.sendRequest(request, correlationId=cid)
```

### Market Data Subscription
```python
subs = blpapi.SubscriptionList()
subs.add(topic="/AAPL US Equity", fields=["BID", "ASK", "LAST_PRICE"], options=["interval=1"])
session.subscribe(subs)

while True:
    event = session.nextEvent()
    if event.eventType() == blpapi.Event.SUBSCRIPTION_DATA:
        for msg in event:
            print(msg.toString())
```

## Discovering Schemas
Use these tools to inspect schemas dynamically:
- `service.operations()` and `service.getOperation(Name("..."))` to enumerate/confirm operation names. [3]
- `service.toString()` to view service schema; `Request.toString()` to inspect populated request; `Message.toString()` for payloads. [3][4][6]
- `Name` class for efficient keys in element access. [8]

## Production Guidance
- Entitlements: Some operations and fields require authorization; ensure identities are authorized and entitlements are checked. [2]
- Correlation IDs: Manage lifecycle; do not aggressively reuse in async mode; cancel or await final response before reuse. [2]
- Threading: Asynchronous handlers run on SDK threads; ensure thread-safe data structures. [2]
- Performance: Prefer event queues; snapshot request templates can reduce latency by servicing from cache. [2]
- Diagnostics: Use `requestLabel` and request/message `getRequestId()` when contacting Bloomberg for support. [4][6]

## Troubleshooting
- `InvalidStateException` on `getService`: Service not opened; call `openService()` first. [2]
- `REQUEST_STATUS` events: Inspect messages for failure reason; check entitlements and parameters. [5]
- Subscription states stuck at `SUBSCRIBING`: Verify topic format, fields, and options; check authorization. [2]
- Timeouts: `nextEvent()` with small timeout may return `TIMEOUT`; increase timeout or use async mode. [2][5]
- Multiple subscriptions and messages: If dedup desired, enable `allowMultipleCorrelatorsPerMsg` in `SessionOptions`. [6]

## References
1. API Library – Bloomberg Professional Services. https://www.bloomberg.com/professional/support/api-library/
2. blpapi.Session — BLPAPI Python 3.16. https://bloomberg.github.io/blpapi-docs/python/3.16/_autosummary/blpapi.Session.html
3. blpapi.Service — BLPAPI Python 3.16. https://bloomberg.github.io/blpapi-docs/python/3.16/_autosummary/blpapi.Service.html
4. blpapi.Request — BLPAPI Python 3.16. https://bloomberg.github.io/blpapi-docs/python/3.16/_autosummary/blpapi.Request.html
5. blpapi.Event — BLPAPI Python 3.16. https://bloomberg.github.io/blpapi-docs/python/3.16/_autosummary/blpapi.Event.html
6. blpapi.Message — BLPAPI Python 3.16. https://bloomberg.github.io/blpapi-docs/python/3.16/_autosummary/blpapi.Message.html
7. blpapi.SubscriptionList — BLPAPI Python 3.16. https://bloomberg.github.io/blpapi-docs/python/3.16/_autosummary/blpapi.SubscriptionList.html
8. blpapi.Name — BLPAPI Python 3.16. https://bloomberg.github.io/blpapi-docs/python/3.16/_autosummary/blpapi.Name.html
