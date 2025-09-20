# 🎬 Dry-Run Narrative: Proxmox + Ansible Automation Bootstrap

This document provides a detailed walkthrough of the complete automation bootstrap process, explaining what happens at each step and how the system works together.

## 🎯 Overview

The automation baseline creates a complete Proxmox + Ansible infrastructure management system that can be committed to a repository and re-run idempotently. Here's what the bootstrap process accomplishes:

### What Gets Created
1. **Infrastructure Discovery System** - Automated inventory of your Proxmox cluster
2. **Template Management** - Debian 12 cloud-init template for consistent VM deployment
3. **Ansible Control Node** - Dedicated VM for running automation
4. **Complete Automation Stack** - Playbooks, configurations, and helper scripts
5. **Security Framework** - Vault encryption, SSH keys, firewall hardening
6. **Monitoring & Logging** - Comprehensive audit trails and system monitoring

## 🚀 Bootstrap Sequence

### Phase 1: Infrastructure Discovery

**Script**: `discover-proxmox.sh`

**What Happens**:
```bash
# API calls made to Proxmox:
GET /version                    # Get Proxmox version
GET /cluster/status            # Get cluster health
GET /nodes                     # List all nodes
GET /storage                   # List storage pools
GET /cluster/network           # Get network configuration
GET /nodes/{node}/qemu         # List VMs per node
GET /nodes/{node}/lxc          # List containers per node
GET /nodes/{node}/storage/local/content  # List ISOs
```

**Output**: Detailed JSON report of your cluster state, saved to `logs/proxmox-discovery-*.log`

**Why This Matters**: You need to understand your current infrastructure before automating it. This creates a baseline inventory.

### Phase 2: Template Setup

**Script**: `setup-debian-template.sh`

**What Happens**:
```bash
# 1. Download Debian 12 cloud image
wget https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-nocloud-amd64.qcow2

# 2. Create VM template (ID: 9000)
POST /nodes/{node}/qemu/{template_id}/clone
{
  "newid": 9000,
  "name": "debian-12-cloud",
  "memory": 2048,
  "cores": 2
}

# 3. Configure template settings
PUT /nodes/{node}/qemu/{template_id}/config
{
  "scsi0": "local-lvm:32",
  "net0": "virtio,bridge=vmbr0",
  "agent": "1",
  "template": 1
}
```

**Output**: A cloud-init ready Debian 12 template that can be cloned to create VMs

**Why This Matters**: Templates provide consistency. Every VM created from this template will have the same base configuration, security hardening, and cloud-init capabilities.

### Phase 3: Ansible Control Node Provisioning

**Script**: `create-ansible-vm.sh`

**What Happens**:
```bash
# 1. Clone template to create VM
POST /nodes/{node}/qemu/{template_id}/clone
{
  "newid": 9001,
  "name": "ansible-control",
  "memory": 4096,
  "cores": 2
}

# 2. Configure VM with cloud-init
PUT /nodes/{node}/qemu/{vm_id}/config
{
  "scsi0": "local-lvm:40",
  "net0": "virtio,bridge=vmbr0",
  "agent": "1",
  "ciuser": "ansible",
  "sshkeys": "ssh-ed25519 AAAA... your-key"
}

# 3. Start the VM
POST /nodes/{node}/qemu/{vm_id}/status/start
```

**Cloud-Init Configuration**:
```yaml
#cloud-config
hostname: ansible-control
users:
  - name: ansible
    ssh_authorized_keys:
      - ssh-ed25519 AAAA... your-key
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
packages:
  - python3
  - git
  - curl
  - jq
  - tmux
runcmd:
  - ufw enable
  - ufw default deny incoming
  - ufw allow ssh
```

**Output**: A running VM with SSH access, ready for Ansible installation

### Phase 4: Ansible Control Node Configuration

**Script**: `setup-ansible-control.sh` (run on the VM)

**What Happens**:
```bash
# 1. Install Ansible via pipx
pipx install ansible

# 2. Install required collections
ansible-galaxy collection install community.proxmox
ansible-galaxy collection install community.general

# 3. Generate SSH keys
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519

# 4. Create vault configuration
ansible-vault encrypt group_vars/all/vault.yml

# 5. Setup systemd services
systemctl enable ansible-env.service
systemctl enable ansible-collections-update.timer
```

**Directory Structure Created**:
```
/home/ansible/infra/
├── ansible/
│   ├── ansible.cfg              # Production Ansible config
│   ├── requirements.yml         # Collection requirements
│   ├── inventories/prod/hosts.yml  # Inventory definitions
│   ├── playbooks/proxmox/       # Automation playbooks
│   └── group_vars/all/vault.yml # Encrypted secrets
├── scripts/                     # Helper scripts
├── logs/                        # Operation logs
└── facts/                       # Infrastructure facts
```

**Output**: A fully configured Ansible control node with all automation capabilities

### Phase 5: Validation & Testing

**Scripts**: `test-connection.sh`, `collect-facts.sh`

**What Happens**:
```bash
# 1. Test connectivity
ansible-playbook playbooks/proxmox/ping.yml
# Tests SSH to VMs and API connectivity to Proxmox

# 2. Collect infrastructure facts
ansible-playbook playbooks/proxmox/facts.yml
# Gathers comprehensive cluster information

# 3. Create test VM
./scripts/create-vm.sh test-vm 9999 1 2048 20
# Creates a small test VM to verify automation
```

**Output**: Verified working automation system with test VM created

## 🔄 How It All Works Together

### The Automation Flow

1. **Discovery** → **Template** → **Control Node** → **Configuration** → **Testing**

2. **Each Phase Builds on the Previous**:
   - Discovery provides the inventory for automation
   - Template provides consistent VM deployment
   - Control Node provides the automation engine
   - Configuration provides the automation capabilities
   - Testing validates everything works

### Key Integration Points

**Proxmox API Integration**:
- All operations use the Proxmox API with token authentication
- API calls are logged for audit purposes
- Error handling ensures operations are safe to retry

**Cloud-Init Integration**:
- VMs are configured via cloud-init for consistent setup
- SSH keys are injected during VM creation
- Security hardening is applied automatically

**Ansible Integration**:
- Playbooks use the Proxmox collection for API operations
- Inventory is dynamically maintained
- Vault encryption protects sensitive data

**Security Integration**:
- SSH keys replace password authentication
- Vault encryption protects secrets
- Firewall rules are applied automatically
- Audit logging tracks all operations

## 🎭 Example Automation Run

Here's what happens when you create a new VM:

```bash
# User runs:
./scripts/create-vm.sh web-server 100 2 4096 40

# Behind the scenes:
# 1. Check if VM 100 already exists
GET /nodes/pve/qemu/100/config

# 2. Clone template to create VM
POST /nodes/pve/qemu/9000/clone
{
  "newid": 100,
  "name": "web-server",
  "memory": 4096,
  "cores": 2
}

# 3. Configure VM settings
PUT /nodes/pve/qemu/100/config
{
  "scsi0": "local-lvm:40",
  "net0": "virtio,bridge=vmbr0",
  "agent": "1",
  "ciuser": "ansible",
  "sshkeys": "ssh-ed25519 AAAA... key"
}

# 4. Start the VM
POST /nodes/pve/qemu/100/status/start

# 5. Cloud-init runs on the VM:
# - Sets hostname to "web-server"
# - Creates "ansible" user with SSH key
# - Installs packages (python3, git, curl, etc.)
# - Configures firewall (ufw)
# - Disables root login
```

**Result**: A fully configured, secure VM ready for application deployment

## 🔒 Security Throughout the Process

### Authentication
- **Proxmox API**: Token-based authentication with least privilege
- **SSH**: Ed25519 key pairs, no password authentication
- **Ansible Vault**: Encrypted storage of all secrets

### Network Security
- **Firewall**: UFW enabled with deny-by-default
- **SSH**: Root login disabled, key-only access
- **Network Isolation**: VMs can be placed on isolated networks

### Data Protection
- **Vault Encryption**: All sensitive data encrypted at rest
- **Audit Logging**: All operations logged for compliance
- **Access Control**: Least privilege principles throughout

## 📊 Monitoring & Observability

### Logging
- **Operation Logs**: Every API call logged with timestamp
- **Ansible Logs**: Playbook execution logs
- **System Logs**: VM and host system logs

### Facts Collection
- **Daily Facts**: Automated collection of infrastructure state
- **Historical Data**: Facts saved with timestamps for trend analysis
- **Change Detection**: Compare facts over time to detect changes

### Health Monitoring
- **Connectivity Tests**: Regular ping tests to all hosts
- **API Health**: Proxmox API connectivity monitoring
- **Resource Monitoring**: CPU, memory, disk usage tracking

## 🎯 Production Readiness

### Idempotency
- **Safe to Re-run**: All operations can be safely repeated
- **State Checking**: Scripts check current state before making changes
- **Error Handling**: Graceful handling of existing resources

### Scalability
- **Multi-Node Support**: Designed for multi-node Proxmox clusters
- **Template Reuse**: Templates can be used across multiple nodes
- **Inventory Management**: Dynamic inventory updates as infrastructure grows

### Maintainability
- **Documentation**: Comprehensive setup and security guides
- **Helper Scripts**: Common operations simplified with scripts
- **Version Control**: All configurations can be version controlled

## 🚀 What You Get

After running this bootstrap process, you have:

1. **Complete Automation Stack** - Ready to manage your Proxmox infrastructure
2. **Security Framework** - Production-ready security with encryption and hardening
3. **Monitoring System** - Comprehensive logging and facts collection
4. **Helper Tools** - Scripts for common operations
5. **Documentation** - Complete setup and security guides
6. **Tested System** - Validated with test VM creation

**You can now**:
- Create VMs with a single command
- Automate infrastructure management
- Monitor your cluster health
- Scale your infrastructure programmatically
- Maintain security and compliance
- Version control your infrastructure as code

This is a complete, production-ready automation baseline that you can commit to a repository and use to manage your Proxmox infrastructure reliably and securely.
