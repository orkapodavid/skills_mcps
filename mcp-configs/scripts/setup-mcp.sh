#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "=== MCP Setup Script (macOS/Linux) ==="
echo ""

# Detect tool
select_tool() {
    echo "Select tool to configure:"
    echo "1) Claude Desktop"
    echo "2) Claude Code"
    echo "3) Cursor"
    read -p "Choice [1-3]: " choice
    
    case $choice in
        1) setup_claude_desktop ;;
        2) setup_claude_code ;;
        3) setup_cursor ;;
        *) echo "Invalid choice"; exit 1 ;;
    esac
}

setup_claude_desktop() {
    echo ""
    echo "--- Setting up Claude Desktop ---"
    CONFIG_DIR="$HOME/Library/Application Support/Claude"
    mkdir -p "$CONFIG_DIR"
    
    if [[ -f "$CONFIG_DIR/claude_desktop_config.json" ]]; then
        echo "⚠️  Config file already exists"
        read -p "Backup and replace? [y/N]: " confirm
        if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
            backup_file="$CONFIG_DIR/claude_desktop_config.json.backup.$(date +%Y%m%d_%H%M%S)"
            cp "$CONFIG_DIR/claude_desktop_config.json" "$backup_file"
            echo "✓ Backup created: $backup_file"
        else
            echo "Setup cancelled"
            exit 0
        fi
    fi
    
    cp "$REPO_ROOT/mcp-configs/templates/claude-desktop/claude_desktop_config.macos.json" \
       "$CONFIG_DIR/claude_desktop_config.json"
    
    echo "✓ Config copied to: $CONFIG_DIR/claude_desktop_config.json"
    echo ""
    echo "Next steps:"
    echo "1. Edit the config file to add your credentials and paths"
    echo "2. Replace YOUR_USERNAME with your actual username"
    echo "3. Replace YOUR_GITHUB_PAT with your GitHub Personal Access Token"
    echo "4. Restart Claude Desktop"
    echo ""
    echo "Edit now? [y/N]: "
    read -p "" edit_now
    if [[ "$edit_now" == "y" || "$edit_now" == "Y" ]]; then
        ${EDITOR:-nano} "$CONFIG_DIR/claude_desktop_config.json"
    fi
}

setup_claude_code() {
    echo ""
    echo "--- Setting up Claude Code ---"
    read -p "Project path (or . for current directory): " project_path
    project_path="${project_path:-.}"
    project_path=$(cd "$project_path" && pwd)
    
    if [[ -f "$project_path/.mcp.json" ]]; then
        echo "⚠️  Config file already exists at $project_path/.mcp.json"
        read -p "Overwrite? [y/N]: " confirm
        if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
            echo "Setup cancelled"
            exit 0
        fi
    fi
    
    cp "$REPO_ROOT/mcp-configs/templates/claude-code/mcp.json" \
       "$project_path/.mcp.json"
    
    echo "✓ Config copied to: $project_path/.mcp.json"
    echo ""
    echo "Next steps:"
    echo "1. Set environment variables (e.g., export GITHUB_TOKEN=...)"
    echo "2. Customize the config if needed"
    echo "3. Run your Claude Code commands"
}

setup_cursor() {
    echo ""
    echo "--- Setting up Cursor ---"
    read -p "Project path (or . for current directory): " project_path
    project_path="${project_path:-.}"
    project_path=$(cd "$project_path" && pwd)
    
    mkdir -p "$project_path/.cursor"
    
    if [[ -f "$project_path/.cursor/mcp.json" ]]; then
        echo "⚠️  Config file already exists"
        read -p "Overwrite? [y/N]: " confirm
        if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
            echo "Setup cancelled"
            exit 0
        fi
    fi
    
    cp "$REPO_ROOT/mcp-configs/templates/cursor/mcp.json" \
       "$project_path/.cursor/mcp.json"
    
    echo "✓ Config copied to: $project_path/.cursor/mcp.json"
    echo ""
    echo "Next steps:"
    echo "1. Set environment variables (e.g., export GITHUB_TOKEN=...)"
    echo "2. Reload Cursor window (Cmd+Shift+P → Reload Window)"
}

# Main execution
select_tool
echo ""
echo "=== Setup complete ==="
