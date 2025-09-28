# Ansible Semaphore Deployment Guide

This guide walks you through deploying Ansible Semaphore on a Proxmox VM using Docker Compose with persistent data and auto-restart capabilities.

## 🎯 MVP Goals

- ✅ Semaphore runs on a dedicated VM in Proxmox cluster
- ✅ Uses Docker Compose with PostgreSQL database
- ✅ All data stored under `/opt/semaphore/` for persistence
- ✅ Managed by systemd for automatic startup after reboots
- ✅ Admin account seeded at first run
- ✅ One-command deployment with `semaphore_bootstrap.sh`

## 📋 Prerequisites

1. **Proxmox Cluster**: Running and accessible
2. **Ansible Control VM**: Ubuntu 22.04 LTS VM in Proxmox
3. **SSH Access**: Key-based authentication configured
4. **Local Ansible**: Installed on your workstation

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Your Local    │    │   Proxmox VM    │    │   Containers    │
│   Workstation   │───▶│ ansible-control │───▶│   Semaphore     │
│                 │    │  Ubuntu 22.04   │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Step 1: Create the VM

First, create a VM in your Proxmox cluster:

```bash
# Use Proxmox web interface or CLI to create VM with:
- VM ID: 200
- Name: ansible-control
- OS: Ubuntu 22.04 LTS
- CPUs: 2
- Memory: 4GB
- Disk: 20GB
- Network: Bridge to your LAN
```

### Step 2: Configure VM

1. **Install Ubuntu 22.04 LTS** on the VM
2. **Create user account**:
   ```bash
   sudo adduser ubuntu
   sudo usermod -aG sudo ubuntu
   ```
3. **Install SSH server**:
   ```bash
   sudo apt update
   sudo apt install openssh-server
   sudo systemctl enable ssh
   ```
4. **Copy your SSH key**:
   ```bash
   ssh-copy-id ubuntu@<VM_IP>
   ```

### Step 3: Update Configuration

Edit the inventory file with your VM's IP address:

```bash
# Edit infra/ansible/inventories/prod/hosts.yml
# Update the ansible_host value for ansible-control
ansible_host: "192.168.1.100"  # Replace with your VM's IP
```

### Step 4: Set Passwords

Set secure passwords for admin and database:

```bash
# Option 1: Edit inventory file directly
vim infra/ansible/inventories/prod/hosts.yml

# Option 2: Use environment variables
export SEMAPHORE_ADMIN_PASSWORD="YourSecurePassword123!"
export POSTGRES_PASSWORD="YourSecureDBPassword456!"
```

### Step 5: Deploy Semaphore

Run the bootstrap script:

```bash
cd /path/to/tk-proxmox
./infra/scripts/semaphore_bootstrap.sh
```

## 📁 Project Structure

```
infra/
├── ansible/
│   ├── inventories/prod/hosts.yml          # VM inventory & config
│   ├── playbooks/semaphore/
│   │   ├── install.yml                     # Main deployment playbook
│   │   └── create-vm.yml                   # VM creation helper
│   └── roles/semaphore/
│       ├── tasks/main.yml                  # Installation tasks
│       ├── handlers/main.yml               # Service handlers
│       └── templates/
│           ├── docker-compose.yml.j2       # Docker Compose template
│           └── semaphore-compose.service.j2 # Systemd service template
├── scripts/
│   └── semaphore_bootstrap.sh              # One-command deployment
└── SETUP_SEMAPHORE.md                      # This file
```

## 🔧 Configuration Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `semaphore_hostname` | `semaphore.local` | Hostname for Semaphore |
| `semaphore_admin_user` | `admin` | Admin username |
| `semaphore_admin_email` | `admin@example.com` | Admin email |
| `semaphore_admin_password` | `ChangeMePlease123!` | Admin password |
| `postgres_db` | `semaphore` | Database name |
| `postgres_user` | `semaphore` | Database user |
| `postgres_password` | `ChangeMePlease456!` | Database password |
| `semaphore_version` | `latest` | Semaphore Docker image tag |
| `postgres_version` | `16` | PostgreSQL version |

## 🐳 Docker Compose Services

### PostgreSQL Database
- **Image**: `postgres:16`
- **Data**: `/opt/semaphore/db` → `/var/lib/postgresql/data`
- **Port**: Internal only (5432)
- **Health Check**: Built-in pg_isready

### Semaphore Application
- **Image**: `semaphoreui/semaphore:latest`
- **Port**: `3000:3000`
- **Data**: `/opt/semaphore/config` → `/etc/semaphore`
- **Depends**: PostgreSQL health check
- **Health Check**: HTTP ping endpoint

## 🔄 Systemd Service

The `semaphore-compose.service` provides:

- **Auto-start**: Starts with system boot
- **Dependency**: Waits for Docker service
- **Restart**: Automatic restart on failure
- **Security**: Runs as non-root user with limited privileges
- **Logging**: Full journald integration

### Service Management

```bash
# Check status
sudo systemctl status semaphore-compose

# Restart service
sudo systemctl restart semaphore-compose

# View logs
sudo journalctl -u semaphore-compose -f

# Stop service
sudo systemctl stop semaphore-compose

# Disable auto-start
sudo systemctl disable semaphore-compose
```

## 🐳 Container Management

```bash
# View running containers
docker compose -f /opt/semaphore/docker-compose.yml ps

# View logs
docker compose -f /opt/semaphore/docker-compose.yml logs -f

# Restart containers
docker compose -f /opt/semaphore/docker-compose.yml restart

# Stop containers
docker compose -f /opt/semaphore/docker-compose.yml down

# Update containers
docker compose -f /opt/semaphore/docker-compose.yml pull
docker compose -f /opt/semaphore/docker-compose.yml up -d
```

## 🔒 Security Considerations

1. **Change default passwords** before deployment
2. **Use SSH keys** instead of password authentication
3. **Firewall rules**: Only allow necessary ports (22, 3000)
4. **Regular updates**: Keep VM and containers updated
5. **Backup data**: Regular backups of `/opt/semaphore/`

## 🔍 Troubleshooting

### VM Connection Issues
```bash
# Test VM connectivity
ansible control_nodes -i infra/ansible/inventories/prod/hosts.yml -m ping

# Check SSH connection
ssh ubuntu@<VM_IP>
```

### Service Issues
```bash
# Check systemd service
sudo systemctl status semaphore-compose

# Check Docker service
sudo systemctl status docker

# Check container logs
docker compose -f /opt/semaphore/docker-compose.yml logs
```

### Database Issues
```bash
# Connect to database
docker exec -it semaphore_postgres psql -U semaphore -d semaphore

# Check database logs
docker logs semaphore_postgres
```

### Port Issues
```bash
# Check if port 3000 is listening
sudo netstat -tlnp | grep 3000

# Check firewall
sudo ufw status
```

## 🔄 Backup & Recovery

### Backup
```bash
# Create backup directory
sudo mkdir -p /backup/semaphore/$(date +%Y%m%d)

# Backup database
docker exec semaphore_postgres pg_dump -U semaphore semaphore > /backup/semaphore/$(date +%Y%m%d)/database.sql

# Backup configuration
sudo cp -r /opt/semaphore/config /backup/semaphore/$(date +%Y%m%d)/
```

### Recovery
```bash
# Restore database
docker exec -i semaphore_postgres psql -U semaphore -d semaphore < /backup/semaphore/YYYYMMDD/database.sql

# Restore configuration
sudo cp -r /backup/semaphore/YYYYMMDD/config/* /opt/semaphore/config/

# Restart services
sudo systemctl restart semaphore-compose
```

## 🎉 Post-Installation

After successful deployment:

1. **Access Semaphore**: `http://<VM_IP>:3000`
2. **Login** with admin credentials
3. **Create your first project**
4. **Add your repositories**
5. **Configure task templates**
6. **Set up user access**

## 📚 Additional Resources

- [Semaphore Documentation](https://docs.semaphoreui.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Ansible Documentation](https://docs.ansible.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**🎯 Result**: A production-ready Ansible Semaphore installation that survives reboots, automatically starts, and maintains persistent data.
