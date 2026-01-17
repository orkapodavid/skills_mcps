# API Gateway Pattern

**Summary:** Route API requests to multiple backend services.

## Example
```caddy
api.local.test {
  @auth path /auth/*
  handle @auth {
    reverse_proxy localhost:7001
  }
  @users path /users/*
  handle @users {
    reverse_proxy localhost:7002
  }
}
```

## References
- https://caddyserver.com/docs/caddyfile/matchers
