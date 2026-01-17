# Static File Server

**Summary:** Serve files from a Windows directory.

## Example
```caddy
:8080 {
  root * C:\\sites\\myapp\\public
  file_server
}
```

## Notes
- Use double backslashes in paths
- Add `encode gzip zstd` for compression

## References
- https://caddyserver.com/docs/caddyfile/directives/file_server
