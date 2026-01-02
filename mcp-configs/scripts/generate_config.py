#!/usr/bin/env python3
"""
MCP Configuration Generator

Generates a platform-specific `claude_desktop_config.json` with secure defaults.
- Detects OS (Windows/macOS/Linux)
- Sets up a dedicated workspace directory
- Configures default MCP servers (filesystem, github, postgres)
- Handles path formatting and shell commands
"""

import json
import os
import platform
import shutil
import sys
from pathlib import Path

def get_platform_details():
    system = platform.system().lower()
    if system == "windows":
        is_windows = True
        npx_cmd = "npx.cmd"
        app_data = os.getenv("APPDATA")
        if not app_data:
            print("Error: %APPDATA% not found.")
            sys.exit(1)
        config_dir = Path(app_data) / "Claude"
    elif system == "darwin":
        is_windows = False
        npx_cmd = "npx"
        config_dir = Path.home() / "Library" / "Application Support" / "Claude"
    else:
        # Linux/Other - assuming standard XDG or similar, but Claude Desktop is mostly Mac/Win
        # defaulting to local directory for safety or manual placement
        is_windows = False
        npx_cmd = "npx"
        config_dir = Path.cwd()

    return is_windows, npx_cmd, config_dir

def create_workspace():
    """Creates a dedicated workspace directory if it doesn't exist."""
    workspace = Path.home() / "claude_workspace"
    try:
        workspace.mkdir(parents=True, exist_ok=True)
        print(f"[+] Workspace directory ready: {workspace}")
    except Exception as e:
        print(f"[!] Could not create workspace {workspace}: {e}")
        # Fallback to current directory if home isn't writable
        workspace = Path.cwd() / "claude_workspace"
        workspace.mkdir(exist_ok=True)
        print(f"[+] Using fallback workspace: {workspace}")

    return str(workspace.resolve())

def generate_config(is_windows, npx_cmd, workspace_path):
    config = {
        "mcpServers": {
            "filesystem": {
                "command": npx_cmd,
                "args": [
                    "-y",
                    "@anthropic-ai/mcp-server-filesystem",
                    workspace_path
                ]
            },
            "github": {
                "command": npx_cmd,
                "args": [
                    "-y",
                    "@anthropic-ai/mcp-server-github"
                ],
                "env": {
                    "GITHUB_TOKEN": "YOUR_GITHUB_PAT_HERE"
                }
            },
            "postgres": {
                "command": npx_cmd,
                "args": [
                    "-y",
                    "@anthropic-ai/mcp-server-postgres"
                ],
                "env": {
                    "POSTGRES_CONNECTION_STRING": "postgresql://user:password@localhost:5432/dbname"
                }
            }
        }
    }

    # Add a warning comment field (technically not standard JSON, but some parsers allow it,
    # or it just sits as a key). To be safe and compliant, we'll omit it or put it in a separate file.
    # We will print the warning to stdout instead.

    return config

def main():
    print("=== Claude MCP Configuration Generator ===")

    is_windows, npx_cmd, config_dir = get_platform_details()
    workspace_path = create_workspace()

    config = generate_config(is_windows, npx_cmd, workspace_path)
    config_json = json.dumps(config, indent=2)

    output_path = config_dir / "claude_desktop_config.json"

    print("\nGenerated Configuration:")
    print(config_json)
    print("\n" + "-"*40)

    print(f"Target Configuration File: {output_path}")

    # Check if file exists
    if output_path.exists():
        response = input(f"\n[?] File {output_path} already exists. Overwrite? (y/N): ").lower()
        if response != 'y':
            print("Operation cancelled. You can copy the JSON above manually.")
            sys.exit(0)

    try:
        if not output_path.parent.exists():
            print(f"[+] Creating directory: {output_path.parent}")
            output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_text(config_json, encoding='utf-8')
        print(f"[+] Successfully wrote configuration to {output_path}")
    except Exception as e:
        print(f"[!] Error writing file: {e}")
        sys.exit(1)

    print("\n[IMPORTANT] Next Steps:")
    print("1. Edit the file to add your real GITHUB_TOKEN and DB credentials.")
    print("2. DO NOT commit this file to version control if it contains secrets.")
    print("3. Restart Claude Desktop to apply changes.")

if __name__ == "__main__":
    main()
