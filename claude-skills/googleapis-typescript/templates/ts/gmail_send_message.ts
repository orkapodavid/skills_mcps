/**
 * Gmail: Send Message Example
 * 
 * Type-safe Gmail message sending with Result pattern.
 * 
 * Prerequisites:
 * - npm i googleapis google-auth-library
 * - Set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
 * - User must have granted gmail.send scope
 */

import { google, gmail_v1 } from 'googleapis';
import { OAuth2Client } from 'google-auth-library';
import {
  Result,
  ApiError,
  GmailMessage,
  MessageId,
  ThreadId,
  parseOAuthConfig,
  ok,
  err,
  ApiErrors,
  createMessageId,
} from './types.js';
import { withRetry, classifyError } from './utils/retry.js';

// ============================================================
// Branded Types for Email
// ============================================================

declare const __brand: unique symbol;
type Brand<T, B extends string> = T & { readonly [__brand]: B };

type EmailAddress = Brand<string, 'EmailAddress'>;

function isValidEmail(value: string): value is EmailAddress {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function createEmailAddress(email: string): Result<EmailAddress, ApiError> {
  if (!isValidEmail(email)) {
    return err(ApiErrors.validation(`Invalid email format: ${email}`, 'email'));
  }
  return ok(email as EmailAddress);
}

// ============================================================
// Client Setup
// ============================================================

function createGmailClient(auth: OAuth2Client): gmail_v1.Gmail {
  return google.gmail({ version: 'v1', auth });
}

// ============================================================
// MIME Encoding
// ============================================================

export interface EmailContent {
  readonly to: EmailAddress;
  readonly subject: string;
  readonly body: string;
  readonly cc?: EmailAddress[];
  readonly bcc?: EmailAddress[];
  readonly replyTo?: EmailAddress;
}

/**
 * Create RFC 2822 MIME message and encode as base64url.
 */
function createMimeMessage(content: EmailContent): string {
  const headers: string[] = [
    `To: ${content.to}`,
    `Subject: ${content.subject}`,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=utf-8',
  ];

  if (content.cc && content.cc.length > 0) {
    headers.push(`Cc: ${content.cc.join(', ')}`);
  }
  if (content.bcc && content.bcc.length > 0) {
    headers.push(`Bcc: ${content.bcc.join(', ')}`);
  }
  if (content.replyTo) {
    headers.push(`Reply-To: ${content.replyTo}`);
  }

  const message = `${headers.join('\r\n')}\r\n\r\n${content.body}`;

  // Encode as base64url (URL-safe base64)
  return Buffer.from(message)
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

// ============================================================
// Type-Safe API Methods
// ============================================================

export interface SendMessageResult {
  readonly messageId: MessageId;
  readonly threadId: ThreadId;
}

/**
 * Send email with type-safe Result pattern.
 */
export async function sendMessage(
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

      const messageId = response.data.id;
      const threadId = response.data.threadId;

      if (!messageId || !threadId) {
        return err(ApiErrors.unknown('Missing message or thread ID in response'));
      }

      return ok({
        messageId: createMessageId(messageId),
        threadId: threadId as ThreadId,
      });
    } catch (error) {
      return err(classifyError(error));
    }
  });
}

/**
 * Create a draft instead of sending immediately.
 */
export async function createDraft(
  gmail: gmail_v1.Gmail,
  content: EmailContent
): Promise<Result<{ draftId: string; messageId: MessageId }, ApiError>> {
  return withRetry(async () => {
    try {
      const raw = createMimeMessage(content);

      const response = await gmail.users.drafts.create({
        userId: 'me',
        requestBody: {
          message: { raw },
        },
      });

      const draftId = response.data.id;
      const messageId = response.data.message?.id;

      if (!draftId || !messageId) {
        return err(ApiErrors.unknown('Missing draft or message ID in response'));
      }

      return ok({
        draftId,
        messageId: createMessageId(messageId),
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

  const gmail = createGmailClient(oAuth2Client);

  // Validate email addresses
  const toResult = createEmailAddress('recipient@example.com');
  if (!toResult.success) {
    console.error('Invalid recipient email:', toResult.error.message);
    process.exit(1);
  }

  // Send message with Result handling
  const result = await sendMessage(gmail, {
    to: toResult.data,
    subject: 'Hello from googleapis-typescript',
    body: 'This message was sent using type-safe Gmail API wrappers.',
  });

  if (!result.success) {
    console.error('Failed to send:', result.error.kind, result.error.message);
    process.exit(1);
  }

  console.log('Message sent successfully!');
  console.log('Message ID:', result.data.messageId);
  console.log('Thread ID:', result.data.threadId);
}

main();
