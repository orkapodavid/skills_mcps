# Baileys MCP Server (Streamable HTTP)

This guide helps you expose Baileys as remote tools for Claude Code.

## Overview
- Transport: Streamable HTTP
- Mount path: `/mcp`
- Tools:
  - `send_message(jid, text)`
  - `get_chats()`
  - `get_status()`

## Setup

1. Create a Node project:
```
mkdir mcp-server && cd mcp-server
npm init -y
npm install express @whiskeysockets/baileys pino cors
npm install -D typescript ts-node @types/node @types/express
```

2. Copy templates from `scripts/mcp-server/`

3. Configure env:
```
SOCKET_URL=https://web.whatsapp.com/ws
AUTH_DIR=./baileys_auth_info
PORT=8080
```

4. Run locally:
```
npx ts-node src/server.ts
```

5. Add to Claude Code:
```
claude mcp add --transport http baileys http://localhost:8080/mcp
```

6. Deploy to Cloud Run (optional):
- Use `assets/Dockerfile` and `assets/cloudrun.yaml`
- Expose `/mcp`

## Security Notes
- Protect the endpoint; require an API key header
- Rate-limit send_message
- Do not expose raw creds
