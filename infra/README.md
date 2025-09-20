# 🚀 Proxmox + Ansible Automation Baseline

A complete automation baseline for managing Proxmox VE infrastructure using Ansible, designed for production use with security best practices.

## 🎯 What This Provides

- **Complete VM Lifecycle Management** - Create, configure, and manage VMs with cloud-init
- **Infrastructure Discovery** - Automated inventory of Proxmox clusters
- **Security-First Design** - Vault encryption, SSH keys, firewall hardening
- **Production Ready** - Idempotent operations, comprehensive logging, error handling
- **ProxMenux Compatible** - Works alongside existing ProxMenux installations

## 🚀 Quick Start

### 1. Configure Environment
```bash
# Set your Proxmox credentials
export PROXMOX_API_URL="https://172.23.5.15:8006/api2/json"
export PROXMOX_USERNAME="root@pam"
export PROXMOX_TOKEN_NAME="mcp-token"
export PROXMOX_TOKEN_VALUE="your-actual-token-value"
export SSH_PUBKEY="ssh-ed25519 AAAA... your-public-key"
```

### 2. Discover Infrastructure
```bash
./scripts/discover-proxmox.sh
```

### 3. Setup Template
```bash
./scripts/setup-debian-template.sh
```

### 4. Create Ansible Control Node
```bash
./scripts/create-ansible-vm.sh
```

### 5. Configure Ansible
```bash
# SSH to the control node
ssh ansible@<vm-ip>

# Run setup
cd infra
./scripts/setup-ansible-control.sh
```

### 6. Test Everything
```bash
# Test connectivity
./scripts/test-connection.sh

# Collect facts
./scripts/collect-facts.sh

# Create a test VM
./scripts/create-vm.sh test-vm 9999 1 2048 20
```

## 📁 Directory Structure

```
infra/
├── ansible/                    # Ansible configuration and playbooks
│   ├── ansible.cfg            # Ansible configuration
│   ├── requirements.yml       # Collection requirements
│   ├── inventories/prod/      # Production inventory
│   │   └── hosts.yml         # Host definitions
│   ├── playbooks/proxmox/     # Proxmox-specific playbooks
│   │   ├── ping.yml          # Connectivity testing
│   │   ├── facts.yml         # Infrastructure facts
│   │   └── vm_create.yml     # VM creation
│   ├── roles/                # Custom roles (empty)
│   └── group_vars/all/       # Group variables
│       └── vault.yml         # Encrypted secrets
├── scripts/                   # Helper scripts
│   ├── discover-proxmox.sh   # Infrastructure discovery
│   ├── setup-debian-template.sh # Template setup
│   ├── create-ansible-vm.sh  # VM creation
│   ├── setup-ansible-control.sh # Ansible setup
│   ├── test-connection.sh    # Connectivity testing
│   ├── collect-facts.sh      # Facts collection
│   ├── create-vm.sh         # VM creation helper
│   └── proxmox-actions.log   # Action log
├── logs/                     # Log files (created during execution)
├── facts/                    # Infrastructure facts (created during execution)
├── SETUP.md                  # Detailed setup guide
├── SECURITY.md               # Security guidelines
└── README.md                 # This file
```

## 🛠️ Available Scripts

### Infrastructure Management
- **`discover-proxmox.sh`** - Inventory your Proxmox cluster
- **`setup-debian-template.sh`** - Create Debian 12 cloud template
- **`create-ansible-vm.sh`** - Provision Ansible control node

### Ansible Operations
- **`test-connection.sh`** - Test connectivity to all hosts
- **`collect-facts.sh`** - Gather infrastructure information
- **`create-vm.sh <name> <id> [cores] [memory] [disk]`** - Quick VM creation

## 🎭 Available Playbooks

### Core Operations
- **`ping.yml`** - Test SSH and API connectivity
- **`facts.yml`** - Collect comprehensive infrastructure facts
- **`vm_create.yml`** - Create VMs with cloud-init configuration

### Usage Examples
```bash
# Test everything
ansible-playbook playbooks/proxmox/ping.yml -i inventories/prod/hosts.yml

# Collect infrastructure facts
ansible-playbook playbooks/proxmox/facts.yml -i inventories/prod/hosts.yml

# Create a VM
ansible-playbook playbooks/proxmox/vm_create.yml \
    -i inventories/prod/hosts.yml \
    -e "vm_name=web-server" \
    -e "vm_id=100" \
    -e "vm_cores=2" \
    -e "vm_memory=4096" \
    -e "vm_disk_size=40"
```

## 🔒 Security Features

- **Vault Encryption** - All secrets stored encrypted
- **SSH Key Authentication** - No passwords, Ed25519 keys
- **Firewall Hardening** - UFW with secure defaults
- **Audit Logging** - Comprehensive operation logs
- **Access Control** - Least privilege principles

## 🔄 ProxMenux Integration

This automation works alongside ProxMenux:

1. **Discovery After Changes** - Run facts collection after ProxMenux operations
2. **Shared Resources** - Coordinate template and storage usage
3. **Inventory Reconciliation** - Keep Ansible inventory updated

```bash
# After using ProxMenux, reconcile inventory
./scripts/collect-facts.sh
```

## 📊 Monitoring & Logging

### Log Files
- `logs/ansible.log` - Ansible operations
- `logs/proxmox-*.log` - Proxmox API calls
- `logs/discovery-*.log` - Infrastructure discovery

### Systemd Services
- **`ansible-env.service`** - Environment loading
- **`ansible-collections-update.timer`** - Daily collection updates

### Facts Collection
- `facts/proxmox-facts-YYYY-MM-DD.md` - Daily infrastructure reports

## 🚨 Troubleshooting

### Common Issues

**MCP Tools Not Available:**
```bash
# Restart Cursor completely
# Check ~/.cursor/mcp.json configuration
# Verify Proxmox credentials
```

**VM Creation Fails:**
```bash
# Check template exists (ID: 9000)
# Verify storage space
# Check network bridge
```

**Ansible Connection Issues:**
```bash
# Test SSH connectivity
ssh -o StrictHostKeyChecking=no ansible@<vm-ip>

# Check cloud-init completion
cloud-init status
```

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Detailed setup instructions
- **[SECURITY.md](SECURITY.md)** - Security guidelines and best practices
- **[proxmox-actions.log](scripts/proxmox-actions.log)** - Action log

## 🎯 Next Steps

After setup completion:

1. **Customize Inventory** - Add your specific hosts and VMs
2. **Create Custom Roles** - Develop reusable automation
3. **Set Up Monitoring** - Integrate with Grafana/Prometheus
4. **Implement Backups** - Configure automated backups
5. **Scale Horizontally** - Add more Proxmox nodes

## 🤝 Contributing

This automation baseline is designed to be:
- **Idempotent** - Safe to run multiple times
- **Modular** - Easy to extend and customize
- **Documented** - Clear instructions and examples
- **Secure** - Security-first design principles

## 📄 License

This automation baseline is provided as-is for educational and production use. Please review and customize according to your security requirements.

---

**Ready to automate your Proxmox infrastructure?** Start with the [SETUP.md](SETUP.md) guide for detailed instructions!
