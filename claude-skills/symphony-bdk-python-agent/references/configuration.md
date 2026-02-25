# Configuration Reference

Comprehensive guide to `config.yaml` structure and loading for `symphony-bdk-python`.

Official docs: https://symphony-bdk-python.finos.org/markdown/configuration.html

## Minimal Configuration

```yaml
host: mypod.symphony.com
bot:
  username: bot-username
  privateKey:
    path: /path/to/bot/rsa-private-key.pem
```

- `host` — hostname of the Symphony pod environment.
- `bot.username` — service account username as configured in the pod admin console.
- `bot.privateKey.path` — RSA private key matching the public key uploaded in admin console.

## Loading Configuration

Three methods available via `BdkConfigLoader`:

```python
from symphony.bdk.core.config.loader import BdkConfigLoader

# 1. From absolute file path
config = BdkConfigLoader.load_from_file("/absolute/path/to/config.yaml")

# 2. From string content
config = BdkConfigLoader.load_from_content(yaml_string)

# 3. From ~/.symphony/ directory (recommended for local dev)
config = BdkConfigLoader.load_from_symphony_dir("config.yaml")
```

Prefer `load_from_symphony_dir` for local development — keeps credentials out of the project codebase.

## Full Configuration Structure

```yaml
scheme: https
host: localhost.symphony.com
port: 8443

defaultHeaders:
  Connection: Keep-Alive
  Keep-Alive: timeout=5, max=1000

proxy:
  host: proxy.symphony.com
  port: 1234
  username: proxyuser
  password: proxypassword

pod:
  host: dev.symphony.com
  port: 443

agent:
  host: dev-agent.symphony.com
  port: 5678
  proxy:                          # per-component proxy override
    host: agent-proxy
    port: 3396

keyManager:
  host: dev-key.symphony.com
  port: 8444
  defaultHeaders:
    Connection: Keep-Alive
    Keep-Alive: close

sessionAuth:
  host: dev-session.symphony.com
  port: 8444

ssl:
  trustStore:
    path: /path/to/truststore.pem

bot:
  username: bot-name
  privateKey:
    path: /path/to/bot/rsa-private-key.pem

app:
  appId: app-id
  certificate:
    path: path/to/app-certificate.pem

datafeed:
  version: v2                     # v1 or v2; v2 is default
  retry:
    maxAttempts: 6
    initialIntervalMillis: 2000
    multiplier: 1.5
    maxIntervalMillis: 10000

datahose:
  tag: FANCY_TAG
  eventTypes:
    - INSTANTMESSAGECREATED
    - ROOMUPDATED
    - ROOMCREATED
  retry:
    maxAttempts: 61
    initialIntervalMillis: 20001
    multiplier: 1.51
    maxIntervalMillis: 100001

retry:
  maxAttempts: 6                  # -1 for infinite attempts; default 10
  initialIntervalMillis: 2000
  multiplier: 1.5
  maxIntervalMillis: 10000
```

## Configuration Fields

### Global Properties

| Field | Description |
|---|---|
| `scheme` | `https` (default) or `http` |
| `host` | Default hostname for all components |
| `port` | Default port for all components |
| `defaultHeaders` | Headers sent with every HTTP request; overridable per component |

### Component Overrides

Each of `pod`, `agent`, `keyManager`, `sessionAuth` accepts:
- `host`, `port`, `scheme`, `context` — override the global value
- `proxy` — component-specific proxy (overrides global proxy)
- `defaultHeaders` — component-specific headers

### Proxy

| Field | Required | Description |
|---|---|---|
| `host` | Yes | Proxy hostname |
| `port` | Yes | Proxy port |
| `username` | No | Proxy auth username |
| `password` | No | Proxy auth password |

Set at global level or per-component. Component-level proxy overrides global.

### SSL / TLS

```yaml
ssl:
  trustStore:
    path: /path/to/truststore.pem
```

- Path to PEM file of concatenated CA certificates.
- If omitted, the BDK loads system default certificates via `SSLContext.load_default_certs`.
- To extract a cert: `openssl s_client -connect <host>:<port> -showcerts > cert.pem`

### Bot Authentication

```yaml
bot:
  username: bot-name
  privateKey:
    path: /path/to/rsa-private-key.pem
```

### Extension App Authentication

```yaml
app:
  appId: app-id
  privateKey:
    path: /path/to/app-rsa-private-key.pem
  # OR
  certificate:
    path: /path/to/app-certificate.pem
```

### Retry Configuration

Global retry applies to all services. Override per-service via `datafeed.retry`, `datahose.retry`.

| Field | Default | Description |
|---|---|---|
| `maxAttempts` | 10 | Max retry attempts (`-1` = infinite) |
| `initialIntervalMillis` | 500 | Initial interval between first two attempts |
| `multiplier` | 2 | Exponential backoff multiplier |
| `maxIntervalMillis` | 300000 (5 min) | Upper bound on retry interval |

### Datafeed

| Field | Default | Description |
|---|---|---|
| `version` | `v2` | Datafeed version (`v1` or `v2`) |
| `retry.*` | (global) | Override retry for datafeed loop |

### Datahose

| Field | Description |
|---|---|
| `tag` | Unique tag identifying this datahose consumer |
| `eventTypes` | List of event types to subscribe to |
| `retry.*` | Override retry for datahose loop |

## Common Pitfalls

1. **Relative key paths** — The `privateKey.path` must be absolute or relative to the working directory. Use absolute paths to avoid runtime `FileNotFoundError`.
2. **Pod vs. agent host mismatch** — In on-premise deployments, `pod`, `agent`, and `keyManager` often have distinct hostnames.
3. **Datafeed version** — Use `v2` unless the pod only supports v1. The v2 API is more resilient.
4. **Proxy per-component** — If only the agent requires a proxy, set `agent.proxy` rather than the global `proxy` to avoid routing pod traffic through it.
5. **SSL trust store** — Required when the pod uses self-signed or internal CA certificates not in the system trust store.
