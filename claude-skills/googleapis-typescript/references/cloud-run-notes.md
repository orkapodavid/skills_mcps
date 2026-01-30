# Cloud Run Deployment Notes

## Container
- Use Node 20+ base image.
- Include `ts-node` only for dev; compile for prod.

## Secrets
- Prefer Secret Manager; mount at runtime.
- Avoid bundling credentials in the image.

## Identity
- Use Workload Identity Federation for service-to-service access.
- Grant IAM roles minimally (e.g., `roles/drive.readonly`).

## Health checks
- Provide basic `/healthz` endpoint in your web server.
