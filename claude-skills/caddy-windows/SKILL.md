---
name: caddy-windows
version: 0.1.0
description: This skill should be used when the user asks to "install Caddy on Windows", "configure a Caddy reverse proxy on Windows", "set up HTTPS for local development with Caddy on Windows", "run Caddy as a Windows service", or troubleshoot Caddy on Windows-specific behavior including firewall, certificates, and services.
tags:
  - caddy
  - windows
  - reverse-proxy
  - https
  - tls
  - local-development
  - devops
  - networking
  - reverse-proxy-patterns
use_cases:
  - Install and verify Caddy on Windows for local development
  - Configure Caddyfile for static sites and reverse proxy targets on Windows
  - Enable automatic HTTPS and local HTTPS development on Windows
  - Run Caddy as a Windows service and manage lifecycle
  - Configure Windows firewall and environment for Caddy
  - Debug Caddy issues specific to Windows
author: Claude Skills Library
created: 2026-01-17
updated: 2026-01-17
---

# Caddy on Windows Skill

## Overview

Provide structured guidance for installing, configuring, and operating Caddy on Windows, using the bundled Windows-focused documentation as references. Focus on local development, reverse proxying to backend services, HTTPS setup, and Windows-specific operational concerns.

Treat this skill as the entry point whenever a request mentions Caddy together with Windows, PowerShell, local reverse proxies, HTTPS on localhost, or running services on a Windows machine.

## When to Use This Skill

Trigger this skill when a user:
- Mentions "Caddy on Windows", "Caddy reverse proxy on Windows", or "Windows Caddyfile"
- Asks to expose a local app (Node, Python, .NET, etc.) through Caddy on Windows
- Wants automatic HTTPS or trusted certificates for localhost on Windows
- Needs to run Caddy as a Windows service or manage it in the background
- Encounters errors related to firewall, ports, certificates, or services on Windows while using Caddy

If the request is about generic Caddy concepts without Windows context, consider whether Windows-specific behavior matters. If ports, firewall, paths, or services are involved on a Windows host, prefer this skill.

## How to Use Bundled Resources

Use progressive disclosure when loading the Windows Caddy resources:

- Start from the high-level README:
  - Read `README.md` in this directory for a quick reminder of installation methods and basic usage on Windows.

- Load detailed guides only when needed:
  - Caddyfile syntax and basics:
    - `01-caddyfile-basics/caddyfile-syntax-guide.md`
    - `01-caddyfile-basics/directives-reference.md`
    - `01-caddyfile-basics/placeholders-functions.md`
  - Reverse proxy configuration patterns:
    - `02-reverse-proxy/basic-reverse-proxy.md`
    - `02-reverse-proxy/health-checks.md`
    - `02-reverse-proxy/multiple-upstreams.md`
  - HTTPS and certificates:
    - `03-ssl-tls/automatic-https.md`
    - `03-ssl-tls/local-development-https.md`
    - `03-ssl-tls/self-signed-certificates.md`
  - Common architectural patterns:
    - `04-common-patterns/api-gateway-pattern.md`
    - `04-common-patterns/protocol-bridging.md`
    - `04-common-patterns/request-rewriting.md`
    - `04-common-patterns/static-file-server.md`
  - Windows-specific behavior and troubleshooting:
    - `05-windows-specific/environment-variables.md`
    - `05-windows-specific/firewall-configuration.md`
    - `05-windows-specific/running-as-service.md`
    - `05-windows-specific/troubleshooting-windows.md`
  - Example Caddyfiles:
    - `06-examples/example-basic-config.Caddyfile`
    - `06-examples/example-development.Caddyfile`
    - `06-examples/example-load-balancer.Caddyfile`
    - `06-examples/example-api-gateway.Caddyfile`
  - Advanced topics:
    - `07-advanced/custom-plugins.md`
    - `07-advanced/monitoring-logging.md`
    - `07-advanced/performance-tuning.md`

Load only the specific files required for the current task to conserve context.

## Core Workflows

### Install and Verify Caddy on Windows

- Determine whether Caddy is already installed by running `caddy version` in PowerShell.
- If Caddy is missing or outdated, follow installation guidance referenced in `README.md`:
  - Consider Chocolatey, Scoop, Webi, or direct binary download based on user environment.
- After installation, validate with:
  - `caddy version` to confirm installation
  - A minimal Caddyfile responding on a high, non-privileged port (for example `:8080`).

Prefer non-elevated ports unless a strong reason exists to bind to privileged ports.

### Configure a Basic Windows Caddyfile

- For simple static responses or static files:
  - Use patterns from `01-caddyfile-basics/*` and `04-common-patterns/static-file-server.md`.
- For reverse proxying to a local app:
  - Use patterns from `02-reverse-proxy/basic-reverse-proxy.md` and `06-examples/example-development.Caddyfile`.
- Ensure Windows paths use backslashes where required and escape them correctly in Caddyfile directives.
- Validate every new or modified Caddyfile with:
  - `caddy validate --config Caddyfile`

### Set Up HTTPS and Local Development Certificates

- For automatic HTTPS with public domains, rely on `03-ssl-tls/automatic-https.md`.
- For localhost or internal network development on Windows:
  - Use `03-ssl-tls/local-development-https.md` to configure trusted local certificates.
  - Instruct the user when elevation is required, for example for `caddy trust`.
- When a corporate or custom CA is involved, consult `03-ssl-tls/self-signed-certificates.md`.

Avoid over-issuing certificates or using production ACME endpoints for purely local development scenarios.

### Run Caddy as a Windows Service

- When long-running background behavior is required, load:
  - `05-windows-specific/running-as-service.md`
  - `05-windows-specific/environment-variables.md`
- Use these references to:
  - Decide between running Caddy as a service, scheduled task, or foreground process.
  - Configure working directory, Caddyfile location, and environment variables compatible with Windows services.

Always call out the difference between testing a configuration in a foreground PowerShell session and the final service configuration.

### Manage Windows Firewall and Networking

- When port binding or connectivity fails on Windows:
  - Load `05-windows-specific/firewall-configuration.md`.
- Use this reference to:
  - Determine whether Windows Defender Firewall rules are required.
  - Distinguish between local-only access (`localhost`) and LAN access.
  - Recommend least-privilege firewall rules targeted at the specific ports and interfaces required.

Avoid suggesting blanket firewall disable actions; prefer constrained rules.

## Example-Driven Guidance

When designing or debugging Caddy configurations on Windows:

- Start from the example Caddyfiles in `06-examples/`:
  - Select the closest example to the user scenario (basic site, dev reverse proxy, load balancer, API gateway).
  - Adapt upstream addresses, ports, and domains for the user environment.
- Use the patterns in `04-common-patterns/*` to refine behavior:
  - Request rewriting
  - Static file hosting
  - Protocol bridging

Prefer incremental changes: validate and test after each modification rather than refactoring the entire Caddyfile in one step.

## Troubleshooting on Windows

For issues specific to Caddy running on Windows:

- Load `05-windows-specific/troubleshooting-windows.md` when:
  - Caddy fails to start only as a service, not in foreground.
  - Path resolution, environment variables, or permissions differ between PowerShell and service context.
  - Ports that work on Linux or macOS behave differently on Windows.
- Combine this with:
  - `--environ` and `--watch` flags for runtime diagnostics.
  - Relevant SSL/TLS references from `03-ssl-tls/*` when certificate errors appear.

Capture logs, command output, and relevant snippets of the Caddyfile before proposing major changes.

## Best Practices for Using This Skill

- Prefer small, validated configuration changes over large refactors.
- Keep Windows-specific behavior explicit: path handling, services, and firewall differences matter.
- Use the example Caddyfiles as templates rather than rewriting configurations from scratch.
- Only load detailed reference files when they directly inform the current task, to preserve context.

