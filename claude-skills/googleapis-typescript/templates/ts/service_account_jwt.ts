/**
 * Service Account (JWT) Flow Example
 * 
 * Type-safe service account authentication with environment detection.
 * 
 * Prerequisites:
 * - npm i googleapis google-auth-library
 * - Set GOOGLE_APPLICATION_CREDENTIALS for local development
 * - On Cloud Run, use Workload Identity Federation (no key file needed)
 */

import { google, cloudresourcemanager_v1 } from 'googleapis';
import { JWT, GoogleAuth } from 'google-auth-library';
import {
  Result,
  ApiError,
  ServiceAccountConfig,
  parseServiceAccountConfig,
  ok,
  err,
  ApiErrors,
} from './types.js';
import { withRetry, classifyError } from './utils/retry.js';

// ============================================================
// Environment Detection
// ============================================================

export interface RuntimeEnvironment {
  readonly isCloudRun: boolean;
  readonly isGKE: boolean;
  readonly isLocal: boolean;
  readonly projectId?: string;
  readonly serviceAccount?: string;
}

/**
 * Detect runtime environment for auth strategy selection.
 */
export function detectEnvironment(): RuntimeEnvironment {
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

// ============================================================
// Auth Factory
// ============================================================

export type AuthClient = JWT | GoogleAuth;

/**
 * Create appropriate auth client based on environment.
 * 
 * - Cloud Run / GKE: Use Application Default Credentials (Workload Identity)
 * - Local: Use service account key file
 */
export function createAuthClient(
  scopes: readonly string[]
): Result<AuthClient, ApiError> {
  const env = detectEnvironment();

  if (env.isCloudRun || env.isGKE) {
    // Use ADC - Workload Identity Federation
    console.log('[Auth] Using Application Default Credentials');
    return ok(
      new GoogleAuth({
        scopes: [...scopes],
      })
    );
  }

  // Local development - use key file
  const configResult = parseServiceAccountConfig(scopes);
  if (!configResult.success) {
    return err(configResult.error);
  }

  console.log('[Auth] Using service account key file');
  return ok(
    new JWT({
      keyFile: configResult.data.keyFilePath,
      scopes: [...scopes],
      subject: configResult.data.subject, // For domain-wide delegation
    })
  );
}

// ============================================================
// Type-Safe API Methods
// ============================================================

export interface Project {
  readonly projectId: string;
  readonly name: string;
  readonly lifecycleState: string;
}

/**
 * List GCP projects with type-safe Result pattern.
 */
export async function listProjects(
  auth: AuthClient
): Promise<Result<Project[], ApiError>> {
  return withRetry(async () => {
    try {
      const crm = google.cloudresourcemanager({ version: 'v1', auth });
      const response = await crm.projects.list();

      const projects: Project[] = (response.data.projects ?? []).map((p) => ({
        projectId: p.projectId ?? '',
        name: p.name ?? '',
        lifecycleState: p.lifecycleState ?? 'UNKNOWN',
      }));

      return ok(projects);
    } catch (error) {
      return err(classifyError(error));
    }
  });
}

/**
 * Get project details by ID.
 */
export async function getProject(
  auth: AuthClient,
  projectId: string
): Promise<Result<Project, ApiError>> {
  return withRetry(async () => {
    try {
      const crm = google.cloudresourcemanager({ version: 'v1', auth });
      const response = await crm.projects.get({ projectId });

      const p = response.data;
      return ok({
        projectId: p.projectId ?? '',
        name: p.name ?? '',
        lifecycleState: p.lifecycleState ?? 'UNKNOWN',
      });
    } catch (error) {
      return err(classifyError(error));
    }
  });
}

// ============================================================
// Domain-Wide Delegation Helper
// ============================================================

/**
 * Create auth client with domain-wide delegation.
 * 
 * Requires:
 * 1. Service account with domain-wide delegation enabled
 * 2. Admin console grant to service account
 */
export function createDelegatedAuthClient(
  scopes: readonly string[],
  subject: string // User email to impersonate
): Result<JWT, ApiError> {
  const configResult = parseServiceAccountConfig(scopes);
  if (!configResult.success) {
    return err(configResult.error);
  }

  return ok(
    new JWT({
      keyFile: configResult.data.keyFilePath,
      scopes: [...scopes],
      subject,
    })
  );
}

// ============================================================
// Example Usage
// ============================================================

async function main(): Promise<void> {
  const env = detectEnvironment();
  console.log('Runtime environment:', env);

  // Create auth client (auto-detects environment)
  const authResult = createAuthClient([
    'https://www.googleapis.com/auth/cloud-platform.read-only',
  ]);

  if (!authResult.success) {
    console.error('Auth setup failed:', authResult.error.message);
    process.exit(1);
  }

  // List projects with Result handling
  const projectsResult = await listProjects(authResult.data);

  if (!projectsResult.success) {
    switch (projectsResult.error.kind) {
      case 'auth':
        console.error('Authentication failed. Check credentials.');
        break;
      case 'quota':
        console.error('Quota exceeded. Retry after:', projectsResult.error.retryAfterMs);
        break;
      default:
        console.error('Error:', projectsResult.error.message);
    }
    process.exit(1);
  }

  console.log('Projects found:', projectsResult.data.length);
  for (const project of projectsResult.data) {
    console.log(`- ${project.projectId}: ${project.name} (${project.lifecycleState})`);
  }
}

main();
