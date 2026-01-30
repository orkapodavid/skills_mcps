/**
 * Drive: List Files Example
 * 
 * Type-safe Google Drive file listing with Result pattern and pagination.
 * 
 * Prerequisites:
 * - npm i googleapis google-auth-library
 * - Set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
 * - Or set GOOGLE_APPLICATION_CREDENTIALS for service account
 */

import { google, drive_v3 } from 'googleapis';
import { OAuth2Client } from 'google-auth-library';
import {
  Result,
  ApiError,
  DriveFile,
  FileId,
  FolderId,
  PageToken,
  PaginatedResponse,
  parseOAuthConfig,
  ok,
  err,
  ApiErrors,
  createFileId,
  createFolderId,
  createPageToken,
} from './types.js';
import { withRetry, toResult, classifyError } from './utils/retry.js';
import { createPageFetcher, collectUpTo } from './utils/pagination.js';

// ============================================================
// Client Setup
// ============================================================

function createDriveClient(auth: OAuth2Client): drive_v3.Drive {
  return google.drive({ version: 'v3', auth });
}

// ============================================================
// Type-Safe API Methods
// ============================================================

export interface ListFilesOptions {
  readonly pageSize?: number;
  readonly pageToken?: PageToken;
  readonly folderId?: FolderId;
  readonly mimeType?: string;
  readonly query?: string;
}

/**
 * List files with type-safe Result pattern.
 */
export async function listFiles(
  drive: drive_v3.Drive,
  options: ListFilesOptions = {}
): Promise<Result<PaginatedResponse<DriveFile>, ApiError>> {
  const { pageSize = 10, pageToken, folderId, mimeType, query } = options;

  // Build query string
  const queryParts: string[] = [];
  if (folderId) {
    queryParts.push(`'${folderId}' in parents`);
  }
  if (mimeType) {
    queryParts.push(`mimeType = '${mimeType}'`);
  }
  if (query) {
    queryParts.push(query);
  }

  return withRetry(async () => {
    try {
      const response = await drive.files.list({
        pageSize,
        pageToken,
        q: queryParts.length > 0 ? queryParts.join(' and ') : undefined,
        fields: 'files(id, name, mimeType, parents, createdTime, modifiedTime), nextPageToken',
      });

      const files: DriveFile[] = (response.data.files ?? []).map((file) => ({
        id: createFileId(file.id ?? ''),
        name: file.name ?? '',
        mimeType: file.mimeType ?? '',
        parents: file.parents?.map(createFolderId),
        createdTime: file.createdTime ?? undefined,
        modifiedTime: file.modifiedTime ?? undefined,
      }));

      return ok({
        items: files,
        nextPageToken: response.data.nextPageToken
          ? createPageToken(response.data.nextPageToken)
          : undefined,
      });
    } catch (error) {
      return err(classifyError(error));
    }
  });
}

/**
 * Get file by ID.
 */
export async function getFile(
  drive: drive_v3.Drive,
  fileId: FileId
): Promise<Result<DriveFile, ApiError>> {
  return withRetry(async () => {
    try {
      const response = await drive.files.get({
        fileId,
        fields: 'id, name, mimeType, parents, createdTime, modifiedTime',
      });

      const file = response.data;
      return ok({
        id: createFileId(file.id ?? ''),
        name: file.name ?? '',
        mimeType: file.mimeType ?? '',
        parents: file.parents?.map(createFolderId),
        createdTime: file.createdTime ?? undefined,
        modifiedTime: file.modifiedTime ?? undefined,
      });
    } catch (error) {
      return err(classifyError(error));
    }
  });
}

// ============================================================
// Example Usage
// ============================================================

async function main(): Promise<void> {
  // Parse config with validation
  const configResult = parseOAuthConfig();
  if (!configResult.success) {
    console.error('Config error:', configResult.error.message);
    process.exit(1);
  }

  const { clientId, clientSecret, redirectUri } = configResult.data;

  const oAuth2Client = new OAuth2Client(clientId, clientSecret, redirectUri);

  // TODO: Load tokens from your storage
  // oAuth2Client.setCredentials({ access_token, refresh_token, expiry_date })

  const drive = createDriveClient(oAuth2Client);

  // List first 20 files with type-safe Result handling
  const result = await listFiles(drive, { pageSize: 10 });

  if (!result.success) {
    // Exhaustive error handling
    switch (result.error.kind) {
      case 'auth':
        console.error('Authentication failed:', result.error.message);
        break;
      case 'quota':
        console.error('Quota exceeded. Retry after:', result.error.retryAfterMs, 'ms');
        break;
      case 'rate_limit':
        console.error('Rate limited. Retry after:', result.error.retryAfterMs, 'ms');
        break;
      case 'not_found':
        console.error('Resource not found:', result.error.resourceId);
        break;
      case 'server':
        console.error('Server error:', result.error.code);
        break;
      case 'network':
        console.error('Network error:', result.error.message);
        break;
      case 'validation':
        console.error('Validation error:', result.error.field);
        break;
      case 'unknown':
        console.error('Unknown error:', result.error.message);
        break;
    }
    process.exit(1);
  }

  console.log('Files found:', result.data.items.length);
  for (const file of result.data.items) {
    console.log(`- ${file.name} (${file.id}): ${file.mimeType}`);
  }

  if (result.data.nextPageToken) {
    console.log('More pages available');
  }
}

main();
