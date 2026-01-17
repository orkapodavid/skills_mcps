# Protocol Bridging

**Summary:** Bridge HTTP to FastCGI/GRPC/WebSocket.

## FastCGI (PHP)
```caddy
:8080 {
  root * C:\\www
  php_fastcgi 127.0.0.1:9000
  file_server
}
```

## gRPC over h2c
```caddy
:8080 {
  reverse_proxy h2c://localhost:50051
}
```

## WebSockets
```caddy
:8080 {
  reverse_proxy localhost:3000
}
```

## References
- https://caddyserver.com/docs/caddyfile/directives/reverse_proxy#the-http-transport
- https://caddyserver.com/docs/caddyfile/directives/reverse_proxy#the-fastcgi-transport
