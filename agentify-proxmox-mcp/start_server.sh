#!/bin/bash
"""
Proxmox MCP server startup script
"""

echo "🚀 Starting Proxmox MCP server..."
echo ""

# Check virtual environment
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment does not exist, please run installation steps first"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Set environment variables
export PROXMOX_MCP_CONFIG="proxmox-config/config.json"

# Check configuration file
if [ ! -f "$PROXMOX_MCP_CONFIG" ]; then
    echo "❌ Configuration file does not exist: $PROXMOX_MCP_CONFIG"
    echo "Please ensure the configuration file is properly set up"
    exit 1
fi

echo "✅ Configuration file: $PROXMOX_MCP_CONFIG"
echo "✅ Virtual environment activated"
echo ""
echo "🔍 Starting server..."
echo "Press Ctrl+C to stop the server"
echo ""

# Start server
python -m proxmox_mcp.server 