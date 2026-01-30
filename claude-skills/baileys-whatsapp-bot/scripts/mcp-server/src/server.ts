import express from 'express'
import cors from 'cors'
import P from 'pino'
import makeWASocket, { useMultiFileAuthState } from '@whiskeysockets/baileys'

const logger = P({ level: 'info' })
const app = express()
app.use(cors())
app.use(express.json())

const AUTH_DIR = process.env.AUTH_DIR || './baileys_auth_info'
const PORT = Number(process.env.PORT || 8080)

let sock: ReturnType<typeof makeWASocket> | null = null

async function init() {
  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR)
  sock = makeWASocket({ auth: state, printQRInTerminal: true, logger })
  sock.ev.on('creds.update', saveCreds)
}

// Minimal MCP-like HTTP endpoints
app.post('/mcp/tool-call', async (req, res) => {
  try {
    const { tool, input } = req.body || {}
    if (!sock) return res.status(503).json({ error: 'Socket not ready' })
    switch (tool) {
      case 'send_message': {
        const { jid, text } = input || {}
        if (!jid || !text) return res.status(400).json({ error: 'jid and text required' })
        const result = await sock.sendMessage(jid, { text })
        return res.json({ ok: true, result })
      }
      case 'get_chats': {
        const chats = await sock!.groupFetchAllParticipating().catch(() => [])
        return res.json({ ok: true, chats })
      }
      case 'get_status': {
        const user = sock!.user
        return res.json({ ok: true, user })
      }
      default:
        return res.status(400).json({ error: 'unknown tool' })
    }
  } catch (e: any) {
    logger.error(e)
    res.status(500).json({ error: String(e?.message || e) })
  }
})

app.get('/mcp', (_req, res) => {
  res.json({ name: 'baileys-mcp', tools: ['send_message', 'get_chats', 'get_status'] })
})

init().then(() => {
  app.listen(PORT, () => logger.info(`MCP server listening on :${PORT}`))
})
