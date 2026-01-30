---
name: googleapis-typescript
description: This skill should be used when the user needs to "integrate with Google APIs in TypeScript", "authenticate with OAuth2 or service accounts", "call Drive, Sheets, or Gmail APIs", "handle pagination and retries", or is "deploying to Cloud Run with Google API access". Provides type-safe patterns for googleapis Node.js client.
version: 0.1.0
---

# Google APIs with TypeScript

This skill provides type-safe patterns for integrating Google APIs in TypeScript backends using the official `googleapis` Node.js client.

## When to Use

- Building TypeScript backends that call Google APIs (Drive, Sheets, Gmail, etc.)
- Implementing OAuth2 consent flows or service account authentication
- Requiring production-grade patterns (pagination, retries, error handling)
- Deploying to Cloud Run or GKE with Google API access

## Core Workflow

1. **Choose authentication method**:
   - OAuth2 web server flow (user consent, access user data)
   - Service account JWT (server-to-server, automation)
2. **Initialize googleapis client** with appropriate scopes
3. **Implement API calls** using typed responses and Result pattern
4. **Add production patterns**: pagination, exponential backoff, quota management
5. **Configure secrets** for deployment (environment variables, Secret Manager)

## Quick Start

Install dependencies:
```bash
npm i googleapis google-auth-library
npm i -D typescript ts-node @types/node
```

Create or update `tsconfig.json` for ES2020+ and `moduleResolution: "node"`.

Place credentials:
- **OAuth2**: Set `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`
- **Service Account**: Set `GOOGLE_APPLICATION_CREDENTIALS` path to JSON key

## Reference Guide

Load detailed guidance based on context:

| Topic | Reference | Load When |
|-------|-----------|-----------|
| OAuth2 Flow | `references/auth-oauth2.md` | User consent, token storage, web apps |
| Service Account | `references/auth-service-account.md` | Server-to-server, automation, Cloud Run |
| Error Handling | `references/error-handling.md` | Result pattern, error classification |
| Pagination & Retries | `references/pagination-retries.md` | Async iterators, exponential backoff |
| Common APIs | `references/common-apis.md` | Drive, Sheets, Gmail type-safe wrappers |
| Quickstart | `references/quickstart.md` | Installation, scopes, running examples |
| Cloud Run | `references/cloud-run-notes.md` | Deployment, Workload Identity |
| TypeScript Config | `references/typescript-config.md` | tsconfig options |

## Template Files

Working examples in `templates/ts/`:

| Template | Description |
|----------|-------------|
| `types.ts` | Branded types, Result pattern, ApiError union |
| `utils/retry.ts` | Exponential backoff with jitter |
| `utils/pagination.ts` | Async iterator for paginated responses |
| `drive_list_files.ts` | Drive file listing with pagination |
| `sheets_append_values.ts` | Sheets append with batch update |
| `gmail_send_message.ts` | Email sending with MIME encoding |
| `oauth2_web_server.ts` | Express OAuth2 consent flow |
| `service_account_jwt.ts` | Environment-aware service account auth |

## Constraints

### Must Do

- Use branded types for resource IDs (`FileId`, `SheetId`, `MessageId`)
- Return `Result<T, ApiError>` instead of throwing for expected failures
- Implement exponential backoff with jitter for retries
- Use type guards to classify and handle errors exhaustively
- Validate environment configuration at startup with Result pattern
- Use field masks to minimize response payload
- Log request IDs and durations for debugging
- Respect API quotas; cap pagination to prevent exhaustion

### Must Not Do

- Commit credentials or API keys to source control
- Use `any` type for API responses without justification
- Retry non-retryable errors (auth, validation, not found)
- Ignore `429` rate limit responses
- Mix user IDs with resource IDs (use branded types)
- Skip error classification; handle all ApiError kinds
- Call APIs without retry logic in production
- Use synchronous token storage in production

## Output Templates

When implementing Google API integrations:

1. **Type definitions**: Define branded types and interfaces first
2. **Configuration**: Parse and validate environment with Result
3. **API wrappers**: Create functions returning `Result<T, ApiError>`
4. **Error handling**: Use switch on `error.kind` for exhaustive handling
5. **Rationale**: Explain retry strategy and quota considerations

## Knowledge Reference

googleapis, google-auth-library, OAuth2Client, JWT, GoogleAuth, Workload Identity Federation, branded types, discriminated unions, Result pattern, exponential backoff, jitter, pagination, pageToken, field masks, Cloud Run, Secret Manager, domain-wide delegation.

## Related Skills

- **typescript-pro** - Advanced type patterns (generics, utility types)
- **cloud-deployment** - Cloud Run and GKE deployment patterns
