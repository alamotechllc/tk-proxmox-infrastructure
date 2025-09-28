#!/bin/bash
# Proxmox Infrastructure Discovery Script
# Run this to discover your current Proxmox setup before automation

set -euo pipefail

# Configuration
PROXMOX_API_URL="${PROXMOX_API_URL:-https://172.23.5.15:8006/api2/json}"
PROXMOX_USERNAME="${PROXMOX_USERNAME:-root@pam}"
PROXMOX_TOKEN_NAME="${PROXMOX_TOKEN_NAME:-mcp-token}"
PROXMOX_TOKEN_VALUE="${PROXMOX_TOKEN_VALUE:-REPLACE_WITH_YOUR_ACTUAL_TOKEN_VALUE}"

LOG_FILE="logs/proxmox-discovery-$(date +%Y%m%d-%H%M%S).log"
echo "Starting Proxmox discovery at $(date)" | tee -a "$LOG_FILE"

# Function to make API calls
proxmox_api() {
    local endpoint="$1"
    curl -s -k \
        -H "Authorization: PVEAPIToken=$PROXMOX_USERNAME:$PROXMOX_TOKEN_NAME=$PROXMOX_TOKEN_VALUE" \
        "$PROXMOX_API_URL$endpoint" | jq '.'
}

echo "=== PROXMOX INFRASTRUCTURE DISCOVERY ===" | tee -a "$LOG_FILE"
echo "API URL: $PROXMOX_API_URL" | tee -a "$LOG_FILE"
echo "User: $PROXMOX_USERNAME" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 1. Cluster Status
echo "1. CLUSTER STATUS" | tee -a "$LOG_FILE"
echo "----------------" | tee -a "$LOG_FILE"
proxmox_api "/cluster/status" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 2. Nodes
echo "2. AVAILABLE NODES" | tee -a "$LOG_FILE"
echo "-----------------" | tee -a "$LOG_FILE"
proxmox_api "/nodes" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 3. Storage
echo "3. AVAILABLE STORAGE" | tee -a "$LOG_FILE"
echo "-------------------" | tee -a "$LOG_FILE"
proxmox_api "/storage" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 4. Networks
echo "4. AVAILABLE NETWORKS" | tee -a "$LOG_FILE"
echo "--------------------" | tee -a "$LOG_FILE"
proxmox_api "/cluster/network" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 5. Templates
echo "5. AVAILABLE TEMPLATES" | tee -a "$LOG_FILE"
echo "---------------------" | tee -a "$LOG_FILE"
# Check each node for templates
nodes=$(proxmox_api "/nodes" | jq -r '.[] | select(.type == "node") | .node')
for node in $nodes; do
    echo "Templates on node $node:" | tee -a "$LOG_FILE"
    proxmox_api "/nodes/$node/qemu" | jq '.[] | select(.template == 1) | {vmid, name, template}' | tee -a "$LOG_FILE"
done
echo "" | tee -a "$LOG_FILE"

# 6. ISOs
echo "6. AVAILABLE ISO IMAGES" | tee -a "$LOG_FILE"
echo "----------------------" | tee -a "$LOG_FILE"
for node in $nodes; do
    echo "ISOs on node $node:" | tee -a "$LOG_FILE"
    proxmox_api "/nodes/$node/storage/local/content" | jq '.[] | select(.volid | contains(".iso")) | .volid' | tee -a "$LOG_FILE"
done
echo "" | tee -a "$LOG_FILE"

echo "Discovery complete. Check $LOG_FILE for full details." | tee -a "$LOG_FILE"
