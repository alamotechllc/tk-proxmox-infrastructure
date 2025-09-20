# 🚀 Proxmox + Ansible Automation Setup Guide

This guide provides step-by-step instructions for setting up a complete Proxmox + Ansible automation baseline.

## 📋 Prerequisites

- Proxmox VE cluster with API access
- Proxmox API token with appropriate permissions
- SSH key pair for authentication
- Network access to Proxmox hosts

## 🔧 Configuration Variables

Before starting, configure these environment variables:

```bash
# Proxmox Configuration
export PROXMOX_API_URL="https://172.23.5.15:8006/api2/json"
export PROXMOX_USERNAME="root@pam"
export PROXMOX_TOKEN_NAME="mcp-token"
export PROXMOX_TOKEN_VALUE="your-actual-token-value"

# Target Infrastructure
export PROXMOX_TARGET_NODE="pve"
export PROXMOX_STORAGE="local-lvm"
export PROXMOX_ISO_STORAGE="local"
export PROXMOX_BRIDGE="vmbr0"

# SSH Configuration
export SSH_PUBKEY="ssh-ed25519 AAAA... your-public-key"

# Ansible VM Configuration
export ANSIBLE_VM_NAME="ansible-control"
export ANSIBLE_VM_VMID="9001"
export ANSIBLE_VM_VCPUS="2"
export ANSIBLE_VM_RAM_MB="4096"
export ANSIBLE_VM_DISK_GB="40"
export ANSIBLE_VM_NET="dhcp"  # or "static"
export ANSIBLE_VM_STATIC_IP=""  # if using static networking
export ANSIBLE_VM_GW=""  # if using static networking

# DNS Configuration
export DNS_SERVERS="1.1.1.1 9.9.9.9"
```

## 🎯 Step-by-Step Setup

### 1. Discovery Phase

First, discover your current Proxmox infrastructure:

```bash
# Run discovery script
./scripts/discover-proxmox.sh
```

This will create a detailed report of your cluster status, nodes, storage, and existing templates.

### 2. Template Setup

Ensure you have a Debian 12 cloud-init template:

```bash
# Setup Debian 12 cloud template
./scripts/setup-debian-template.sh
```

This script will:
- Download the official Debian 12 cloud image
- Import it as a Proxmox template (ID: 9000)
- Configure cloud-init settings

### 3. Ansible Control Node Provisioning

Create the Ansible control node VM:

```bash
# Create Ansible control node
./scripts/create-ansible-vm.sh
```

This will:
- Clone the Debian template
- Configure cloud-init with SSH keys
- Set up networking (DHCP or static)
- Install required packages
- Create directory structure

### 4. Ansible Setup on Control Node

SSH to the newly created VM and run the setup script:

```bash
# SSH to the Ansible control node
ssh ansible@<vm-ip>

# Run the setup script
cd infra
./scripts/setup-ansible-control.sh
```

This will:
- Install Ansible via pipx
- Install required collections
- Configure SSH keys
- Set up vault encryption
- Create helper scripts
- Configure systemd services

### 5. Configuration

Configure your vault variables:

```bash
# Edit vault variables
ansible-vault edit group_vars/all/vault.yml
```

Add your actual Proxmox credentials and other sensitive data.

### 6. Validation

Test the complete setup:

```bash
# Test connectivity
./scripts/test-connection.sh

# Collect infrastructure facts
./scripts/collect-facts.sh

# Create a test VM
./scripts/create-vm.sh test-vm 9999 1 2048 20
```

## 📁 Generated File Structure

```
infra/
├── ansible/
│   ├── ansible.cfg              # Ansible configuration
│   ├── requirements.yml         # Collection requirements
│   ├── inventories/prod/
│   │   └── hosts.yml           # Production inventory
│   ├── playbooks/proxmox/
│   │   ├── ping.yml            # Connectivity testing
│   │   ├── facts.yml           # Facts collection
│   │   └── vm_create.yml       # VM creation
│   ├── roles/                  # Custom roles (empty)
│   └── group_vars/all/
│       └── vault.yml           # Encrypted variables
├── scripts/
│   ├── discover-proxmox.sh     # Infrastructure discovery
│   ├── setup-debian-template.sh # Template setup
│   ├── create-ansible-vm.sh    # VM creation
│   ├── setup-ansible-control.sh # Ansible setup
│   ├── test-connection.sh      # Connectivity testing
│   ├── collect-facts.sh        # Facts collection
│   └── create-vm.sh            # VM creation helper
├── logs/                       # Log files
├── facts/                      # Infrastructure facts
├── SETUP.md                    # This file
├── SECURITY.md                 # Security guidelines
└── README.md                   # Quick reference
```

## 🔒 Security Considerations

### Vault Encryption

All sensitive data is stored in encrypted vault files:

```bash
# Encrypt vault file
ansible-vault encrypt group_vars/all/vault.yml

# Edit encrypted vault
ansible-vault edit group_vars/all/vault.yml

# View encrypted vault
ansible-vault view group_vars/all/vault.yml
```

### SSH Key Management

SSH keys are automatically generated and configured:
- Private key: `~/.ssh/id_ed25519` (600 permissions)
- Public key: `~/.ssh/id_ed25519.pub` (644 permissions)
- Config: `~/.ssh/config` (600 permissions)

### Network Security

Default security hardening:
- UFW firewall enabled
- SSH access only (port 22)
- Root login disabled
- Password authentication disabled

## 🔄 Using with ProxMenux

This automation stack is designed to work alongside ProxMenux:

1. **After ProxMenux changes**: Run facts collection to reconcile inventory
2. **Before automation**: Ensure ProxMenux hasn't modified critical resources
3. **Shared resources**: Coordinate template and storage usage

```bash
# Reconcile inventory after ProxMenux usage
./scripts/collect-facts.sh
```

## 🛠️ Available Playbooks

### Core Playbooks

- **`ping.yml`** - Test connectivity to all hosts
- **`facts.yml`** - Collect comprehensive infrastructure facts
- **`vm_create.yml`** - Create new VMs with cloud-init
- **`vm_delete.yml`** - Safely remove VMs
- **`snapshot.yml`** - Manage VM snapshots
- **`backup.yml`** - Backup VMs and configurations

### Usage Examples

```bash
# Test connectivity
ansible-playbook playbooks/proxmox/ping.yml -i inventories/prod/hosts.yml

# Collect facts
ansible-playbook playbooks/proxmox/facts.yml -i inventories/prod/hosts.yml

# Create VM
ansible-playbook playbooks/proxmox/vm_create.yml \
    -i inventories/prod/hosts.yml \
    -e "vm_name=web-server" \
    -e "vm_id=100" \
    -e "vm_cores=2" \
    -e "vm_memory=4096" \
    -e "vm_disk_size=40"

# Create VM with static IP
ansible-playbook playbooks/proxmox/vm_create.yml \
    -i inventories/prod/hosts.yml \
    -e "vm_name=db-server" \
    -e "vm_id=101" \
    -e "vm_ip=192.168.1.10/24" \
    -e "vm_gateway=192.168.1.1"
```

## 🔧 Helper Scripts

### Quick Operations

```bash
# Test everything
./scripts/test-connection.sh

# Update infrastructure inventory
./scripts/collect-facts.sh

# Create a new VM quickly
./scripts/create-vm.sh web-server 100 2 4096 40
```

### Advanced Operations

```bash
# Discover infrastructure
./scripts/discover-proxmox.sh

# Setup new template
./scripts/setup-debian-template.sh

# Recreate control node
./scripts/create-ansible-vm.sh --force
```

## 📊 Monitoring and Maintenance

### Systemd Services

- **`ansible-env.service`** - Loads environment variables
- **`ansible-collections-update.timer`** - Daily collection updates

### Logging

All operations are logged to:
- `logs/ansible.log` - Ansible operations
- `logs/proxmox-*.log` - Proxmox API calls
- `logs/discovery-*.log` - Infrastructure discovery

### Facts Collection

Infrastructure facts are saved to:
- `facts/proxmox-facts-YYYY-MM-DD.md` - Daily facts reports
- `facts/` directory - Historical data

## 🚨 Troubleshooting

### Common Issues

1. **MCP Tools Not Available**
   - Restart Cursor completely
   - Check MCP configuration in `~/.cursor/mcp.json`
   - Verify Proxmox credentials

2. **VM Creation Fails**
   - Check template exists (ID: 9000)
   - Verify storage space available
   - Check network bridge configuration

3. **Ansible Connection Issues**
   - Verify SSH keys are correct
   - Check network connectivity
   - Ensure cloud-init completed

### Debug Commands

```bash
# Check Ansible version
ansible --version

# Test SSH connectivity
ssh -o StrictHostKeyChecking=no ansible@<vm-ip>

# Check Proxmox API
curl -k -H "Authorization: PVEAPIToken=user:token=secret" \
    https://proxmox:8006/api2/json/version

# View logs
tail -f logs/ansible.log
tail -f logs/proxmox-*.log
```

## 🎯 Next Steps

After completing this setup:

1. **Customize inventory** - Add your specific hosts and VMs
2. **Create custom roles** - Develop reusable automation
3. **Set up monitoring** - Integrate with Grafana/Prometheus
4. **Implement backups** - Configure automated backups
5. **Scale horizontally** - Add more Proxmox nodes

## 📚 Additional Resources

- [Proxmox VE Documentation](https://pve.proxmox.com/wiki/Main_Page)
- [Ansible Documentation](https://docs.ansible.com/)
- [Proxmox Ansible Collection](https://docs.ansible.com/ansible/latest/collections/community/proxmox/)
- [Cloud-Init Documentation](https://cloudinit.readthedocs.io/)

---

**Note**: This setup creates a production-ready automation baseline. All operations are idempotent and can be safely re-run. The system is designed to work alongside existing ProxMenux installations without conflicts.
