# Common APIs — Drive, Sheets, Gmail

Type-safe wrappers and patterns for commonly used Google APIs.

## Branded Types for API Resources

Use branded types to prevent mixing IDs from different APIs:

```typescript
// Resource IDs
type FileId = Brand<string, 'FileId'>;
type FolderId = Brand<string, 'FolderId'>;
type SpreadsheetId = Brand<string, 'SpreadsheetId'>;
type SheetId = Brand<string, 'SheetId'>;
type MessageId = Brand<string, 'MessageId'>;
type ThreadId = Brand<string, 'ThreadId'>;
type LabelId = Brand<string, 'LabelId'>;

// Factory functions
const createFileId = (id: string): FileId => id as FileId;
const createSpreadsheetId = (id: string): SpreadsheetId => id as SpreadsheetId;
const createMessageId = (id: string): MessageId => id as MessageId;
```

---

## Drive API

### List Files

```typescript
interface ListFilesOptions {
  readonly pageSize?: number;
  readonly pageToken?: PageToken;
  readonly folderId?: FolderId;
  readonly mimeType?: string;
  readonly query?: string;
}

async function listFiles(
  drive: drive_v3.Drive,
  options: ListFilesOptions = {}
): Promise<Result<PaginatedResponse<DriveFile>, ApiError>> {
  return withRetry(async () => {
    try {
      const queryParts: string[] = [];
      if (options.folderId) queryParts.push(`'${options.folderId}' in parents`);
      if (options.mimeType) queryParts.push(`mimeType = '${options.mimeType}'`);
      if (options.query) queryParts.push(options.query);

      const response = await drive.files.list({
        pageSize: options.pageSize ?? 10,
        pageToken: options.pageToken,
        q: queryParts.length > 0 ? queryParts.join(' and ') : undefined,
        fields: 'files(id, name, mimeType, parents), nextPageToken',
      });

      const files: DriveFile[] = (response.data.files ?? []).map(file => ({
        id: createFileId(file.id ?? ''),
        name: file.name ?? '',
        mimeType: file.mimeType ?? '',
        parents: file.parents?.map(createFolderId),
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
```

### MIME Type Constants

```typescript
const DRIVE_MIME = {
  FOLDER: 'application/vnd.google-apps.folder',
  DOCUMENT: 'application/vnd.google-apps.document',
  SPREADSHEET: 'application/vnd.google-apps.spreadsheet',
  PRESENTATION: 'application/vnd.google-apps.presentation',
  FORM: 'application/vnd.google-apps.form',
  PDF: 'application/pdf',
} as const;
```

### Common Queries

```typescript
// Files in specific folder
`'${folderId}' in parents`

// Files by MIME type
`mimeType = '${DRIVE_MIME.SPREADSHEET}'`

// Files by name
`name = 'My Document'`
`name contains 'report'`

// Exclude trashed
`trashed = false`

// Modified recently
`modifiedTime > '2024-01-01T00:00:00'`
```

---

## Sheets API

### Type-Safe Range Notation

```typescript
type A1Range = Brand<string, 'A1Range'>;

function isValidA1Range(value: string): value is A1Range {
  // Basic A1 notation: Sheet1!A1:B10, A1:B10, Sheet1
  const pattern = /^([^!]+!)?([A-Z]+\d+(:[A-Z]+\d+)?)?$/i;
  return pattern.test(value) || /^[^!]+$/.test(value);
}

function createA1Range(range: string): Result<A1Range, ApiError> {
  if (!isValidA1Range(range)) {
    return err(ApiErrors.validation(`Invalid A1 range: ${range}`, 'range'));
  }
  return ok(range as A1Range);
}
```

### Append Values

```typescript
interface AppendValuesOptions {
  readonly spreadsheetId: SpreadsheetId;
  readonly range: A1Range;
  readonly values: unknown[][];
  readonly valueInputOption?: 'RAW' | 'USER_ENTERED';
  readonly insertDataOption?: 'OVERWRITE' | 'INSERT_ROWS';
}

async function appendValues(
  sheets: sheets_v4.Sheets,
  options: AppendValuesOptions
): Promise<Result<AppendResult, ApiError>> {
  return withRetry(async () => {
    try {
      const response = await sheets.spreadsheets.values.append({
        spreadsheetId: options.spreadsheetId,
        range: options.range,
        valueInputOption: options.valueInputOption ?? 'USER_ENTERED',
        insertDataOption: options.insertDataOption ?? 'INSERT_ROWS',
        requestBody: { values: options.values },
      });

      const updates = response.data.updates;
      return ok({
        spreadsheetId: createSpreadsheetId(updates?.spreadsheetId ?? ''),
        updatedRange: updates?.updatedRange ?? '',
        updatedCells: updates?.updatedCells ?? 0,
      });
    } catch (error) {
      return err(classifyError(error));
    }
  });
}
```

### Batch Update

```typescript
async function batchUpdateValues(
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
          data: data.map(d => ({ range: d.range, values: d.values })),
        },
      });

      return ok({ totalUpdatedCells: response.data.totalUpdatedCells ?? 0 });
    } catch (error) {
      return err(classifyError(error));
    }
  });
}
```

---

## Gmail API

### Type-Safe Email Address

```typescript
type EmailAddress = Brand<string, 'EmailAddress'>;

function isValidEmail(value: string): value is EmailAddress {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function createEmailAddress(email: string): Result<EmailAddress, ApiError> {
  if (!isValidEmail(email)) {
    return err(ApiErrors.validation(`Invalid email: ${email}`, 'email'));
  }
  return ok(email as EmailAddress);
}
```

### MIME Message Encoding

```typescript
interface EmailContent {
  readonly to: EmailAddress;
  readonly subject: string;
  readonly body: string;
  readonly cc?: EmailAddress[];
  readonly bcc?: EmailAddress[];
  readonly replyTo?: EmailAddress;
}

function createMimeMessage(content: EmailContent): string {
  const headers: string[] = [
    `To: ${content.to}`,
    `Subject: ${content.subject}`,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=utf-8',
  ];

  if (content.cc?.length) headers.push(`Cc: ${content.cc.join(', ')}`);
  if (content.bcc?.length) headers.push(`Bcc: ${content.bcc.join(', ')}`);
  if (content.replyTo) headers.push(`Reply-To: ${content.replyTo}`);

  const message = `${headers.join('\r\n')}\r\n\r\n${content.body}`;

  // Base64url encoding
  return Buffer.from(message)
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}
```

### Send Message

```typescript
async function sendMessage(
  gmail: gmail_v1.Gmail,
  content: EmailContent
): Promise<Result<SendMessageResult, ApiError>> {
  return withRetry(async () => {
    try {
      const raw = createMimeMessage(content);

      const response = await gmail.users.messages.send({
        userId: 'me',
        requestBody: { raw },
      });

      if (!response.data.id || !response.data.threadId) {
        return err(ApiErrors.unknown('Missing IDs in response'));
      }

      return ok({
        messageId: createMessageId(response.data.id),
        threadId: response.data.threadId as ThreadId,
      });
    } catch (error) {
      return err(classifyError(error));
    }
  });
}
```

---

## Scope Reference

| API | Scope | Access Level |
|-----|-------|-------------|
| Drive | `drive` | Full access |
| Drive | `drive.readonly` | Read-only |
| Drive | `drive.file` | Files created by app |
| Sheets | `spreadsheets` | Full access |
| Sheets | `spreadsheets.readonly` | Read-only |
| Gmail | `gmail.send` | Send only |
| Gmail | `gmail.readonly` | Read only |
| Gmail | `gmail.modify` | Read and modify |

## Related Templates

- **`templates/ts/drive_list_files.ts`** - Drive listing with pagination
- **`templates/ts/sheets_append_values.ts`** - Sheets operations
- **`templates/ts/gmail_send_message.ts`** - Email sending
- **`templates/ts/types.ts`** - All branded types and interfaces
