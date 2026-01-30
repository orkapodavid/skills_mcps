/**
 * Exponential Backoff Retry Utility
 * 
 * Type-safe retry logic with jitter for Google API calls.
 */

import {
    Result,
    ApiError,
    isRetryableError,
    getRetryDelay,
    ok,
    err,
    ApiErrors,
    ApiClientConfig,
    DEFAULT_API_CONFIG,
} from '../types.js';

export interface RetryOptions {
    readonly maxRetries: number;
    readonly initialDelayMs: number;
    readonly maxDelayMs: number;
    readonly jitterFactor: number; // 0-1, amount of randomness to add
}

export const DEFAULT_RETRY_OPTIONS: RetryOptions = {
    maxRetries: DEFAULT_API_CONFIG.maxRetries,
    initialDelayMs: DEFAULT_API_CONFIG.initialRetryDelayMs,
    maxDelayMs: DEFAULT_API_CONFIG.maxRetryDelayMs,
    jitterFactor: 0.2,
} as const;

/**
 * Calculate delay with exponential backoff and jitter.
 */
export function calculateBackoffDelay(
    attempt: number,
    options: RetryOptions
): number {
    // Exponential backoff: initialDelay * 2^attempt
    const exponentialDelay = options.initialDelayMs * Math.pow(2, attempt);
    const cappedDelay = Math.min(exponentialDelay, options.maxDelayMs);

    // Add jitter to prevent thundering herd
    const jitter = cappedDelay * options.jitterFactor * Math.random();
    return Math.floor(cappedDelay + jitter);
}

/**
 * Sleep for specified milliseconds.
 */
function sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Retry an async operation with exponential backoff.
 * 
 * Only retries on retryable errors (quota, rate limit, server, network).
 * Auth and validation errors fail immediately.
 */
export async function withRetry<T>(
    operation: () => Promise<Result<T, ApiError>>,
    options: Partial<RetryOptions> = {}
): Promise<Result<T, ApiError>> {
    const opts: RetryOptions = { ...DEFAULT_RETRY_OPTIONS, ...options };
    let lastError: ApiError | undefined;

    for (let attempt = 0; attempt <= opts.maxRetries; attempt++) {
        const result = await operation();

        if (result.success) {
            return result;
        }

        lastError = result.error;

        // Don't retry non-retryable errors
        if (!isRetryableError(result.error)) {
            return result;
        }

        // Check if we've exhausted retries
        if (attempt === opts.maxRetries) {
            break;
        }

        // Calculate delay - use server-provided delay if available
        const serverDelay = getRetryDelay(result.error);
        const delay = serverDelay ?? calculateBackoffDelay(attempt, opts);

        console.log(
            `[Retry] Attempt ${attempt + 1}/${opts.maxRetries} failed with ${result.error.kind}. ` +
            `Retrying in ${delay}ms...`
        );

        await sleep(delay);
    }

    return err(lastError ?? ApiErrors.unknown('All retries exhausted'));
}

/**
 * Wrap a throwing function to return Result.
 */
export async function toResult<T>(
    operation: () => Promise<T>
): Promise<Result<T, ApiError>> {
    try {
        const data = await operation();
        return ok(data);
    } catch (error: unknown) {
        return err(classifyError(error));
    }
}

/**
 * Classify a caught error into ApiError type.
 */
export function classifyError(error: unknown): ApiError {
    if (error instanceof Error) {
        const apiError = error as { code?: number; message?: string; response?: { status?: number } };
        const statusCode = apiError.code ?? apiError.response?.status;

        if (statusCode === 401) {
            return ApiErrors.auth(error.message, 401);
        }
        if (statusCode === 403) {
            return ApiErrors.auth(error.message, 403);
        }
        if (statusCode === 404) {
            return ApiErrors.notFound(error.message, 'unknown');
        }
        if (statusCode === 429) {
            // Default to 60s if no retry-after header
            return ApiErrors.rateLimit(error.message, 60000);
        }
        if (statusCode && statusCode >= 500) {
            return ApiErrors.server(error.message, statusCode);
        }
        if (error.message.includes('ENOTFOUND') || error.message.includes('ETIMEDOUT')) {
            return ApiErrors.network(error.message, error);
        }

        return ApiErrors.unknown(error.message, error);
    }

    return ApiErrors.unknown(String(error), error);
}
