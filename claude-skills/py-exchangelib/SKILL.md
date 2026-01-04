---
name: Exchangelib Microsoft Exchange Skill
description: This skill equips an LLM coder to automate Microsoft Exchange/Office 365 workflows via exchangelib (EWS). It should be used when building Python automation for email, calendar, contacts, rules, and mailbox synchronization with on-prem Exchange 2007–2016 or Office 365 using EWS, including OAuth and MSAL flows.
---

# Exchangelib Microsoft Exchange Skill

This skill provides procedural knowledge, scripts, and references to build robust Exchange automations with Python using exchangelib.

Use this skill when:
- Automating email sending, replying, forwarding, and bulk operations
- Managing calendar events (including recurring), meetings, and availability
- Working with contacts, distribution lists, attachments, and extended properties
- Implementing OAuth (application or delegated) and MSAL interactive auth
- Synchronizing mailboxes, subscribing to notifications (pull/push/streaming)
- Building fault-tolerant, performant EWS clients with connection tuning, proxies, TLS, and caching

## Quick Start

1) Install dependencies (Linux/macOS):
- Python 3.9+
- System libs: libxml2, libxslt
- Optional (Kerberos): libkrb5-dev, build-essential, libssl-dev, libffi-dev

```
pip install exchangelib[complete]
# Or minimal:
pip install exchangelib
```

2) Copy `.env.template` to `.env` and fill secrets.
3) Choose an auth path:
- Basic/NTLM for on-prem (if allowed)
- OAuth app (impersonation) for org-wide service accounts
- OAuth delegated (EWS.AccessAsUser.All) for single-account flows
- MSAL interactive to leverage browser SSO

4) Run scripts in `scripts/` (see sections below).

## Architecture & Best Practices

- Account model: Each workflow begins by constructing `Account(...)` with credentials or configuration.
- Autodiscover: Prefer autodiscover for variable environments; cache results when stable.
- Configuration: Set `server`, `auth_type`, `version`, and `max_connections` explicitly to avoid guessing in locked-down envs.
- Fault tolerance: Use `FaultTolerance(max_wait=...)` in `Configuration` for transient failures.
- Paging/chunking: Tune `EWSService.PAGE_SIZE` and `CHUNK_SIZE` or per-QuerySet `page_size`, `chunk_size`.
- Timezones: Use `EWSDateTime`, `EWSTimeZone` for correctness.
- Extended properties: Register custom fields for items/folders as needed.
- Security:
  - Prefer OAuth (application or delegated). Basic auth is deprecated on O365.
  - Rotate secrets; store tokens securely; implement `on_token_auto_refreshed()` to persist refreshed tokens.
  - Use custom transport adapters for proxies/TLS pinning when required.

## Setup & Authentication Workflows

- Basic/NTLM (on-prem): `Credentials(username, password)` + `Account(autodiscover=True, access_type=DELEGATE)`
- OAuth application (impersonation, org-wide): Create Azure App → grant `full_access_as_app` → use `OAuth2Credentials(client_id, client_secret, tenant_id)` → `Configuration(auth_type=OAUTH2)`
- OAuth delegated (single account): Azure App with `EWS.AccessAsUser.All` → `OAuth2LegacyCredentials(client_id, client_secret, tenant_id, username, password)`
- MSAL interactive (delegated): Azure App (no secret), desktop redirect `http://localhost` → `O365InteractiveConfiguration(client_id, username)`

See `scripts/` for runnable examples.

## Common Workflows

- Send email (with HTML body, cc/bcc, attachments)
- Save to Sent, reply, reply-all, forward
- Create calendar events, recurring patterns, cancel meetings, accept/decline requests
- Query with Django-like QuerySet (`filter`, `exclude`, `order_by`, `values_list`)
- Bulk operations: create/update/move/send/delete/archive
- Attachments: file and item attachments; streaming download
- Contacts: search GAL, manage indexed properties
- Rules: create/modify/delete Inbox rules
- OOF: read/write Out Of Office
- Subscriptions: pull/push/streaming; parse notifications
- Synchronization: `sync_hierarchy`, `sync_items`

## Error Handling & Troubleshooting

- Enable debug logging with `PrettyXmlHandler()` for wire-level XML inspection
- Use `FaultTolerance` and retry logic for transient failures
- Validate searchable fields via `ItemClass.FIELDS` and `is_searchable`
- Clear autodiscover cache when domains change

## Security & Compliance Notes

- Store secrets in environment variables or `.env`; do not hardcode
- Restrict scopes/permissions to minimum necessary
- Respect mailbox policies and rate limits; coordinate with Exchange admins
- TLS: Validate certs; pin roots via custom adapter if required

## References Bundle

See `references/` for offline docs extracted from https://ecederstrand.github.io/exchangelib/.

## Scripts Overview

- `setup_basic_auth.py`: Basic/NTLM on-prem connection
- `setup_oauth_client_credentials.py`: Org-wide app auth (impersonation)
- `setup_oauth_delegated_msal.py`: MSAL interactive delegated auth
- `send_email.py`: Compose and send, send-and-save
- `read_inbox.py`: Query inbox using QuerySet
- `create_calendar_event.py`: Create events, recurring patterns
- `sync_streaming.py`: Streaming subscription and event handling

Each script reads configuration from environment variables. See `.env.template`.

## How Claude Should Use This Skill

This skill should be used when building Python automations that integrate with Microsoft Exchange via EWS, requiring:
- Reliable mailbox operations, calendar workflows, and directory lookups
- OAuth/MSAL authentication flows in enterprise environments
- Bulk operations and synchronization with performance tuning

Claude should load `SKILL.md` and selectively include `references/` excerpts while writing code, and run `scripts/` as templates to accelerate implementation.
