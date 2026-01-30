# Pagination, Retries, and Quotas

Type-safe patterns for handling pagination, implementing retries, and managing API quotas.

## Pagination

### Async Iterator Pattern

Use async generators for type-safe, memory-efficient pagination:

```typescript
interface PaginatedResponse<T> {
  readonly items: T[];
  readonly nextPageToken?: PageToken;
}

interface PageFetcher<T> {
  (pageToken?: PageToken): Promise<Result<PaginatedResponse<T>, ApiError>>;
}

async function* paginate<T>(
  fetcher: PageFetcher<T>,
  options: PaginationOptions = {}
): AsyncGenerator<Result<T, ApiError>, void, unknown> {
  const maxPages = options.maxPages ?? 100;
  let pageToken = options.pageToken;
  let pageCount = 0;

  while (pageCount < maxPages) {
    const result = await fetcher(pageToken);

    if (!result.success) {
      yield err(result.error);
      return;
    }

    for (const item of result.data.items) {
      yield ok(item);
    }

    pageToken = result.data.nextPageToken;
    pageCount++;

    if (!pageToken) break;
  }
}
```

### Usage Examples

```typescript
// Stream items one at a time
for await (const result of paginate(fetcher)) {
  if (!result.success) {
    console.error('Pagination error:', result.error);
    break;
  }
  processItem(result.data);
}

// Collect up to N items
const files = await collectUpTo(fetcher, 100);

// Find first matching item
const match = await findFirst(fetcher, file => file.name.includes('report'));
```

### Creating Page Fetchers

Wrap googleapis list methods:

```typescript
function createPageFetcher<TResponse, TItem>(
  listFn: (params: { pageToken?: string }) => Promise<{ data: TResponse }>,
  extractItems: (response: TResponse) => TItem[] | undefined,
  extractNextToken: (response: TResponse) => string | undefined
): PageFetcher<TItem> {
  return async (pageToken?: PageToken) => {
    try {
      const response = await listFn({ pageToken });
      return ok({
        items: extractItems(response.data) ?? [],
        nextPageToken: extractNextToken(response.data) 
          ? createPageToken(extractNextToken(response.data)!) 
          : undefined,
      });
    } catch (error) {
      return err(classifyError(error));
    }
  };
}

// Usage with Drive API
const driveFetcher = createPageFetcher(
  (params) => drive.files.list({ ...params, pageSize: 100 }),
  (res) => res.files,
  (res) => res.nextPageToken
);
```

## Retries

### Exponential Backoff with Jitter

```typescript
interface RetryOptions {
  readonly maxRetries: number;
  readonly initialDelayMs: number;
  readonly maxDelayMs: number;
  readonly jitterFactor: number;
}

const DEFAULT_RETRY_OPTIONS: RetryOptions = {
  maxRetries: 3,
  initialDelayMs: 1000,
  maxDelayMs: 30000,
  jitterFactor: 0.2,
};

function calculateBackoffDelay(attempt: number, options: RetryOptions): number {
  // Exponential: initialDelay * 2^attempt
  const exponentialDelay = options.initialDelayMs * Math.pow(2, attempt);
  const cappedDelay = Math.min(exponentialDelay, options.maxDelayMs);
  
  // Jitter to prevent thundering herd
  const jitter = cappedDelay * options.jitterFactor * Math.random();
  return Math.floor(cappedDelay + jitter);
}
```

### Type-Safe Retry Wrapper

```typescript
async function withRetry<T>(
  operation: () => Promise<Result<T, ApiError>>,
  options: Partial<RetryOptions> = {}
): Promise<Result<T, ApiError>> {
  const opts = { ...DEFAULT_RETRY_OPTIONS, ...options };
  let lastError: ApiError | undefined;

  for (let attempt = 0; attempt <= opts.maxRetries; attempt++) {
    const result = await operation();

    if (result.success) return result;

    lastError = result.error;

    // Don't retry non-retryable errors
    if (!isRetryableError(result.error)) return result;

    if (attempt === opts.maxRetries) break;

    // Use server-provided delay if available
    const serverDelay = getRetryDelay(result.error);
    const delay = serverDelay ?? calculateBackoffDelay(attempt, opts);

    console.log(
      `[Retry] Attempt ${attempt + 1}/${opts.maxRetries} failed. ` +
      `Retrying in ${delay}ms...`
    );

    await sleep(delay);
  }

  return err(lastError ?? ApiErrors.unknown('All retries exhausted'));
}
```

### Retryable vs Non-Retryable Errors

| Error Type | Retryable | Reason |
|------------|-----------|--------|
| `quota` | ✅ | Temporary, retry after delay |
| `rate_limit` | ✅ | Temporary, respect Retry-After |
| `server` (5xx) | ✅ | Transient server issues |
| `network` | ✅ | Connection problems |
| `auth` | ❌ | Bad credentials, won't change |
| `not_found` | ❌ | Resource doesn't exist |
| `validation` | ❌ | Invalid request, fix input |

## Quotas

### Understanding Google API Quotas

| Quota Type | Description | Typical Limit |
|------------|-------------|---------------|
| Per-minute | Requests per project per minute | 100-10000 |
| Per-day | Requests per project per day | 10000-unlimited |
| Per-user | Requests per user per minute | 10-100 |
| Concurrent | Simultaneous requests | 10-100 |

### Quota-Aware Design

```typescript
interface QuotaConfig {
  readonly requestsPerMinute: number;
  readonly requestsPerDay: number;
  readonly concurrentRequests: number;
}

class QuotaTracker {
  private minuteRequests = 0;
  private minuteStart = Date.now();

  async acquire(): Promise<boolean> {
    const now = Date.now();
    
    // Reset minute counter
    if (now - this.minuteStart > 60000) {
      this.minuteRequests = 0;
      this.minuteStart = now;
    }

    if (this.minuteRequests >= this.config.requestsPerMinute) {
      return false; // Quota exhausted
    }

    this.minuteRequests++;
    return true;
  }
}
```

### Request ID Tracking

Track request IDs for debugging and quota auditing:

```typescript
function extractRequestId(response: any): RequestId | undefined {
  const headers = response.headers;
  const requestId = headers?.['x-guploader-uploadid'] 
    ?? headers?.['x-goog-request-id'];
  return requestId ? (requestId as RequestId) : undefined;
}

async function loggedApiCall<T>(
  operation: () => Promise<T>,
  context: { api: string; method: string }
): Promise<T> {
  const startTime = Date.now();
  try {
    const result = await operation();
    console.log({
      api: context.api,
      method: context.method,
      durationMs: Date.now() - startTime,
      status: 'success',
    });
    return result;
  } catch (error) {
    console.error({
      api: context.api,
      method: context.method,
      durationMs: Date.now() - startTime,
      status: 'error',
      error: error.message,
    });
    throw error;
  }
}
```

### Field Masks

Reduce response size and improve performance:

```typescript
// Instead of fetching all fields
const response = await drive.files.list();

// Specify only needed fields
const response = await drive.files.list({
  fields: 'files(id, name, mimeType), nextPageToken',
});

// Type-safe field specification
type DriveFileFields = 'id' | 'name' | 'mimeType' | 'parents' | 'createdTime';
type FieldMask<T extends string> = T | `${T}, ${string}`;

function createFieldMask<T extends string>(fields: T[]): string {
  return fields.join(', ');
}
```

### Batch Requests

Reduce quota usage with batching:

```typescript
// Instead of N separate requests
for (const id of fileIds) {
  await drive.files.get({ fileId: id });
}

// Use batch API (when available)
const batch = google.newBatch();
fileIds.forEach((id, i) => {
  batch.add(drive.files.get({ fileId: id }), { id: `file-${i}` });
});
const results = await batch;
```

## Best Practices Summary

| Category | Practice |
|----------|----------|
| Pagination | Use async iterators, cap max pages |
| Retries | Exponential backoff with jitter |
| Quotas | Track usage, use field masks |
| Errors | Classify errors, only retry retryable |
| Logging | Log request IDs and durations |

## Related Templates

- **`templates/ts/utils/retry.ts`** - Exponential backoff implementation
- **`templates/ts/utils/pagination.ts`** - Async iterator utilities
- **`templates/ts/types.ts`** - ApiError and retry type definitions
