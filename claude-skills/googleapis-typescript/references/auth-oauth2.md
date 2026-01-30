# OAuth2 Web Server Flow

Type-safe OAuth2 consent flow for accessing user data with their permission.

## When to Use

- Accessing user-owned resources (files, emails, calendar)
- Building web applications with Google Sign-In
- Requiring offline access (refresh tokens)

## Setup

### 1. Create OAuth 2.0 Client ID

1. Go to [Google Cloud Console > APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials)
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Web application"
4. Add authorized redirect URIs (e.g., `http://localhost:3000/oauth2/callback`)

### 2. Configure Environment Variables

```bash
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-client-secret"
export GOOGLE_REDIRECT_URI="http://localhost:3000/oauth2/callback"
```

## Type-Safe Configuration

Parse and validate OAuth config at startup:

```typescript
interface OAuthConfig {
  readonly clientId: string;
  readonly clientSecret: string;
  readonly redirectUri: string;
}

function parseOAuthConfig(): Result<OAuthConfig, ApiError> {
  const clientId = process.env.GOOGLE_CLIENT_ID;
  const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
  const redirectUri = process.env.GOOGLE_REDIRECT_URI;

  if (!clientId) return err(ApiErrors.validation('Missing GOOGLE_CLIENT_ID', 'clientId'));
  if (!clientSecret) return err(ApiErrors.validation('Missing GOOGLE_CLIENT_SECRET', 'clientSecret'));
  if (!redirectUri) return err(ApiErrors.validation('Missing GOOGLE_REDIRECT_URI', 'redirectUri'));

  return ok({ clientId, clientSecret, redirectUri });
}
```

## Token Storage Interface

Define a storage interface for production flexibility:

```typescript
// Branded types for tokens
type AccessToken = Brand<string, 'AccessToken'>;
type RefreshToken = Brand<string, 'RefreshToken'>;

interface StoredTokens {
  readonly accessToken: AccessToken;
  readonly refreshToken: RefreshToken;
  readonly expiryDate: number;
  readonly scope: string;
}

interface TokenStorage {
  save(userId: UserId, tokens: StoredTokens): Promise<Result<void, ApiError>>;
  load(userId: UserId): Promise<Result<StoredTokens | null, ApiError>>;
  delete(userId: UserId): Promise<Result<void, ApiError>>;
}
```

### Implementation Options

| Storage | Use Case | Considerations |
|---------|----------|----------------|
| In-memory | Development | Lost on restart, single instance only |
| Redis | Session store | Fast, good for short-lived sessions |
| PostgreSQL | Multi-region | Persistent, queryable, ACID |
| Secret Manager | Production secrets | Audit trail, rotation support |
| Encrypted cookie | Stateless | Limited size, client-side storage |

## Consent Flow

### 1. Generate Auth URL

```typescript
const SCOPES = [
  'https://www.googleapis.com/auth/drive.readonly',
  'https://www.googleapis.com/auth/gmail.send',
] as const;

app.get('/auth', (_req, res) => {
  const url = oAuth2Client.generateAuthUrl({
    access_type: 'offline',     // Get refresh token
    scope: [...SCOPES],
    prompt: 'consent',          // Force consent for refresh token
    include_granted_scopes: true,
  });
  res.redirect(url);
});
```

### 2. Handle Callback

```typescript
app.get('/oauth2/callback', async (req, res) => {
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

    // Get user ID from session (implement your own session management)
    const userId = getUserIdFromSession(req);
    await tokenStorage.save(userId, storedTokensResult.data);
    
    res.json({ message: 'Authentication successful' });
  } catch (err) {
    res.status(500).json({ error: 'Token exchange failed' });
  }
});
```

## Token Refresh

The `google-auth-library` handles refresh automatically when credentials are set:

```typescript
// Tokens are refreshed automatically when expired
oAuth2Client.setCredentials({
  access_token: storedTokens.accessToken,
  refresh_token: storedTokens.refreshToken,
  expiry_date: storedTokens.expiryDate,
});

// Listen for token updates to persist new access tokens
oAuth2Client.on('tokens', async (newTokens) => {
  const updated = {
    ...storedTokens,
    accessToken: newTokens.access_token as AccessToken,
    expiryDate: newTokens.expiry_date ?? Date.now() + 3600 * 1000,
  };
  await tokenStorage.save(userId, updated);
});
```

## Incremental Authorization

Request additional scopes as needed:

```typescript
function generateIncrementalAuthUrl(
  oAuth2Client: OAuth2Client,
  additionalScopes: string[]
): string {
  return oAuth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: additionalScopes,
    include_granted_scopes: true, // Include previously granted scopes
  });
}
```

## Security Best Practices

| Practice | Description |
|----------|-------------|
| Never commit secrets | Use environment variables or Secret Manager |
| Validate redirect URI | Check against whitelist before redirecting |
| Use HTTPS in production | Required for OAuth2 security |
| Store tokens securely | Encrypt at rest, use secure session storage |
| Implement logout | Delete tokens and revoke with `oAuth2Client.revokeToken()` |
| Minimal scopes | Request only what you need |
| CSRF protection | Use state parameter in auth URL |

## Related Templates

- **`templates/ts/oauth2_web_server.ts`** - Complete Express server example
- **`templates/ts/types.ts`** - TokenStorage interface and branded token types
