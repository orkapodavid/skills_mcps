# Request Rewriting

**Summary:** Change paths before proxying.

## Strip Prefix
```caddy
:8080 {
  handle_path /api/* {
    reverse_proxy localhost:3000
  }
}
```

## Replace Prefix
```caddy
:8080 {
  handle_path /old/* {
    rewrite * /new{path}
    reverse_proxy localhost:3000
  }
}
```

## References
- https://caddyserver.com/docs/caddyfile/directives/rewrite
- https://caddyserver.com/docs/caddyfile/directives/handle_path
