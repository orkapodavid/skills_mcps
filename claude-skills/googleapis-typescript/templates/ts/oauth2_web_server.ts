/**
 * OAuth2 Web Server Flow Example
 * 
 * Type-safe OAuth2 consent flow with token storage interface.
 * 
 * Prerequisites:
 * - npm i googleapis google-auth-library express
 * - npm i -D @types/express
 * - Set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
 */

import express, { Request, Response } from 'express';
import { google } from 'googleapis';
import { OAuth2Client, Credentials } from 'google-auth-library';
import {
  Result,
  ApiError,
  AccessToken,
  RefreshToken,
  parseOAuthConfig,
  ok,
  err,
  ApiErrors,
} from './types.js';

// ============================================================
// Token Storage Interface
// ============================================================

/**
 * Branded user ID for type safety.
 */
declare const __brand: unique symbol;
type Brand<T, B extends string> = T & { readonly [__brand]: B };
type UserId = Brand<string, 'UserId'>;

function createUserId(id: string): UserId {
  return id as UserId;
}

/**
 * Stored token structure with typed fields.
 */
export interface StoredTokens {
  readonly accessToken: AccessToken;
  readonly refreshToken: RefreshToken;
  readonly expiryDate: number;
  readonly scope: string;
}

/**
 * Token storage interface - implement with your preferred backend.
 * 
 * Examples:
 * - In-memory (development only)
 * - Redis/Memcached (session store)
 * - Database (PostgreSQL, MongoDB)
 * - Secret Manager (production)
 */
export interface TokenStorage {
  save(userId: UserId, tokens: StoredTokens): Promise<Result<void, ApiError>>;
  load(userId: UserId): Promise<Result<StoredTokens | null, ApiError>>;
  delete(userId: UserId): Promise<Result<void, ApiError>>;
}

/**
 * In-memory token storage for development.
 * DO NOT use in production - tokens are lost on restart.
 */
class InMemoryTokenStorage implements TokenStorage {
  private tokens = new Map<UserId, StoredTokens>();

  async save(userId: UserId, tokens: StoredTokens): Promise<Result<void, ApiError>> {
    this.tokens.set(userId, tokens);
    return ok(undefined);
  }

  async load(userId: UserId): Promise<Result<StoredTokens | null, ApiError>> {
    return ok(this.tokens.get(userId) ?? null);
  }

  async delete(userId: UserId): Promise<Result<void, ApiError>> {
    this.tokens.delete(userId);
    return ok(undefined);
  }
}

// ============================================================
// OAuth2 Helpers
// ============================================================

function credentialsToStoredTokens(credentials: Credentials): Result<StoredTokens, ApiError> {
  if (!credentials.access_token) {
    return err(ApiErrors.validation('Missing access token', 'access_token'));
  }
  if (!credentials.refresh_token) {
    return err(ApiErrors.validation('Missing refresh token', 'refresh_token'));
  }

  return ok({
    accessToken: credentials.access_token as AccessToken,
    refreshToken: credentials.refresh_token as RefreshToken,
    expiryDate: credentials.expiry_date ?? Date.now() + 3600 * 1000,
    scope: credentials.scope ?? '',
  });
}

function storedTokensToCredentials(tokens: StoredTokens): Credentials {
  return {
    access_token: tokens.accessToken,
    refresh_token: tokens.refreshToken,
    expiry_date: tokens.expiryDate,
    scope: tokens.scope,
  };
}

// ============================================================
// Server Setup
// ============================================================

const SCOPES = [
  'https://www.googleapis.com/auth/drive.readonly',
  'https://www.googleapis.com/auth/gmail.send',
] as const;

async function main(): Promise<void> {
  // Parse config with validation
  const configResult = parseOAuthConfig();
  if (!configResult.success) {
    console.error('Config error:', configResult.error.message);
    process.exit(1);
  }

  const { clientId, clientSecret, redirectUri } = configResult.data;
  const oAuth2Client = new OAuth2Client(clientId, clientSecret, redirectUri);
  const tokenStorage = new InMemoryTokenStorage();

  const app = express();

  // --------------------------------------------------------
  // Routes
  // --------------------------------------------------------

  /**
   * Initiate OAuth2 consent flow.
   */
  app.get('/auth', (_req: Request, res: Response) => {
    const url = oAuth2Client.generateAuthUrl({
      access_type: 'offline',
      scope: [...SCOPES],
      prompt: 'consent', // Force consent to get refresh_token
      include_granted_scopes: true,
    });
    res.redirect(url);
  });

  /**
   * Handle OAuth2 callback.
   */
  app.get('/oauth2/callback', async (req: Request, res: Response) => {
    const code = req.query.code as string | undefined;
    const error = req.query.error as string | undefined;

    if (error) {
      res.status(400).json({ error: `OAuth error: ${error}` });
      return;
    }

    if (!code) {
      res.status(400).json({ error: 'Missing authorization code' });
      return;
    }

    try {
      const { tokens } = await oAuth2Client.getToken(code);
      const storedTokensResult = credentialsToStoredTokens(tokens);

      if (!storedTokensResult.success) {
        res.status(500).json({ error: storedTokensResult.error.message });
        return;
      }

      // In production, get userId from session
      const userId = createUserId('demo-user');
      const saveResult = await tokenStorage.save(userId, storedTokensResult.data);

      if (!saveResult.success) {
        res.status(500).json({ error: saveResult.error.message });
        return;
      }

      oAuth2Client.setCredentials(tokens);
      res.json({
        message: 'OAuth2 tokens stored successfully',
        expiresIn: storedTokensResult.data.expiryDate - Date.now(),
      });
    } catch (err) {
      console.error('Token exchange error:', err);
      res.status(500).json({ error: 'Token exchange failed' });
    }
  });

  /**
   * Example protected endpoint - list Drive files.
   */
  app.get('/drive/list', async (_req: Request, res: Response) => {
    // In production, get userId from session
    const userId = createUserId('demo-user');
    const tokensResult = await tokenStorage.load(userId);

    if (!tokensResult.success) {
      res.status(500).json({ error: tokensResult.error.message });
      return;
    }

    if (!tokensResult.data) {
      res.status(401).json({ error: 'Not authenticated', authUrl: '/auth' });
      return;
    }

    oAuth2Client.setCredentials(storedTokensToCredentials(tokensResult.data));

    try {
      const drive = google.drive({ version: 'v3', auth: oAuth2Client });
      const response = await drive.files.list({
        pageSize: 10,
        fields: 'files(id, name, mimeType)',
      });

      res.json({
        files: response.data.files ?? [],
        count: response.data.files?.length ?? 0,
      });
    } catch (err) {
      console.error('Drive API error:', err);
      res.status(500).json({ error: 'Failed to list files' });
    }
  });

  /**
   * Logout - delete stored tokens.
   */
  app.post('/logout', async (_req: Request, res: Response) => {
    const userId = createUserId('demo-user');
    const deleteResult = await tokenStorage.delete(userId);

    if (!deleteResult.success) {
      res.status(500).json({ error: deleteResult.error.message });
      return;
    }

    res.json({ message: 'Logged out successfully' });
  });

  /**
   * Health check endpoint.
   */
  app.get('/healthz', (_req: Request, res: Response) => {
    res.send('ok');
  });

  // --------------------------------------------------------
  // Start Server
  // --------------------------------------------------------

  const port = process.env.PORT ?? 3000;
  app.listen(port, () => {
    console.log(`OAuth2 web server running at http://localhost:${port}`);
    console.log(`Visit http://localhost:${port}/auth to start OAuth flow`);
  });
}

main();
