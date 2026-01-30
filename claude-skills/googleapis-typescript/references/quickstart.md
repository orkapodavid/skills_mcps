# Quickstart

This skill targets the official Google APIs Node.js client with TypeScript.

Primary docs:
- Repo: https://github.com/googleapis/google-api-nodejs-client#readme
- NPM: https://www.npmjs.com/package/googleapis
- API reference: https://googleapis.dev/nodejs/googleapis/latest/

## Install
```
npm i googleapis google-auth-library
npm i -D typescript ts-node @types/node
```

## Minimal tsconfig.json
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ES2020",
    "moduleResolution": "node",
    "strict": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "outDir": "dist"
  },
  "include": ["templates/ts/**/*.ts", "src/**/*.ts"]
}
```

## Choosing auth
- OAuth2: end-user consent flow
- Service Account: server-to-server (preferred for backend automation)

## Common scopes
- Drive read: `https://www.googleapis.com/auth/drive.readonly`
- Sheets write: `https://www.googleapis.com/auth/spreadsheets`
- Gmail send: `https://www.googleapis.com/auth/gmail.send`

## Run examples
```
node --loader ts-node/esm templates/ts/drive_list_files.ts
node --loader ts-node/esm templates/ts/sheets_append_values.ts
node --loader ts-node/esm templates/ts/gmail_send_message.ts
```
