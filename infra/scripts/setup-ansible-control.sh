#!/bin/bash
# Ansible Control Node Setup Script
# Run this script on the Ansible control node VM after creation

set -euo pipefail

# Configuration
ANSIBLE_USER="${ANSIBLE_USER:-ansible}"
ANSIBLE_HOME="/home/$ANSIBLE_USER"
INFRA_DIR="$ANSIBLE_HOME/infra"
ANSIBLE_DIR="$INFRA_DIR/ansible"

LOG_FILE="$INFRA_DIR/logs/ansible-setup-$(date +%Y%m%d-%H%M%S).log"
echo "Starting Ansible control node setup at $(date)" | tee -a "$LOG_FILE"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== ANSIBLE CONTROL NODE SETUP ==="

# Check if running as correct user
if [[ "$(whoami)" != "$ANSIBLE_USER" ]]; then
    log "ERROR: This script must be run as user $ANSIBLE_USER"
    log "Please run: sudo -u $ANSIBLE_USER $0"
    exit 1
fi

# Create directory structure
log "Creating directory structure..."
mkdir -p "$INFRA_DIR"/{ansible/{inventories/prod,playbooks/proxmox,roles,group_vars,host_vars},scripts,logs,facts}
mkdir -p "$ANSIBLE_HOME"/.ansible/{vault-identities,plugins/{action,callback,connection,filter,inventory,lookup,modules,strategy,terminal,test}}
mkdir -p "$ANSIBLE_HOME"/.ssh

# Set proper permissions
chmod 700 "$ANSIBLE_HOME"/.ssh
chmod 755 "$ANSIBLE_HOME"/.ansible

log "Directory structure created successfully"

# Install pipx if not present
if ! command -v pipx &> /dev/null; then
    log "Installing pipx..."
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install Ansible via pipx
log "Installing Ansible via pipx..."
pipx install ansible

# Install additional Python packages
log "Installing additional Python packages..."
pip install --user \
    proxmoxer \
    requests \
    pyyaml \
    jinja2 \
    netaddr \
    paramiko \
    cryptography

# Install Ansible collections
log "Installing Ansible collections..."
cd "$ANSIBLE_DIR"
ansible-galaxy collection install -r requirements.yml --force

# Create SSH key if it doesn't exist
if [[ ! -f "$ANSIBLE_HOME/.ssh/id_ed25519" ]]; then
    log "Generating SSH key pair..."
    ssh-keygen -t ed25519 -f "$ANSIBLE_HOME/.ssh/id_ed25519" -N "" -C "ansible-control-$(hostname)"
    chmod 600 "$ANSIBLE_HOME/.ssh/id_ed25519"
    chmod 644 "$ANSIBLE_HOME/.ssh/id_ed25519.pub"
fi

# Create SSH config
log "Creating SSH configuration..."
cat > "$ANSIBLE_HOME/.ssh/config" << 'EOF'
Host *
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    ControlMaster auto
    ControlPath /tmp/ansible-ssh-%h-%p-%r
    ControlPersist 60s
    ServerAliveInterval 60
    ServerAliveCountMax 3
EOF

chmod 600 "$ANSIBLE_HOME/.ssh/config"

# Create vault password file
log "Creating Ansible vault configuration..."
VAULT_PASSWORD=$(openssl rand -base64 32)
echo "$VAULT_PASSWORD" > "$ANSIBLE_HOME/.ansible/vault_pass"
chmod 600 "$ANSIBLE_HOME/.ansible/vault_pass"

# Create example vault variables
log "Creating example vault variables..."
cat > "$ANSIBLE_DIR/group_vars/all/vault.yml" << 'EOF'
# Vault Variables - Encrypt this file with: ansible-vault encrypt group_vars/all/vault.yml

vault_proxmox_api_url: "https://172.23.5.15:8006/api2/json"
vault_proxmox_username: "root@pam"
vault_proxmox_token_name: "mcp-token"
vault_proxmox_token_value: "REPLACE_WITH_YOUR_ACTUAL_TOKEN_VALUE"

vault_ssh_public_key: "ssh-ed25519 AAAA... ansible-control"
vault_ssh_private_key: "-----BEGIN OPENSSH PRIVATE KEY-----..."

# Additional secrets
vault_grafana_admin_password: "changeme"
vault_monitoring_api_key: "changeme"
EOF

# Encrypt the vault file
log "Encrypting vault variables..."
ansible-vault encrypt "$ANSIBLE_DIR/group_vars/all/vault.yml" --vault-password-file "$ANSIBLE_HOME/.ansible/vault_pass"

# Create environment file
log "Creating environment configuration..."
cat > "$INFRA_DIR/.env.example" << 'EOF'
# Proxmox Configuration
PROXMOX_API_URL=https://172.23.5.15:8006/api2/json
PROXMOX_USERNAME=root@pam
PROXMOX_TOKEN_NAME=mcp-token
PROXMOX_TOKEN_VALUE=REPLACE_WITH_YOUR_ACTUAL_TOKEN_VALUE
PROXMOX_TARGET_NODE=pve
PROXMOX_STORAGE=local-lvm
PROXMOX_ISO_STORAGE=local
PROXMOX_BRIDGE=vmbr0

# SSH Configuration
SSH_PUBKEY=ssh-ed25519 AAAA... ansible-control

# Ansible VM Configuration
ANSIBLE_VM_NAME=ansible-control
ANSIBLE_VM_VMID=9001
ANSIBLE_VM_VCPUS=2
ANSIBLE_VM_RAM_MB=4096
ANSIBLE_VM_DISK_GB=40
ANSIBLE_VM_NET=dhcp
ANSIBLE_VM_STATIC_IP=
ANSIBLE_VM_GW=

# DNS Configuration
DNS_SERVERS=1.1.1.1 9.9.9.9
EOF

# Create systemd service for environment loading
log "Creating systemd service for environment loading..."
sudo tee /etc/systemd/system/ansible-env.service > /dev/null << EOF
[Unit]
Description=Ansible Environment Loader
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/bash -c 'source $INFRA_DIR/.env && echo "Environment loaded"'
User=$ANSIBLE_USER
Group=$ANSIBLE_USER

[Install]
WantedBy=multi-user.target
EOF

# Create daily collection update timer
log "Creating daily collection update timer..."
sudo tee /etc/systemd/system/ansible-collections-update.service > /dev/null << EOF
[Unit]
Description=Update Ansible Collections
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/ansible-galaxy collection install -r $ANSIBLE_DIR/requirements.yml --force
User=$ANSIBLE_USER
Group=$ANSIBLE_USER
WorkingDirectory=$ANSIBLE_DIR
EOF

sudo tee /etc/systemd/system/ansible-collections-update.timer > /dev/null << EOF
[Unit]
Description=Run Ansible Collections Update Daily
Requires=ansible-collections-update.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Enable and start services
log "Enabling systemd services..."
sudo systemctl daemon-reload
sudo systemctl enable ansible-env.service
sudo systemctl enable ansible-collections-update.timer
sudo systemctl start ansible-env.service
sudo systemctl start ansible-collections-update.timer

# Create tmuxp configuration
log "Creating tmuxp configuration..."
cat > "$ANSIBLE_HOME/.tmuxp/ansible-session.yaml" << 'EOF'
session_name: ansible-automation
windows:
  - window_name: ansible
    panes:
      - shell_command: cd ~/infra/ansible
      - shell_command: ansible --version
  - window_name: logs
    panes:
      - shell_command: tail -f ~/infra/logs/ansible.log
  - window_name: playbooks
    panes:
      - shell_command: cd ~/infra/ansible/playbooks/proxmox
EOF

# Create helper scripts
log "Creating helper scripts..."

# Quick test script
cat > "$INFRA_DIR/scripts/test-connection.sh" << 'EOF'
#!/bin/bash
# Test Proxmox and VM connectivity

cd ~/infra/ansible
ansible-playbook playbooks/proxmox/ping.yml -i inventories/prod/hosts.yml
EOF

# Facts collection script
cat > "$INFRA_DIR/scripts/collect-facts.sh" << 'EOF'
#!/bin/bash
# Collect Proxmox infrastructure facts

cd ~/infra/ansible
ansible-playbook playbooks/proxmox/facts.yml -i inventories/prod/hosts.yml
EOF

# VM creation script
cat > "$INFRA_DIR/scripts/create-vm.sh" << 'EOF'
#!/bin/bash
# Create a new VM using Ansible

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <vm-name> <vm-id> [cores] [memory] [disk]"
    echo "Example: $0 web-server 100 2 4096 40"
    exit 1
fi

VM_NAME="$1"
VM_ID="$2"
VM_CORES="${3:-2}"
VM_MEMORY="${4:-4096}"
VM_DISK="${5:-40}"

cd ~/infra/ansible
ansible-playbook playbooks/proxmox/vm_create.yml \
    -i inventories/prod/hosts.yml \
    -e "vm_name=$VM_NAME" \
    -e "vm_id=$VM_ID" \
    -e "vm_cores=$VM_CORES" \
    -e "vm_memory=$VM_MEMORY" \
    -e "vm_disk_size=$VM_DISK"
EOF

# Make scripts executable
chmod +x "$INFRA_DIR/scripts"/*.sh

# Create README
log "Creating README documentation..."
cat > "$INFRA_DIR/README.md" << 'EOF'
# Proxmox + Ansible Automation Baseline

This directory contains the complete automation setup for managing Proxmox infrastructure with Ansible.

## Directory Structure

```
infra/
├── ansible/                    # Ansible configuration and playbooks
│   ├── ansible.cfg            # Ansible configuration
│   ├── requirements.yml       # Collection requirements
│   ├── inventories/prod/      # Production inventory
│   ├── playbooks/proxmox/     # Proxmox-specific playbooks
│   ├── roles/                 # Custom roles
│   └── group_vars/            # Group variables (including vault)
├── scripts/                   # Helper scripts
├── logs/                      # Log files
├── facts/                     # Infrastructure facts
└── README.md                  # This file
```

## Quick Start

1. **Configure vault variables:**
   ```bash
   ansible-vault edit group_vars/all/vault.yml
   ```

2. **Test connectivity:**
   ```bash
   ./scripts/test-connection.sh
   ```

3. **Collect infrastructure facts:**
   ```bash
   ./scripts/collect-facts.sh
   ```

4. **Create a new VM:**
   ```bash
   ./scripts/create-vm.sh web-server 100 2 4096 40
   ```

## Available Playbooks

- `ping.yml` - Test connectivity to Proxmox hosts and VMs
- `facts.yml` - Collect comprehensive infrastructure facts
- `vm_create.yml` - Create new VMs with cloud-init
- `vm_delete.yml` - Safely remove VMs
- `snapshot.yml` - Manage VM snapshots
- `backup.yml` - Backup VMs

## Security

- All sensitive data is stored in encrypted vault files
- SSH keys are generated and configured automatically
- UFW firewall rules are applied by default
- Root login is disabled on all VMs

## Monitoring

- Daily collection updates via systemd timer
- Comprehensive logging to `logs/` directory
- Infrastructure facts saved to `facts/` directory

## Using with ProxMenux

This automation stack is designed to work alongside ProxMenux. After using ProxMenux to create templates or VMs, run the facts collection playbook to reconcile the inventory:

```bash
./scripts/collect-facts.sh
```

This will update the Ansible inventory with any changes made via ProxMenux.
EOF

log "Ansible control node setup complete!"
log "Check $LOG_FILE for full details"
log ""
log "Next steps:"
log "1. Configure vault variables: ansible-vault edit group_vars/all/vault.yml"
log "2. Test connectivity: ./scripts/test-connection.sh"
log "3. Collect facts: ./scripts/collect-facts.sh"
log "4. Start automating: ./scripts/create-vm.sh <name> <id>"
