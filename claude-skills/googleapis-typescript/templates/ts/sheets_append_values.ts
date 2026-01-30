/**
 * Sheets: Append Values Example
 * 
 * Type-safe Google Sheets value appending with Result pattern.
 * 
 * Prerequisites:
 * - npm i googleapis google-auth-library
 * - Set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
 * - User must have granted spreadsheets scope
 */

import { google, sheets_v4 } from 'googleapis';
import { OAuth2Client } from 'google-auth-library';
import {
  Result,
  ApiError,
  SpreadsheetId,
  SheetRange,
  parseOAuthConfig,
  ok,
  err,
  ApiErrors,
  createSpreadsheetId,
} from './types.js';
import { withRetry, classifyError } from './utils/retry.js';

// ============================================================
// Branded Types for Sheets
// ============================================================

declare const __brand: unique symbol;
type Brand<T, B extends string> = T & { readonly [__brand]: B };

type A1Range = Brand<string, 'A1Range'>;

/**
 * Validate A1 notation range.
 * Examples: "Sheet1!A1:B10", "A1:B10", "Sheet1"
 */
function isValidA1Range(value: string): value is A1Range {
  // Basic A1 notation validation
  const a1Pattern = /^([^!]+!)?([A-Z]+\d+(:[A-Z]+\d+)?)?$/i;
  return a1Pattern.test(value) || /^[^!]+$/.test(value);
}

function createA1Range(range: string): Result<A1Range, ApiError> {
  if (!isValidA1Range(range)) {
    return err(ApiErrors.validation(`Invalid A1 range notation: ${range}`, 'range'));
  }
  return ok(range as A1Range);
}

// ============================================================
// Client Setup
// ============================================================

function createSheetsClient(auth: OAuth2Client): sheets_v4.Sheets {
  return google.sheets({ version: 'v4', auth });
}

// ============================================================
// Type-Safe API Methods
// ============================================================

export interface AppendValuesOptions {
  readonly spreadsheetId: SpreadsheetId;
  readonly range: A1Range;
  readonly values: unknown[][];
  readonly valueInputOption?: 'RAW' | 'USER_ENTERED';
  readonly insertDataOption?: 'OVERWRITE' | 'INSERT_ROWS';
}

export interface AppendResult {
  readonly spreadsheetId: SpreadsheetId;
  readonly updatedRange: string;
  readonly updatedRows: number;
  readonly updatedColumns: number;
  readonly updatedCells: number;
}

/**
 * Append values to a spreadsheet with type-safe Result pattern.
 */
export async function appendValues(
  sheets: sheets_v4.Sheets,
  options: AppendValuesOptions
): Promise<Result<AppendResult, ApiError>> {
  const {
    spreadsheetId,
    range,
    values,
    valueInputOption = 'USER_ENTERED',
    insertDataOption = 'INSERT_ROWS',
  } = options;

  return withRetry(async () => {
    try {
      const response = await sheets.spreadsheets.values.append({
        spreadsheetId,
        range,
        valueInputOption,
        insertDataOption,
        requestBody: { values },
      });

      const updates = response.data.updates;
      if (!updates) {
        return err(ApiErrors.unknown('Missing updates in response'));
      }

      return ok({
        spreadsheetId: createSpreadsheetId(updates.spreadsheetId ?? spreadsheetId),
        updatedRange: updates.updatedRange ?? '',
        updatedRows: updates.updatedRows ?? 0,
        updatedColumns: updates.updatedColumns ?? 0,
        updatedCells: updates.updatedCells ?? 0,
      });
    } catch (error) {
      return err(classifyError(error));
    }
  });
}

/**
 * Read values from a range.
 */
export async function getValues(
  sheets: sheets_v4.Sheets,
  spreadsheetId: SpreadsheetId,
  range: A1Range
): Promise<Result<SheetRange, ApiError>> {
  return withRetry(async () => {
    try {
      const response = await sheets.spreadsheets.values.get({
        spreadsheetId,
        range,
      });

      return ok({
        spreadsheetId,
        range: response.data.range ?? range,
        values: (response.data.values ?? []) as unknown[][],
      });
    } catch (error) {
      return err(classifyError(error));
    }
  });
}

/**
 * Batch update multiple ranges.
 */
export async function batchUpdateValues(
  sheets: sheets_v4.Sheets,
  spreadsheetId: SpreadsheetId,
  data: Array<{ range: A1Range; values: unknown[][] }>
): Promise<Result<{ totalUpdatedCells: number }, ApiError>> {
  return withRetry(async () => {
    try {
      const response = await sheets.spreadsheets.values.batchUpdate({
        spreadsheetId,
        requestBody: {
          valueInputOption: 'USER_ENTERED',
          data: data.map((d) => ({
            range: d.range,
            values: d.values,
          })),
        },
      });

      return ok({
        totalUpdatedCells: response.data.totalUpdatedCells ?? 0,
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

  const sheets = createSheetsClient(oAuth2Client);

  // Validate inputs
  const spreadsheetId = createSpreadsheetId('your-spreadsheet-id');
  const rangeResult = createA1Range('Sheet1!A1:C1');
  if (!rangeResult.success) {
    console.error('Invalid range:', rangeResult.error.message);
    process.exit(1);
  }

  // Append values with Result handling
  const result = await appendValues(sheets, {
    spreadsheetId,
    range: rangeResult.data,
    values: [
      ['Name', 'Email', 'Status'],
      ['Alice', 'alice@example.com', 'Active'],
      ['Bob', 'bob@example.com', 'Pending'],
    ],
  });

  if (!result.success) {
    console.error('Failed to append:', result.error.kind, result.error.message);
    process.exit(1);
  }

  console.log('Values appended successfully!');
  console.log('Updated range:', result.data.updatedRange);
  console.log('Updated cells:', result.data.updatedCells);
}

main();
