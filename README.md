# TK-Proxmox Infrastructure Automation

A comprehensive infrastructure automation solution combining Proxmox virtualization management, Ansible automation, and Semaphore orchestration for network device management.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Proxmox MCP   │───▶│  Ansible        │───▶│  Network        │
│   Server        │    │  Semaphore      │    │  Devices        │
│                 │    │                 │    │                 │
│ • VM Management │    │ • Playbook      │    │ • Arista EOS    │
│ • Cluster Ops   │    │   Execution     │    │ • Cisco Nexus   │
│ • Resource      │    │ • Secret        │    │ • Cisco Catalyst│
│   Monitoring    │    │   Management    │    │ • OPNsense FW   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Proxmox VE cluster
- Ubuntu/Debian control node VM
- Network devices (Arista, Cisco, OPNsense)
- SSH access to all devices

### 1. Setup Proxmox MCP Server
```bash
cd agentify-proxmox-mcp
python -m venv venv
source venv/bin/activate
pip install -r requirements.in
```

### 2. Deploy Ansible Semaphore
```bash
cd infra
./scripts/semaphore_bootstrap.sh
```

### 3. Configure Network Automation
```bash
# Create secrets in Semaphore web interface
# Navigate to: http://[control-node-ip]:3000

# Run network operations
./scripts/run_network_template.sh health_check
./scripts/run_network_template.sh backup -c
```

## 📁 Project Structure

```
tk-proxmox/
├── agentify-proxmox-mcp/          # Proxmox MCP Server
│   ├── src/proxmox_mcp/          # MCP server implementation
│   ├── proxmox-config/           # Configuration files
│   └── test_scripts/             # Testing utilities
├── infra/                        # Infrastructure automation
│   ├── ansible/                  # Ansible configuration
│   │   ├── inventories/          # Device inventories
│   │   ├── playbooks/            # Automation playbooks
│   │   │   ├── network/          # Network device playbooks
│   │   │   ├── semaphore/        # Semaphore deployment
│   │   │   └── templates/        # Reusable templates
│   │   └── roles/                # Ansible roles
│   ├── scripts/                  # Automation scripts
│   └── docs/                     # Documentation
└── README.md                     # This file
```

## 🔧 Components

### Proxmox MCP Server
- **Purpose**: Model Context Protocol server for Proxmox VE
- **Features**: VM management, cluster operations, resource monitoring
- **Location**: `agentify-proxmox-mcp/`

### Ansible Semaphore
- **Purpose**: Web-based Ansible automation platform
- **Features**: Playbook execution, secret management, user interface
- **Access**: http://[control-node-ip]:3000

### Network Operations Template
- **Purpose**: Multi-purpose network device management
- **Operations**: Health checks, backups, VLAN assignment, port management
- **Security**: Encrypted secrets, audit trails, safety validations

## 🎯 Key Features

### 🔐 Security
- **Encrypted Secrets**: All credentials stored as Semaphore secrets
- **Unified Authentication**: Single credential set across all devices
- **Audit Trails**: Complete logging of all operations
- **Protected Infrastructure**: Safety checks prevent critical port modifications

### 🚀 Automation
- **Multi-Vendor Support**: Arista EOS, Cisco Nexus/Catalyst, OPNsense
- **Template-Based**: Reusable templates for common operations
- **Safety First**: Protected ports, VLAN validation, change verification
- **Comprehensive Reporting**: Detailed operation logs and status reports

### 📊 Operations
- **Health Monitoring**: Device connectivity and status checks
- **Configuration Backup**: Automated backup of network device configs
- **VLAN Management**: Safe port assignment with validation
- **Port Control**: Enable/disable ports with safety checks

## 📋 Usage Examples

### Network Health Check
```bash
./infra/scripts/run_network_template.sh health_check
```

### VLAN Port Assignment
```bash
./infra/scripts/run_network_template.sh vlan_assign \
  -d catalyst-access-01 \
  -p GigabitEthernet1/0/10 \
  -V 20 \
  -D "John Smith Workstation"
```

### Configuration Backup
```bash
./infra/scripts/run_network_template.sh backup -c
```

### Port Management
```bash
# Enable port
./infra/scripts/run_network_template.sh port_enable \
  -d catalyst-access-01 \
  -p GigabitEthernet1/0/20

# Disable port
./infra/scripts/run_network_template.sh port_disable \
  -d catalyst-access-01 \
  -p GigabitEthernet1/0/25
```

## 🔧 Configuration

### Proxmox MCP
Edit `agentify-proxmox-mcp/proxmox-config/config.json`:
```json
{
  "proxmox": {
    "host": "your-proxmox-host",
    "port": 8006,
    "verify_ssl": false
  },
  "auth": {
    "user": "your-user@pam",
    "token_name": "your-token",
    "token_value": "your-token-value"
  }
}
```

### Ansible Inventory
Edit `infra/ansible/inventories/prod/hosts.yml`:
```yaml
core_network:
  hosts:
    arista-core-01:
      ansible_host: 172.23.5.1
      device_type: arista_eos
    nexus-agg-01:
      ansible_host: 172.23.5.2
      device_type: cisco_nxos
```

### Semaphore Secrets
Create these secrets in Semaphore web interface:
- `Network Device Admin Credentials`
- `Network Enable Password`
- `OPNsense Admin Credentials`
- `Network Backup Credentials`

## 📚 Documentation

- [Ansible Template Guide](infra/ANSIBLE_TEMPLATE_GUIDE.md)
- [Network Backup Runbook](infra/NETWORK_BACKUP_RUNBOOK.md)
- [VLAN Assignment Runbook](infra/VLAN_PORT_ASSIGNMENT_RUNBOOK.md)
- [Security Migration Guide](infra/SECURITY_MIGRATION_GUIDE.md)
- [Semaphore Setup](infra/SETUP_SEMAPHORE.md)

## 🛠️ Development

### Testing
```bash
# Test Proxmox MCP server
cd agentify-proxmox-mcp
python -m proxmox_mcp.server

# Test Ansible playbooks
cd infra/ansible
ansible-playbook -i inventories/prod/hosts.yml playbooks/network/verify_credentials.yml --check
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

For support and questions:
- Check the documentation in the `infra/` directory
- Review the runbooks for specific operations
- Ensure all prerequisites are met
- Verify network connectivity and credentials

## 🎉 Getting Started Checklist

- [ ] Proxmox VE cluster running
- [ ] Control node VM deployed
- [ ] SSH access to network devices
- [ ] Proxmox MCP server configured
- [ ] Ansible Semaphore deployed
- [ ] Network inventory configured
- [ ] Secrets created in Semaphore
- [ ] Test operations completed

---

**Ready to automate your network infrastructure!** 🚀
