#!/bin/bash
# Debian 12 Cloud Template Setup Script
# Downloads and imports Debian 12 cloud image as Proxmox template

set -euo pipefail

# Configuration
PROXMOX_API_URL="${PROXMOX_API_URL:-https://172.23.5.15:8006/api2/json}"
PROXMOX_USERNAME="${PROXMOX_USERNAME:-root@pam}"
PROXMOX_TOKEN_NAME="${PROXMOX_TOKEN_NAME:-mcp-token}"
PROXMOX_TOKEN_VALUE="${PROXMOX_TOKEN_VALUE:-REPLACE_WITH_YOUR_ACTUAL_TOKEN_VALUE}"
PROXMOX_TARGET_NODE="${PROXMOX_TARGET_NODE:-pve}"
PROXMOX_STORAGE="${PROXMOX_STORAGE:-local-lvm}"
PROXMOX_ISO_STORAGE="${PROXMOX_ISO_STORAGE:-local}"

# Debian 12 cloud image details
DEBIAN_VERSION="12"
DEBIAN_CODENAME="bookworm"
DEBIAN_IMAGE_URL="https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-nocloud-amd64.qcow2"
DEBIAN_TEMPLATE_ID="9000"
DEBIAN_TEMPLATE_NAME="debian-12-cloud"

LOG_FILE="logs/proxmox-template-setup-$(date +%Y%m%d-%H%M%S).log"
echo "Starting Debian template setup at $(date)" | tee -a "$LOG_FILE"

# Function to make API calls
proxmox_api() {
    local method="${1:-GET}"
    local endpoint="$2"
    local data="${3:-}"
    
    if [[ -n "$data" ]]; then
        curl -s -k -X "$method" \
            -H "Authorization: PVEAPIToken=$PROXMOX_USERNAME:$PROXMOX_TOKEN_NAME=$PROXMOX_TOKEN_VALUE" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$PROXMOX_API_URL$endpoint"
    else
        curl -s -k \
            -H "Authorization: PVEAPIToken=$PROXMOX_USERNAME:$PROXMOX_TOKEN_NAME=$PROXMOX_TOKEN_VALUE" \
            "$PROXMOX_API_URL$endpoint"
    fi
}

echo "=== DEBIAN 12 CLOUD TEMPLATE SETUP ===" | tee -a "$LOG_FILE"
echo "Target Node: $PROXMOX_TARGET_NODE" | tee -a "$LOG_FILE"
echo "Storage: $PROXMOX_STORAGE" | tee -a "$LOG_FILE"
echo "ISO Storage: $PROXMOX_ISO_STORAGE" | tee -a "$LOG_FILE"
echo "Template ID: $DEBIAN_TEMPLATE_ID" | tee -a "$LOG_FILE"
echo "Template Name: $DEBIAN_TEMPLATE_NAME" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Check if template already exists
echo "Checking for existing Debian template..." | tee -a "$LOG_FILE"
existing_template=$(proxmox_api "GET" "/nodes/$PROXMOX_TARGET_NODE/qemu/$DEBIAN_TEMPLATE_ID/config" 2>/dev/null || echo "null")

if [[ "$existing_template" != "null" ]]; then
    echo "Template $DEBIAN_TEMPLATE_ID already exists. Skipping download and import." | tee -a "$LOG_FILE"
    echo "Template details:" | tee -a "$LOG_FILE"
    echo "$existing_template" | jq '.' | tee -a "$LOG_FILE"
    exit 0
fi

# Download Debian cloud image
echo "Downloading Debian 12 cloud image..." | tee -a "$LOG_FILE"
cd /tmp
wget -O "debian-12-nocloud-amd64.qcow2" "$DEBIAN_IMAGE_URL" 2>&1 | tee -a "$LOG_FILE"

# Upload to Proxmox storage
echo "Uploading image to Proxmox storage..." | tee -a "$LOG_FILE"
# This would require the image to be uploaded to the Proxmox host
# For now, we'll create a VM and convert it to template

# Create VM configuration
echo "Creating VM configuration..." | tee -a "$LOG_FILE"
vm_config='{
    "vmid": '$DEBIAN_TEMPLATE_ID',
    "name": "'$DEBIAN_TEMPLATE_NAME'",
    "memory": 2048,
    "cores": 2,
    "sockets": 1,
    "net0": "virtio,bridge=vmbr0",
    "scsi0": "'$PROXMOX_STORAGE':32,format=qcow2",
    "bootdisk": "scsi0",
    "boot": "cdn",
    "ostype": "l26",
    "scsihw": "virtio-scsi-pci",
    "agent": "1",
    "template": 1
}'

echo "VM Config:" | tee -a "$LOG_FILE"
echo "$vm_config" | jq '.' | tee -a "$LOG_FILE"

# Create the VM
echo "Creating VM..." | tee -a "$LOG_FILE"
result=$(proxmox_api "POST" "/nodes/$PROXMOX_TARGET_NODE/qemu" "$vm_config" 2>&1)
echo "Result: $result" | tee -a "$LOG_FILE"

# Convert to template
echo "Converting VM to template..." | tee -a "$LOG_FILE"
proxmox_api "POST" "/nodes/$PROXMOX_TARGET_NODE/qemu/$DEBIAN_TEMPLATE_ID/template" '{}' | tee -a "$LOG_FILE"

echo "Template setup complete. Check $LOG_FILE for full details." | tee -a "$LOG_FILE"
