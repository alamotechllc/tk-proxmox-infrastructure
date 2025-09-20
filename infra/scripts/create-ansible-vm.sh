#!/bin/bash
# Ansible Control Node VM Creation Script
# Creates and configures the Ansible control node VM

set -euo pipefail

# Configuration
PROXMOX_API_URL="${PROXMOX_API_URL:-https://172.23.5.15:8006/api2/json}"
PROXMOX_USERNAME="${PROXMOX_USERNAME:-root@pam}"
PROXMOX_TOKEN_NAME="${PROXMOX_TOKEN_NAME:-mcp-token}"
PROXMOX_TOKEN_VALUE="${PROXMOX_TOKEN_VALUE:-REPLACE_WITH_YOUR_ACTUAL_TOKEN_VALUE}"
PROXMOX_TARGET_NODE="${PROXMOX_TARGET_NODE:-pve}"
PROXMOX_STORAGE="${PROXMOX_STORAGE:-local-lvm}"
PROXMOX_BRIDGE="${PROXMOX_BRIDGE:-vmbr0}"

# Ansible VM Configuration
ANSIBLE_VM_NAME="${ANSIBLE_VM_NAME:-ansible-control}"
ANSIBLE_VM_VMID="${ANSIBLE_VM_VMID:-9001}"
ANSIBLE_VM_VCPUS="${ANSIBLE_VM_VCPUS:-2}"
ANSIBLE_VM_RAM_MB="${ANSIBLE_VM_RAM_MB:-4096}"
ANSIBLE_VM_DISK_GB="${ANSIBLE_VM_DISK_GB:-40}"
ANSIBLE_VM_NET="${ANSIBLE_VM_NET:-dhcp}"
ANSIBLE_VM_STATIC_IP="${ANSIBLE_VM_STATIC_IP:-}"
ANSIBLE_VM_GW="${ANSIBLE_VM_GW:-}"
DNS_SERVERS="${DNS_SERVERS:-1.1.1.1 9.9.9.9}"
SSH_PUBKEY="${SSH_PUBKEY:-}"

# Template Configuration
DEBIAN_TEMPLATE_ID="9000"

LOG_FILE="logs/proxmox-ansible-vm-$(date +%Y%m%d-%H%M%S).log"
echo "Starting Ansible VM creation at $(date)" | tee -a "$LOG_FILE"

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

echo "=== ANSIBLE CONTROL NODE VM CREATION ===" | tee -a "$LOG_FILE"
echo "VM Name: $ANSIBLE_VM_NAME" | tee -a "$LOG_FILE"
echo "VM ID: $ANSIBLE_VM_VMID" | tee -a "$LOG_FILE"
echo "CPUs: $ANSIBLE_VM_VCPUS" | tee -a "$LOG_FILE"
echo "RAM: ${ANSIBLE_VM_RAM_MB}MB" | tee -a "$LOG_FILE"
echo "Disk: ${ANSIBLE_VM_DISK_GB}GB" | tee -a "$LOG_FILE"
echo "Network: $ANSIBLE_VM_NET" | tee -a "$LOG_FILE"
echo "Target Node: $PROXMOX_TARGET_NODE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Check if VM already exists
echo "Checking for existing VM..." | tee -a "$LOG_FILE"
existing_vm=$(proxmox_api "GET" "/nodes/$PROXMOX_TARGET_NODE/qemu/$ANSIBLE_VM_VMID/config" 2>/dev/null || echo "null")

if [[ "$existing_vm" != "null" ]]; then
    echo "VM $ANSIBLE_VM_VMID already exists!" | tee -a "$LOG_FILE"
    echo "VM details:" | tee -a "$LOG_FILE"
    echo "$existing_vm" | jq '.' | tee -a "$LOG_FILE"
    echo "Skipping creation. Use --force to recreate." | tee -a "$LOG_FILE"
    exit 1
fi

# Check if template exists
echo "Checking for Debian template..." | tee -a "$LOG_FILE"
template_exists=$(proxmox_api "GET" "/nodes/$PROXMOX_TARGET_NODE/qemu/$DEBIAN_TEMPLATE_ID/config" 2>/dev/null || echo "null")

if [[ "$template_exists" == "null" ]]; then
    echo "ERROR: Debian template $DEBIAN_TEMPLATE_ID not found!" | tee -a "$LOG_FILE"
    echo "Please run setup-debian-template.sh first." | tee -a "$LOG_FILE"
    exit 1
fi

# Prepare cloud-init configuration
echo "Preparing cloud-init configuration..." | tee -a "$LOG_FILE"

# Generate cloud-init user data
cat > /tmp/user-data.yml << EOF
#cloud-config
hostname: $ANSIBLE_VM_NAME
manage_etc_hosts: true

users:
  - name: ansible
    groups: [adm, audio, cdrom, dialout, dip, floppy, lxd, netdev, plugdev, sudo, video]
    lock_passwd: false
    shell: /bin/bash
    ssh_authorized_keys:
      - $SSH_PUBKEY
    sudo: ['ALL=(ALL) NOPASSWD:ALL']

# Disable root login
disable_root: true

# Package management
package_update: true
package_upgrade: true
packages:
  - python3
  - python3-pip
  - git
  - curl
  - wget
  - jq
  - tmux
  - rsync
  - vim
  - htop
  - ufw

# Network configuration
EOF

if [[ "$ANSIBLE_VM_NET" == "static" && -n "$ANSIBLE_VM_STATIC_IP" ]]; then
    cat >> /tmp/user-data.yml << EOF
network:
  version: 2
  ethernets:
    eth0:
      addresses:
        - $ANSIBLE_VM_STATIC_IP
      gateway4: $ANSIBLE_VM_GW
      nameservers:
        addresses: [$DNS_SERVERS]
EOF
fi

cat >> /tmp/user-data.yml << EOF

# Security hardening
runcmd:
  - ufw --force enable
  - ufw default deny incoming
  - ufw default allow outgoing
  - ufw allow ssh
  - systemctl enable ufw

# Create ansible user directory structure
  - mkdir -p /home/ansible/infra/ansible/{inventories/prod,playbooks/proxmox,roles}
  - mkdir -p /home/ansible/infra/scripts
  - chown -R ansible:ansible /home/ansible/infra

# Final message
final_message: "Ansible control node setup complete. SSH access configured for user: ansible"
EOF

# Create cloud-init meta data
cat > /tmp/meta-data.yml << EOF
instance-id: $ANSIBLE_VM_NAME
local-hostname: $ANSIBLE_VM_NAME
EOF

echo "Cloud-init configuration prepared." | tee -a "$LOG_FILE"

# Clone template to create VM
echo "Cloning template to create VM..." | tee -a "$LOG_FILE"
clone_data='{
    "newid": '$ANSIBLE_VM_VMID',
    "name": "'$ANSIBLE_VM_NAME'",
    "memory": '$ANSIBLE_VM_RAM_MB',
    "cores": '$ANSIBLE_VM_VCPUS'
}'

result=$(proxmox_api "POST" "/nodes/$PROXMOX_TARGET_NODE/qemu/$DEBIAN_TEMPLATE_ID/clone" "$clone_data" 2>&1)
echo "Clone result: $result" | tee -a "$LOG_FILE"

# Wait for clone to complete
echo "Waiting for clone to complete..." | tee -a "$LOG_FILE"
sleep 10

# Update VM configuration
echo "Updating VM configuration..." | tee -a "$LOG_FILE"
config_data='{
    "scsi0": "'$PROXMOX_STORAGE':'$ANSIBLE_VM_DISK_GB'",
    "net0": "virtio,bridge='$PROXMOX_BRIDGE'",
    "agent": "1",
    "ciuser": "ansible",
    "cipassword": "",
    "sshkeys": "'$SSH_PUBKEY'"
}'

result=$(proxmox_api "PUT" "/nodes/$PROXMOX_TARGET_NODE/qemu/$ANSIBLE_VM_VMID/config" "$config_data" 2>&1)
echo "Config update result: $result" | tee -a "$LOG_FILE"

# Start the VM
echo "Starting VM..." | tee -a "$LOG_FILE"
result=$(proxmox_api "POST" "/nodes/$PROXMOX_TARGET_NODE/qemu/$ANSIBLE_VM_VMID/status/start" '{}' 2>&1)
echo "Start result: $result" | tee -a "$LOG_FILE"

echo "Ansible VM creation complete!" | tee -a "$LOG_FILE"
echo "VM ID: $ANSIBLE_VM_VMID" | tee -a "$LOG_FILE"
echo "VM Name: $ANSIBLE_VM_NAME" | tee -a "$LOG_FILE"
echo "Check $LOG_FILE for full details." | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Next steps:" | tee -a "$LOG_FILE"
echo "1. Wait for VM to boot and cloud-init to complete" | tee -a "$LOG_FILE"
echo "2. SSH to the VM: ssh ansible@<vm-ip>" | tee -a "$LOG_FILE"
echo "3. Run the Ansible setup script on the VM" | tee -a "$LOG_FILE"
