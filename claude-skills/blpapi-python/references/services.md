# Typical Services and Operations

Bloomberg services provide different types of data. Access them using the `//blp/` prefix.

## Reference and Historical Data (`//blp/refdata`)

The most commonly used service for snapshot and time-series data.

### `ReferenceDataRequest`
Retrieve current or static data for securities.
- **Inputs**: `securities`, `fields`, `overrides`.
- **Outputs**: Current values for the requested fields.

### `HistoricalDataRequest`
Fetch end-of-day historical time-series data.
- **Inputs**: `securities`, `fields`, `startDate`, `endDate`, `periodicitySelection` (DAILY, WEEKLY, MONTHLY, etc.).

### `FieldSearchRequest`
Search for available data fields and their metadata.

## Intraday Data (`//blp/intraday`)

Provides granular tick and bar data.

### `IntradayBarRequest`
Retrieve consolidated OHLC bars for a specific interval.
- **Inputs**: `security`, `eventType` (TRADE, BID, ASK), `interval` (in minutes), `startDateTime`, `endDateTime`.

### `IntradayTickRequest`
Fetch raw tick-by-tick data.
- **Inputs**: `security`, `eventTypes`, `startDateTime`, `endDateTime`.

## Market Data (`//blp/mktdata`)

Standard service for real-time streaming subscriptions. Use `SubscriptionList` to define what to watch.

## Discovering Schemas

Inspect service capabilities dynamically:
- `service.toString()`: Print the entire schema (operations and elements).
- `service.operations()`: List available operations.
- `service.getOperation(operationName)`: Get detailed schema for a specific operation.
- `request.toString()`: Show the populated structure of a request before sending.
- `message.toString()`: View the full structure of a received message.
