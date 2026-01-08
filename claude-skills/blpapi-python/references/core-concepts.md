# Core Concepts and Class Map

Bloomberg BLPAPI is event-driven. Construct a `Session`, open `Service`s, create `Request`s, send them, and iterate `Event`s and `Message`s.

## Principal Classes

### `Session`
The primary entry point for using the API. A `Session` can be used for both requests (snapshot data) and subscriptions (streaming data).
- **Synchronous Mode**: Use `session.nextEvent()` to poll for events.
- **Asynchronous Mode**: Provide an event handler callback at construction.

### `Service`
Describes the operations and schemas available for a particular data set (e.g., `//blp/refdata`). Use `session.getService()` after opening it.

### `Request`
Encapsulates parameters for a single operation (e.g., `ReferenceDataRequest`). Populated using the element-based interface.

### `Event`
A container for one or more messages. Common event types include:
- `RESPONSE`: Final response to a request.
- `PARTIAL_RESPONSE`: Intermediate response to a request.
- `SUBSCRIPTION_DATA`: Real-time data from a subscription.
- `SESSION_STATUS`: Updates on the session state.

### `Message`
The actual payload within an event. Messages are structured as a tree of `Element`s. Access data using getters like `getElementAsString`, `getElementAsFloat`, etc.

## Supporting Classes
- `Identity`: Represents user entitlements for authorized requests.
- `AuthOptions`: Configuration for authentication (e.g., Desktop API vs. Server API).
- `CorrelationId`: A user-supplied ID to match requests/subscriptions with their responses.
- `Name`: An optimized string wrapper for efficient element lookups.
- `Datetime`: Bloomberg-specific date and time class.
- `SubscriptionList`: A collection of topics and fields for real-time data.
