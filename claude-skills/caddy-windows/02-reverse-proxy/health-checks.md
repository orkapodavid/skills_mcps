# Health Checks

**Summary:** Monitor backend health.

## Active Checks
```caddy
reverse_proxy node1:80 node2:80 node3:80 {
  health_uri /healthz
}
```

## Passive Checks
```caddy
reverse_proxy localhost:8080 {
  fail_duration 30s
  max_fails 2
}
```

## References
- https://caddyserver.com/docs/caddyfile/directives/reverse_proxy#active-health-checks
