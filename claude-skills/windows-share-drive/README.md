# Windows Shared Drive Skill for Python (Non-MCP)

This skill provides simple, agent-friendly functions to save and read files on a Windows shared drive (SMB) using a service account. It supports both cross-platform access (smbprotocol) and native Windows UNC with credentials (pywin32).

- Cross-platform backend: smbprotocol.smbclient (SMBv2/3)
- Windows-native backend: pywin32 (WNetAddConnection2) + standard file I/O
- Service account auth: DOMAIN\username + password

## Features
- Write text/bytes to `\\\\server\\share\\path\\to\\file`
- Read text/bytes
- List directories, check existence, create directories
- Automatic backend selection: prefers `pywin32` on Windows; otherwise falls back to `smbprotocol`
- Minimal API tailored for LLM coders and agent runtimes

## Installation

```bash
# Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration
Set the following environment variables (recommended) or pass them programmatically:

- `WSK_DOMAIN` — e.g., `ACME`
- `WSK_USERNAME` — service account username
- `WSK_PASSWORD` — service account password
- `WSK_SERVER` — Windows Server host, e.g., `fileserver01`
- `WSK_SHARE` — Share name, e.g., `Data`
- `WSK_BASE_PATH` — Optional subfolder base, e.g., `Team/Reports`
- `WSK_ENCODING` — Optional text encoding (default `utf-8`)

## Quick Start

```python
from skill.smb_client import WindowsShareClient

client = WindowsShareClient.from_env()

# Write text file
client.write_text("reports/hello.txt", "Hello from agent skill!\n")

# Read it back
content = client.read_text("reports/hello.txt")
print(content)

# Write bytes
client.write_bytes("binaries/blob.bin", b"\x00\x01\x02")

# List directory
print(client.list_dir("reports"))
```

## Example (Runnable)

```bash
python examples/example_save_and_read.py
```

## Notes
- On Windows, if running under a service, ensure the service account has network access rights and can authenticate to the share.
- For smbprotocol backend, SMB signing/requirements depend on server policy. The library handles SMB2/3.
- Avoid hardcoding credentials. Prefer environment variables or a secret manager.

## References
- smbprotocol (smbclient): https://pypi.org/project/smbprotocol/
- WNetAddConnection2 docs: https://learn.microsoft.com/en-us/windows/win32/wnet/adding-a-network-connection

## License
MIT
