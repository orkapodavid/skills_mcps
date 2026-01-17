# Install via Docker on Windows

**Summary:** Run Caddy in Docker Desktop for isolated local dev.

## Prerequisites
- Docker Desktop

## Steps
1. Create `Caddyfile` in working dir.
2. `docker run --name caddy -p 80:80 -p 443:443 -p 2019:2019 -v "$PWD:/etc/caddy" -v caddy_data:/data -v caddy_config:/config caddy`

## Compose (recommended)
```yaml
services:
  caddy:
    image: caddy:latest
    ports:
      - "80:80"
      - "443:443"
      - "2019:2019" # admin API
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
volumes:
  caddy_data: {}
  caddy_config: {}
```

## Validation
- `curl -v https://localhost`

## References
- https://caddyserver.com/docs/install#docker
