/**
 * Shared Types for Google APIs TypeScript Skill
 * 
 * Provides branded types, Result patterns, and type guards for
 * type-safe Google API integrations.
 */

// ============================================================
// Branded Types
// ============================================================

declare const __brand: unique symbol;

/**
 * Helper type to create a branded type.
 * T: The base type (e.g., string)
 * B: The unique brand string
 */
export type Brand<T, B extends string> = T & { readonly [__brand]: B };

// Google API Resource IDs
export type FileId = Brand<string, 'FileId'>;
export type FolderId = Brand<string, 'FolderId'>;
export type SheetId = Brand<string, 'SheetId'>;
export type SpreadsheetId = Brand<string, 'SpreadsheetId'>;
export type MessageId = Brand<string, 'MessageId'>;
export type ThreadId = Brand<string, 'ThreadId'>;
export type LabelId = Brand<string, 'LabelId'>;

// OAuth Tokens
export type AccessToken = Brand<string, 'AccessToken'>;
export type RefreshToken = Brand<string, 'RefreshToken'>;

// API Identifiers
export type RequestId = Brand<string, 'RequestId'>;
export type PageToken = Brand<string, 'PageToken'>;

// ============================================================
// Factory Functions
// ============================================================

export function createFileId(id: string): FileId {
    return id as FileId;
}

export function createFolderId(id: string): FolderId {
    return id as FolderId;
}

export function createSpreadsheetId(id: string): SpreadsheetId {
    return id as SpreadsheetId;
}

export function createMessageId(id: string): MessageId {
    return id as MessageId;
}

export function createPageToken(token: string): PageToken {
    return token as PageToken;
}

// ============================================================
// Result Pattern
// ============================================================

/**
 * Discriminated union for type-safe error handling.
 * Prefer this over throwing exceptions for expected failures.
 */
export type Result<T, E = ApiError> =
    | { readonly success: true; readonly data: T }
    | { readonly success: false; readonly error: E };

export function ok<T>(data: T): Result<T, never> {
    return { success: true, data };
}

export function err<E>(error: E): Result<never, E> {
    return { success: false, error };
}

/**
 * Unwrap a Result, throwing if it's an error.
 * Use only when failure is truly unexpected.
 */
export function unwrap<T, E>(result: Result<T, E>): T {
    if (result.success) {
        return result.data;
    }
    throw result.error;
}

/**
 * Map over a successful Result.
 */
export function mapResult<T, U, E>(
    result: Result<T, E>,
    fn: (data: T) => U
): Result<U, E> {
    if (result.success) {
        return ok(fn(result.data));
    }
    return result;
}

// ============================================================
// API Error Types
// ============================================================

/**
 * Discriminated union for Google API errors.
 * Enables exhaustive handling of error types.
 */
export type ApiError =
    | { readonly kind: 'auth'; readonly message: string; readonly code: 401 | 403 }
    | { readonly kind: 'not_found'; readonly message: string; readonly resourceId: string }
    | { readonly kind: 'quota'; readonly message: string; readonly retryAfterMs: number }
    | { readonly kind: 'rate_limit'; readonly message: string; readonly retryAfterMs: number }
    | { readonly kind: 'server'; readonly message: string; readonly code: number; readonly requestId?: RequestId }
    | { readonly kind: 'network'; readonly message: string; readonly cause?: Error }
    | { readonly kind: 'validation'; readonly message: string; readonly field?: string }
    | { readonly kind: 'unknown'; readonly message: string; readonly cause?: unknown };

// Error constructors
export const ApiErrors = {
    auth: (message: string, code: 401 | 403 = 401): ApiError => ({
        kind: 'auth',
        message,
        code,
    }),

    notFound: (message: string, resourceId: string): ApiError => ({
        kind: 'not_found',
        message,
        resourceId,
    }),

    quota: (message: string, retryAfterMs: number): ApiError => ({
        kind: 'quota',
        message,
        retryAfterMs,
    }),

    rateLimit: (message: string, retryAfterMs: number): ApiError => ({
        kind: 'rate_limit',
        message,
        retryAfterMs,
    }),

    server: (message: string, code: number, requestId?: RequestId): ApiError => ({
        kind: 'server',
        message,
        code,
        requestId,
    }),

    network: (message: string, cause?: Error): ApiError => ({
        kind: 'network',
        message,
        cause,
    }),

    validation: (message: string, field?: string): ApiError => ({
        kind: 'validation',
        message,
        field,
    }),

    unknown: (message: string, cause?: unknown): ApiError => ({
        kind: 'unknown',
        message,
        cause,
    }),
} as const;

// ============================================================
// Type Guards
// ============================================================

export function isRetryableError(error: ApiError): boolean {
    return (
        error.kind === 'quota' ||
        error.kind === 'rate_limit' ||
        error.kind === 'server' ||
        error.kind === 'network'
    );
}

export function isAuthError(error: ApiError): error is Extract<ApiError, { kind: 'auth' }> {
    return error.kind === 'auth';
}

export function isQuotaError(error: ApiError): error is Extract<ApiError, { kind: 'quota' }> {
    return error.kind === 'quota';
}

export function getRetryDelay(error: ApiError): number | null {
    if (error.kind === 'quota' || error.kind === 'rate_limit') {
        return error.retryAfterMs;
    }
    return null;
}

// ============================================================
// Configuration
// ============================================================

export interface OAuthConfig {
    readonly clientId: string;
    readonly clientSecret: string;
    readonly redirectUri: string;
}

export interface ServiceAccountConfig {
    readonly keyFilePath: string;
    readonly scopes: readonly string[];
    readonly subject?: string; // For domain-wide delegation
}

export interface ApiClientConfig {
    readonly maxRetries: number;
    readonly initialRetryDelayMs: number;
    readonly maxRetryDelayMs: number;
    readonly timeoutMs: number;
}

export const DEFAULT_API_CONFIG: ApiClientConfig = {
    maxRetries: 3,
    initialRetryDelayMs: 1000,
    maxRetryDelayMs: 30000,
    timeoutMs: 30000,
} as const;

/**
 * Parse OAuth config from environment variables.
 * Returns Result to handle missing config gracefully.
 */
export function parseOAuthConfig(): Result<OAuthConfig, ApiError> {
    const clientId = process.env.GOOGLE_CLIENT_ID;
    const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
    const redirectUri = process.env.GOOGLE_REDIRECT_URI;

    if (!clientId) {
        return err(ApiErrors.validation('Missing GOOGLE_CLIENT_ID', 'clientId'));
    }
    if (!clientSecret) {
        return err(ApiErrors.validation('Missing GOOGLE_CLIENT_SECRET', 'clientSecret'));
    }
    if (!redirectUri) {
        return err(ApiErrors.validation('Missing GOOGLE_REDIRECT_URI', 'redirectUri'));
    }

    return ok({ clientId, clientSecret, redirectUri });
}

/**
 * Parse service account config from environment.
 */
export function parseServiceAccountConfig(
    scopes: readonly string[]
): Result<ServiceAccountConfig, ApiError> {
    const keyFilePath = process.env.GOOGLE_APPLICATION_CREDENTIALS;

    if (!keyFilePath) {
        return err(ApiErrors.validation('Missing GOOGLE_APPLICATION_CREDENTIALS', 'keyFilePath'));
    }

    return ok({
        keyFilePath,
        scopes,
        subject: process.env.GOOGLE_IMPERSONATE_SUBJECT,
    });
}

// ============================================================
// Pagination Types
// ============================================================

export interface PaginatedResponse<T> {
    readonly items: T[];
    readonly nextPageToken?: PageToken;
}

export interface PaginationOptions {
    readonly pageSize?: number;
    readonly maxPages?: number;
    readonly pageToken?: PageToken;
}

// ============================================================
// Google API Response Types
// ============================================================

export interface DriveFile {
    readonly id: FileId;
    readonly name: string;
    readonly mimeType: string;
    readonly parents?: FolderId[];
    readonly createdTime?: string;
    readonly modifiedTime?: string;
}

export interface SheetRange {
    readonly spreadsheetId: SpreadsheetId;
    readonly range: string;
    readonly values: unknown[][];
}

export interface GmailMessage {
    readonly id: MessageId;
    readonly threadId: ThreadId;
    readonly labelIds?: LabelId[];
    readonly snippet?: string;
    readonly payload?: {
        readonly headers?: Array<{ name: string; value: string }>;
    };
}
