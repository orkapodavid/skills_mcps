---
name: baileys-whatsapp-bot
description: This skill should be used when the user asks to "build a WhatsApp bot", "connect to WhatsApp", "configure Baileys", "persist WhatsApp session", "send WhatsApp messages", or "deploy WhatsApp bot to Cloud Run". It also supports requests to "expose WhatsApp tools" or "create a WhatsApp MCP server".
---

# Baileys WhatsApp Bot Skill

This skill provides concise, production-ready workflows to:
- Configure and connect a Baileys Socket
- Persist creds with `useMultiFileAuthState`
- Handle message and group events
- Send messages reliably
- Deploy to Google Cloud Run
- Optionally expose tools via a remote MCP server so Claude Code can send messages, list chats, and check connection status

Keep this SKILL.md lean. Load detailed references from the `references/` folder when needed.

## Quick Start

1. Install:
   - `npm install @whiskeysockets/baileys`
   - Node 18+ recommended; TypeScript preferred
2. Create socket:
   - `makeWASocket({ auth: state, printQRInTerminal: true })`
3. Persist creds:
   - Listen to `sock.ev.on('creds.update', saveCreds)`
4. Receive messages:
   - `sock.ev.on('messages.upsert', handler)`
5. Send messages:
   - `await sock.sendMessage(jid, { text: 'hello' })`

See `references/llms.txt` for condensed API context and links.

## Session Persistence (Cloud Run)

- Use `useMultiFileAuthState()` with a mounted volume or GCS-mirrored path
- On every `creds.update`, call `saveCreds()`
- Ensure the auth directory is persisted across deployments

## Event Handling Patterns

- `messages.upsert`: Parse `proto.IWebMessageInfo`; respond based on text/images
- `group-participants.update`: Welcome or audit changes
- `presence.update`, `chats.update`, `contacts.update`: For syncing state

## Deployment (Cloud Run)

- Use the `assets/Dockerfile` and `assets/cloudrun.yaml` templates
- Forward logs; handle graceful shutdown
- Scale to 0 with min instances if desired; ensure session storage persists

## Optional: Remote MCP Server

If you want Claude Code to call tools (send_message, get_chats, get_status), use the template MCP server in `scripts/mcp-server/` and expose HTTP at `/mcp`.

- Configure `tools`:
  - `send_message(jid, text)`
  - `get_chats()`
  - `get_status()`
- See `references/mcp-config.json` and `references/mcp-server.md` for instructions

## When to Load References

- For socket options and event catalog → open `references/llms.txt`
- For full example code → open `examples/example.ts`
- For MCP setup and Claude integration → open `references/mcp-server.md`
- For deploy templates → copy from `assets/` folder

## Safety and Limitations

- Respect WhatsApp Terms of Service and privacy laws
- Avoid spam; implement rate limits and opt-in messaging
- This skill does not include business catalog features; consult Baileys docs if needed
