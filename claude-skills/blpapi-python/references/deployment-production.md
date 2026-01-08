# Deployment, Production, and Troubleshooting

## Authorization and Identity

Authorization ensures that the application has permission to access specific data.

- **Identity Lifecycle**: Create an `Identity` object and use `session.sendAuthorizationRequest` if the service requires it.
- **Entitlements**: Always check for `AUTHORIZATION_STATUS` and `SERVICE_STATUS` events.
- **Desktop API**: Usually relies on the logged-in Terminal user's entitlements.

## Error Handling

- **Request Failures**: Monitor `REQUEST_STATUS` events. Inspect the message for error codes and descriptions.
- **Subscription Errors**: Watch `SUBSCRIPTION_STATUS`. Handle states like `CANCELLED` or `SUBSCRIBING` (stuck).
- **Correlation IDs**: Manage IDs carefully to match responses with requests, especially in asynchronous mode.

## Production Guidance

- **Threading**: In asynchronous mode, event handlers run on SDK-managed threads. Ensure all shared data structures are thread-safe.
- **Resource Management**: Always call `session.stop()` to release resources and close connections gracefully.
- **Performance**: Use `EventQueue` for high-throughput responses. Use `Name` objects instead of strings for element access in tight loops.
- **Logging**: Log `CorrelationId` and `Message.toString()` for debugging complex response issues.

## Troubleshooting Common Issues

| Issue | Probable Cause | Resolution |
| :--- | :--- | :--- |
| `InvalidStateException` | Service not opened | Call `session.openService()` and wait for `SERVICE_STATUS` or use `openServiceAsync`. |
| No data returned | Missing entitlements or invalid parameters | Check message content for `RESPONSE` or `REQUEST_STATUS` error details. |
| Timeouts | Terminal not running or network issue | Ensure Bloomberg Terminal is logged in and API is enabled. Check `SessionOptions`. |
| Stuck `SUBSCRIBING` | Invalid topic or field | Verify security string (e.g., `AAPL US Equity`) and field mnemonic (e.g., `LAST_PRICE`). |
| Callback races | Async events before call returns | Use user-generated `CorrelationId` to match events reliably. |
