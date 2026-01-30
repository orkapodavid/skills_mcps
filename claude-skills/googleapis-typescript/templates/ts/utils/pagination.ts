/**
 * Pagination Utilities for Google APIs
 * 
 * Type-safe async iterators for paginated responses.
 */

import {
    Result,
    ApiError,
    PaginatedResponse,
    PaginationOptions,
    PageToken,
    createPageToken,
    ok,
    err,
    ApiErrors,
} from '../types.js';

export interface PageFetcher<T> {
    (pageToken?: PageToken): Promise<Result<PaginatedResponse<T>, ApiError>>;
}

/**
 * Create an async iterator for paginated API responses.
 * 
 * Yields items one at a time, fetching pages as needed.
 * Respects maxPages limit to avoid quota exhaustion.
 */
export async function* paginate<T>(
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

        if (!pageToken) {
            break;
        }
    }

    if (pageCount >= maxPages) {
        console.warn(`[Pagination] Stopped after ${maxPages} pages to preserve quota`);
    }
}

/**
 * Collect all items from paginated response into array.
 * 
 * Use with caution on large datasets - prefer streaming with paginate().
 */
export async function collectAll<T>(
    fetcher: PageFetcher<T>,
    options: PaginationOptions = {}
): Promise<Result<T[], ApiError>> {
    const items: T[] = [];

    for await (const result of paginate(fetcher, options)) {
        if (!result.success) {
            return err(result.error);
        }
        items.push(result.data);
    }

    return ok(items);
}

/**
 * Collect items up to a limit.
 */
export async function collectUpTo<T>(
    fetcher: PageFetcher<T>,
    limit: number,
    options: PaginationOptions = {}
): Promise<Result<T[], ApiError>> {
    const items: T[] = [];

    for await (const result of paginate(fetcher, options)) {
        if (!result.success) {
            return err(result.error);
        }
        items.push(result.data);
        if (items.length >= limit) {
            break;
        }
    }

    return ok(items.slice(0, limit));
}

/**
 * Find first item matching predicate.
 */
export async function findFirst<T>(
    fetcher: PageFetcher<T>,
    predicate: (item: T) => boolean,
    options: PaginationOptions = {}
): Promise<Result<T | undefined, ApiError>> {
    for await (const result of paginate(fetcher, options)) {
        if (!result.success) {
            return err(result.error);
        }
        if (predicate(result.data)) {
            return ok(result.data);
        }
    }

    return ok(undefined);
}

/**
 * Create a PageFetcher from a Google API list method.
 * 
 * Transforms googleapis response format to PaginatedResponse.
 */
export function createPageFetcher<TResponse, TItem>(
    listFn: (params: { pageToken?: string }) => Promise<{ data: TResponse }>,
    extractItems: (response: TResponse) => TItem[] | undefined,
    extractNextToken: (response: TResponse) => string | undefined
): PageFetcher<TItem> {
    return async (pageToken?: PageToken) => {
        try {
            const response = await listFn({ pageToken });
            const items = extractItems(response.data) ?? [];
            const nextToken = extractNextToken(response.data);

            return ok({
                items,
                nextPageToken: nextToken ? createPageToken(nextToken) : undefined,
            });
        } catch (error: unknown) {
            if (error instanceof Error) {
                return err(ApiErrors.unknown(error.message, error));
            }
            return err(ApiErrors.unknown(String(error), error));
        }
    };
}
