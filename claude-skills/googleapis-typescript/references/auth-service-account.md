# Service Account (JWT) Flow

Type-safe service account authentication for server-to-server API calls.

## When to Use

- Backend automation without user interaction
- Server-to-server API calls
- Accessing organization-owned resources
- CI/CD pipelines and scheduled jobs
- Microservices and Cloud Run deployments

## Setup

### 1. Create Service Account

1. Go to [Google Cloud Console > IAM > Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Click "Create Service Account"
3. Assign appropriate IAM roles (principle of least privilege)
4. For local development: Create and download a JSON key

### 2. Configure Environment

For local development:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

For Cloud Run (no key needed - use Workload Identity):
```bash
# Configure during deployment
gcloud run deploy SERVICE_NAME \
  --service-account=SERVICE_ACCOUNT_EMAIL \
  --allow-unauthenticated
```

## Environment Detection

Detect runtime environment for auth strategy selection:

```typescript
interface RuntimeEnvironment {
  readonly isCloudRun: boolean;
  readonly isGKE: boolean;
  readonly isLocal: boolean;
  readonly projectId?: string;
  readonly serviceAccount?: string;
}

function detectEnvironment(): RuntimeEnvironment {
  const isCloudRun = !!process.env.K_SERVICE;
  const isGKE = !!process.env.KUBERNETES_SERVICE_HOST;
  const projectId = process.env.GOOGLE_CLOUD_PROJECT ?? process.env.GCLOUD_PROJECT;

  return {
    isCloudRun,
    isGKE,
    isLocal: !isCloudRun && !isGKE,
    projectId,
    serviceAccount: process.env.GOOGLE_SERVICE_ACCOUNT,
  };
}
```

## Auth Client Factory

Create appropriate auth client based on environment:

```typescript
import { JWT, GoogleAuth } from 'google-auth-library';

type AuthClient = JWT | GoogleAuth;

function createAuthClient(scopes: readonly string[]): Result<AuthClient, ApiError> {
  const env = detectEnvironment();

  if (env.isCloudRun || env.isGKE) {
    // Use Application Default Credentials (Workload Identity)
    console.log('[Auth] Using Application Default Credentials');
    return ok(new GoogleAuth({ scopes: [...scopes] }));
  }

  // Local development - use key file
  const configResult = parseServiceAccountConfig(scopes);
  if (!configResult.success) {
    return err(configResult.error);
  }

  console.log('[Auth] Using service account key file');
  return ok(new JWT({
    keyFile: configResult.data.keyFilePath,
    scopes: [...scopes],
    subject: configResult.data.subject,
  }));
}
```

## Type-Safe Configuration

```typescript
interface ServiceAccountConfig {
  readonly keyFilePath: string;
  readonly scopes: readonly string[];
  readonly subject?: string; // For domain-wide delegation
}

function parseServiceAccountConfig(
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
```

## Common Scopes

| Scope | Description |
|-------|-------------|
| `cloud-platform` | Full access to all GCP APIs |
| `cloud-platform.read-only` | Read-only access to GCP APIs |
| `drive` | Full Drive access |
| `drive.readonly` | Read-only Drive access |
| `spreadsheets` | Full Sheets access |
| `spreadsheets.readonly` | Read-only Sheets access |
| `gmail.send` | Send emails only |
| `gmail.readonly` | Read emails only |

## Domain-Wide Delegation

For accessing user data without user consent (G Suite/Workspace):

### 1. Enable Domain-Wide Delegation

1. In Cloud Console, edit service account
2. Enable "Domain-wide delegation"
3. Note the Client ID

### 2. Configure Admin Console

1. Go to [Admin Console > Security > API Controls](https://admin.google.com/ac/owl/domainwidedelegation)
2. Add new API client
3. Enter Client ID and required scopes

### 3. Impersonate User

```typescript
function createDelegatedAuthClient(
  scopes: readonly string[],
  subject: string // User email to impersonate
): Result<JWT, ApiError> {
  const configResult = parseServiceAccountConfig(scopes);
  if (!configResult.success) {
    return err(configResult.error);
  }

  return ok(new JWT({
    keyFile: configResult.data.keyFilePath,
    scopes: [...scopes],
    subject, // Impersonate this user
  }));
}

// Usage: Access user's Drive as them
const authResult = createDelegatedAuthClient(
  ['https://www.googleapis.com/auth/drive.readonly'],
  'user@yourdomain.com'
);
```

## Workload Identity Federation

Preferred for production on GCP - eliminates key files:

### Cloud Run Setup

```bash
# Service account needs appropriate IAM roles
# No key file needed - identity is inherited

gcloud run deploy my-service \
  --image gcr.io/PROJECT/IMAGE \
  --service-account my-service-account@PROJECT.iam.gserviceaccount.com
```

### GKE Setup

```bash
# Configure Workload Identity
gcloud iam service-accounts add-iam-policy-binding \
  GSA_NAME@PROJECT.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:PROJECT.svc.id.goog[NAMESPACE/KSA_NAME]"

# Annotate Kubernetes service account
kubectl annotate serviceaccount KSA_NAME \
  iam.gke.io/gcp-service-account=GSA_NAME@PROJECT.iam.gserviceaccount.com
```

## Best Practices

| Practice | Description |
|----------|-------------|
| Prefer Workload Identity | No key files to manage, rotate, or leak |
| Minimal IAM roles | Grant only necessary permissions |
| Separate service accounts | One per service/function |
| Audit logs | Enable Cloud Audit Logs for API calls |
| Key rotation | If using keys, rotate regularly |
| Don't commit keys | Use Secret Manager or environment |

## IAM Role Examples

| Role | Use Case |
|------|----------|
| `roles/storage.objectViewer` | Read Cloud Storage objects |
| `roles/bigquery.dataViewer` | Query BigQuery datasets |
| `roles/drive.reader` | Read Drive files (domain-wide delegation) |
| `roles/logging.logWriter` | Write Cloud Logging entries |

## Related Templates

- **`templates/ts/service_account_jwt.ts`** - Environment-aware auth client
- **`templates/ts/types.ts`** - ServiceAccountConfig interface
