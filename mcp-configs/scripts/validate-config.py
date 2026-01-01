#!/usr/bin/env python3
"""Validate MCP configuration files."""

import json
import sys
from pathlib import Path

def validate_mcp_config(config_path: str) -> bool:
    """
    Validate an MCP configuration file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        True if valid, False otherwise
    """
    path = Path(config_path)
    
    if not path.exists():
        print(f"❌ ERROR: File not found: {config_path}")
        return False
    
    # Check JSON syntax
    try:
        with open(path) as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON: {e}")
        return False
    
    # Check structure
    if "mcpServers" not in config:
        print("⚠️  WARNING: No 'mcpServers' key found")
        print("   Config is valid JSON but appears empty")
        return True  # Valid JSON, just empty
    
    servers = config["mcpServers"]
    if not servers:
        print("⚠️  WARNING: 'mcpServers' object is empty")
        return True
    
    # Validate each server
    issues = []
    warnings = []
    
    for name, server in servers.items():
        if not isinstance(server, dict):
            issues.append(f"Server '{name}': must be an object")
            continue
            
        if "command" not in server:
            issues.append(f"Server '{name}': missing required 'command' field")
        
        if "args" not in server:
            issues.append(f"Server '{name}': missing required 'args' field")
        elif not isinstance(server["args"], list):
            issues.append(f"Server '{name}': 'args' must be an array")
        
        # Check for placeholder values
        server_str = json.dumps(server)
        if "YOUR_" in server_str:
            warnings.append(f"Server '{name}': contains placeholder values (YOUR_...)")
        
        # Check environment variables
        if "env" in server:
            if not isinstance(server["env"], dict):
                issues.append(f"Server '{name}': 'env' must be an object")
            else:
                for key, value in server["env"].items():
                    if value.startswith("YOUR_") or value == "":
                        warnings.append(f"Server '{name}': env variable '{key}' not configured")
    
    # Report results
    if issues:
        print("❌ ERRORS found:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    
    if warnings:
        print("⚠️  WARNINGS:")
        for warning in warnings:
            print(f"   - {warning}")
        print("")
        print(f"✓ {len(servers)} server(s) configured (with warnings)")
        return True
    
    print(f"✅ OK: {len(servers)} server(s) configured correctly")
    for name in servers.keys():
        print(f"   - {name}")
    return True

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: validate-config.py <config-file>")
        print("")
        print("Examples:")
        print("  python3 validate-config.py ~/.config/claude/claude_desktop_config.json")
        print("  python3 validate-config.py .mcp.json")
        sys.exit(1)
    
    config_file = sys.argv[1]
    success = validate_mcp_config(config_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
