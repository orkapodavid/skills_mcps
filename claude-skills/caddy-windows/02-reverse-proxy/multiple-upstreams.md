# Multiple Upstreams & Load Balancing

**Summary:** Distribute load across multiple backends.

## Example
```caddy
:8080 {
  reverse_proxy localhost:3001 localhost:3002 localhost:3003 {
    lb_policy round_robin
    health_uri /healthz
    lb_try_duration 5s
  }
}
```

## Sticky by Cookie
```caddy
:8080 {
  reverse_proxy /api/* node1:80 node2:80 node3:80 {
    lb_policy cookie api_sticky
  }
}
```

## References
- https://caddyserver.com/docs/caddyfile/directives/reverse_proxy#load-balancing
