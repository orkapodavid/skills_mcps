# Error Handling Patterns

Type-safe error handling for Google API integrations using discriminated unions and the Result pattern.

## Discriminated Union for API Errors

Define a discriminated union that covers all expected error types:

```typescript
type ApiError =
  | { readonly kind: 'auth'; readonly message: string; readonly code: 401 | 403 }
  | { readonly kind: 'not_found'; readonly message: string; readonly resourceId: string }
  | { readonly kind: 'quota'; readonly message: string; readonly retryAfterMs: number }
  | { readonly kind: 'rate_limit'; readonly message: string; readonly retryAfterMs: number }
  | { readonly kind: 'server'; readonly message: string; readonly code: number; readonly requestId?: string }
  | { readonly kind: 'network'; readonly message: string; readonly cause?: Error }
  | { readonly kind: 'validation'; readonly message: string; readonly field?: string }
  | { readonly kind: 'unknown'; readonly message: string; readonly cause?: unknown };
```

### Error Constructors

Use factory functions for consistent error creation:

```typescript
const ApiErrors = {
  auth: (message: string, code: 401 | 403 = 401): ApiError => ({
    kind: 'auth', message, code,
  }),
  notFound: (message: string, resourceId: string): ApiError => ({
    kind: 'not_found', message, resourceId,
  }),
  quota: (message: string, retryAfterMs: number): ApiError => ({
    kind: 'quota', message, retryAfterMs,
  }),
  // ... other constructors
};
```

## Result Pattern

Prefer returning `Result<T, E>` over throwing exceptions for expected failures:

```typescript
type Result<T, E = ApiError> =
  | { readonly success: true; readonly data: T }
  | { readonly success: false; readonly error: E };

function ok<T>(data: T): Result<T, never> {
  return { success: true, data };
}

function err<E>(error: E): Result<never, E> {
  return { success: false, error };
}
```

### Wrapping API Calls

```typescript
async function listFiles(
  drive: drive_v3.Drive
): Promise<Result<DriveFile[], ApiError>> {
  try {
    const response = await drive.files.list({ pageSize: 10 });
    const files = response.data.files?.map(transformFile) ?? [];
    return ok(files);
  } catch (error) {
    return err(classifyError(error));
  }
}
```

## Error Classification

Classify caught errors into appropriate ApiError types:

```typescript
function classifyError(error: unknown): ApiError {
  if (error instanceof Error) {
    const apiError = error as { code?: number; response?: { status?: number } };
    const statusCode = apiError.code ?? apiError.response?.status;

    if (statusCode === 401) return ApiErrors.auth(error.message, 401);
    if (statusCode === 403) return ApiErrors.auth(error.message, 403);
    if (statusCode === 404) return ApiErrors.notFound(error.message, 'unknown');
    if (statusCode === 429) return ApiErrors.rateLimit(error.message, 60000);
    if (statusCode && statusCode >= 500) return ApiErrors.server(error.message, statusCode);
    if (error.message.includes('ENOTFOUND')) return ApiErrors.network(error.message, error);

    return ApiErrors.unknown(error.message, error);
  }
  return ApiErrors.unknown(String(error), error);
}
```

## Type Guards

Use type guards for conditional error handling:

```typescript
function isRetryableError(error: ApiError): boolean {
  return (
    error.kind === 'quota' ||
    error.kind === 'rate_limit' ||
    error.kind === 'server' ||
    error.kind === 'network'
  );
}

function isAuthError(error: ApiError): error is Extract<ApiError, { kind: 'auth' }> {
  return error.kind === 'auth';
}

function getRetryDelay(error: ApiError): number | null {
  if (error.kind === 'quota' || error.kind === 'rate_limit') {
    return error.retryAfterMs;
  }
  return null;
}
```

## Exhaustive Error Handling

Use switch statements for exhaustive handling:

```typescript
const result = await listFiles(drive);

if (!result.success) {
  switch (result.error.kind) {
    case 'auth':
      console.error('Auth failed:', result.error.code);
      // Redirect to login
      break;
    case 'quota':
      console.error('Quota exceeded. Retry after:', result.error.retryAfterMs);
      // Schedule retry
      break;
    case 'rate_limit':
      console.error('Rate limited. Retry after:', result.error.retryAfterMs);
      // Backoff logic
      break;
    case 'not_found':
      console.error('Resource not found:', result.error.resourceId);
      // Handle missing resource
      break;
    case 'server':
      console.error('Server error:', result.error.code);
      // Log and retry
      break;
    case 'network':
      console.error('Network error:', result.error.message);
      // Check connectivity
      break;
    case 'validation':
      console.error('Invalid input:', result.error.field);
      // Fix input
      break;
    case 'unknown':
      console.error('Unknown error:', result.error.message);
      // Log and alert
      break;
  }
}
```

## Logging Patterns

Log request IDs and relevant context:

```typescript
function logApiError(error: ApiError, context: Record<string, unknown>): void {
  const logEntry = {
    severity: isRetryableError(error) ? 'WARNING' : 'ERROR',
    errorKind: error.kind,
    message: error.message,
    ...context,
  };

  if (error.kind === 'server' && error.requestId) {
    logEntry.requestId = error.requestId;
  }

  console.error(JSON.stringify(logEntry));
}
```

## Best Practices

| Practice | Description |
|----------|-------------|
| Use Result for expected failures | Auth, not found, quota - these are expected |
| Throw for unexpected failures | Programming errors, invariant violations |
| Be specific with error types | Use discriminated union, not generic Error |
| Include context | Resource IDs, request IDs, retry timing |
| Classify at boundary | Convert exceptions to ApiError at API call site |
| Exhaustive handling | Switch on `kind` to handle all cases |

## Related Templates

- **`templates/ts/types.ts`** - Shared type definitions including ApiError
- **`templates/ts/utils/retry.ts`** - Retry logic using error classification
