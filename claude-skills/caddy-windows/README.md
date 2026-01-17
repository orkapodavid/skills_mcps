# Caddy Skills for Windows

A curated set of Windows-focused guides, examples, and scripts to install, configure, and use Caddy for local development and reverse proxying.

## Quick Start

- Install Caddy on Windows (choose one):
  - Chocolatey: `choco install caddy`
  - Scoop: `scoop install caddy`
  - Webi: `curl.exe https://webi.ms/caddy | powershell`
  - Download binary: https://github.com/caddyserver/caddy/releases
- Verify: `caddy version`
- Run a basic site:
  - Create `Caddyfile` with:
    ```
    :8080 {
      respond "Hello from Caddy on Windows!"
    }
    ```
  - Start: `caddy run --config Caddyfile`
- Stop: Ctrl+C

## Cheat Sheet

- Validate config: `caddy validate --config Caddyfile`
- Reload config: `caddy reload --config Caddyfile`
- Trust local CA: `caddy trust` (run an elevated PowerShell)
- Untrust local CA: `caddy untrust`
- Reverse proxy: `reverse_proxy localhost:3000`
- Static files: `root * C:\\path\\to\\site` + `file_server`
- Logs: `--environ` to print environment; `--watch` to auto-reload

## See Also

- 01-caddyfile-basics/
- 02-reverse-proxy/
- 03-ssl-tls/
- 04-common-patterns/
- 05-windows-specific/
- 06-examples/
- 07-advanced/
