# Running as Service (Windows)

See 00-installation/install-as-windows-service.md for NSSM/WinSW instructions.

## Service Account
- Prefer a dedicated account with minimal privileges
- Grant write to Caddy data dir (e.g. `C:\\caddy\\data`)

## Logs
- Configure stdout/stderr log paths in the service manager

## Restart Policy
- Always restart on failure
