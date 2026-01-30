# TypeScript Config Tips

- `strict: true` for reliability
- `esModuleInterop: true` to simplify imports
- `moduleResolution: node`
- Prefer ESM; use `--loader ts-node/esm` for running TS directly
- For production, transpile to `dist/` and run with `node dist/*.js`
