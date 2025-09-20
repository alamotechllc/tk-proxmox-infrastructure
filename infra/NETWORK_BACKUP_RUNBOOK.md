# 🔌 Network Switch Configuration Backup Runbook

## 🎯 Overview

Comprehensive backup solution for multi-vendor network infrastructure including:
- **Arista EOS** switches (eAPI-based backup)
- **Cisco Nexus NX-OS** switches (CLI-based backup)  
- **Cisco Catalyst IOS-XE** switches (CLI-based backup)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Semaphore     │───▶│  Ansible        │───▶│  Network        │
│   Scheduler     │    │  Playbooks      │    │  Switches       │
│                 │    │                 │    │                 │
│ • Daily/Weekly  │    │ • Vendor-aware  │    │ • Arista EOS    │
│ • Retention     │    │ • Error handling│    │ • Nexus NX-OS   │
│ • Compression   │    │ • Reporting     │    │ • Catalyst IOS  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Backup Storage │
                       │                 │
                       │ • Timestamped   │
                       │ • Compressed    │
                       │ • Organized     │
                       └─────────────────┘
```

## 📁 File Structure

```
infra/
├── ansible/
│   ├── playbooks/network/
│   │   ├── backup_switches.yml           # Main backup playbook
│   │   └── schedule_backups.yml          # Backup scheduling setup
│   ├── templates/
│   │   └── backup_report.j2              # Backup summary report template
│   └── inventories/prod/hosts.yml        # Network device inventory
├── scripts/
│   └── backup_network_switches.sh        # Backup execution script
└── NETWORK_BACKUP_RUNBOOK.md             # This documentation
```

## 🚀 Quick Start

### 1. **Manual Backup (All Switches)**
```bash
cd /Users/mike.turner/APP_Projects/tk-proxmox
./infra/scripts/backup_network_switches.sh
```

### 2. **Vendor-Specific Backup**
```bash
# Backup only Arista switches
./infra/scripts/backup_network_switches.sh -v arista

# Backup only Nexus switches  
./infra/scripts/backup_network_switches.sh -v nexus

# Backup only Catalyst switches
./infra/scripts/backup_network_switches.sh -v catalyst
```

### 3. **Custom Options**
```bash
# Custom location with compression and 60-day retention
./infra/scripts/backup_network_switches.sh -l /backup/network -c -r 60

# Dry run to see what would be backed up
./infra/scripts/backup_network_switches.sh -n
```

## 🔧 Configuration

### **Backup Targets (Your Actual Switches)**

#### **🔹 Arista EOS Core Switch**
- **Device**: `arista-core-01` (172.23.5.1)
- **Model**: DCS-7280SR-48C6
- **OS**: EOS-4.28.3M
- **Backup Method**: eAPI + CLI
- **Files Generated**:
  - `arista-core-01_[timestamp].cfg` (running-config)
  - `arista-core-01_startup_[timestamp].cfg` (startup-config)
  - `arista-core-01_info_[timestamp].txt` (system info)

#### **🔹 Cisco Nexus Aggregation Switch**
- **Device**: `nexus-agg-01` (172.23.5.2)
- **Model**: N9K-C93180YC-EX
- **OS**: NX-OS 9.3(8)
- **Backup Method**: CLI via SSH
- **Files Generated**:
  - `nexus-agg-01_[timestamp].cfg` (running-config)
  - `nexus-agg-01_startup_[timestamp].cfg` (startup-config)
  - `nexus-agg-01_info_[timestamp].txt` (system info + VPC status)

#### **🔹 Cisco Catalyst Access Switches**
- **Devices**: 
  - `catalyst-access-01` (172.23.5.10) - C9300-48P
  - `catalyst-access-02` (172.23.5.11) - C9300-24P
- **OS**: IOS-XE 16.12.09
- **Backup Method**: CLI via SSH
- **Files Generated**:
  - `catalyst-access-0X_[timestamp].cfg` (running-config)
  - `catalyst-access-0X_startup_[timestamp].cfg` (startup-config)
  - `catalyst-access-0X_info_[timestamp].txt` (system info + stack status)

### **Backup Storage Structure**
```
/opt/network_backups/
├── 2025-09-20/                    # Daily backups
│   ├── arista/
│   │   ├── arista-core-01_1726867200.cfg
│   │   ├── arista-core-01_startup_1726867200.cfg
│   │   └── arista-core-01_info_1726867200.txt
│   ├── nexus/
│   │   ├── nexus-agg-01_1726867200.cfg
│   │   └── nexus-agg-01_info_1726867200.txt
│   ├── catalyst/
│   │   ├── catalyst-access-01_1726867200.cfg
│   │   └── catalyst-access-02_1726867200.cfg
│   └── logs/
│       └── backup_summary_1726867200.txt
├── daily/                         # Daily retention
├── weekly/                        # Weekly retention
├── monthly/                       # Monthly retention
└── logs/
    ├── daily_backup.log
    ├── weekly_backup.log
    └── monthly_backup.log
```

## ⚙️ Backup Features

### **✅ Multi-Vendor Support**
- **Arista EOS**: Uses `eos_config` and `eos_facts` modules
- **Cisco Nexus**: Uses `nxos_config` and `nxos_facts` modules
- **Cisco Catalyst**: Uses `ios_config` and `ios_facts` modules

### **✅ Comprehensive Backup**
- **Running Configuration**: Current active config
- **Startup Configuration**: Boot configuration
- **System Information**: Hardware details, uptime, interfaces
- **Vendor-Specific Data**: VPC status (Nexus), Stack info (Catalyst)

### **✅ Error Handling**
- **Individual Device Failures**: Continues backing up other devices
- **Detailed Logging**: Failure logs with timestamps
- **Retry Logic**: Built-in Ansible retry mechanisms
- **Success Reporting**: Detailed success/failure summary

### **✅ Storage Management**
- **Organized Structure**: Date-based directories
- **Retention Policies**: Automatic cleanup of old backups
- **Compression**: Optional gzip compression
- **Space Monitoring**: Disk usage tracking

## 🕐 Automated Scheduling

### **Setup Automated Backups**
```bash
# Configure scheduled backups
cd /Users/mike.turner/APP_Projects/tk-proxmox/infra/ansible
ansible-playbook playbooks/network/schedule_backups.yml
```

### **Default Schedule**
- **Daily**: 02:30 AM (7-day retention)
- **Weekly**: Sunday 03:00 AM (30-day retention)
- **Monthly**: 1st of month 04:00 AM (365-day retention)

### **Monitoring Backups**
```bash
# Check backup status
/opt/network_backups/check_backup_status.sh

# View backup logs
tail -f /opt/network_backups/logs/daily_backup.log

# List recent backups
find /opt/network_backups -name "*.cfg" -mtime -7
```

## 🔧 Usage Examples

### **Basic Operations**
```bash
# Backup all switches
./infra/scripts/backup_network_switches.sh

# Backup with compression
./infra/scripts/backup_network_switches.sh -c

# Backup to custom location
./infra/scripts/backup_network_switches.sh -l /backup/network

# Dry run (test without executing)
./infra/scripts/backup_network_switches.sh -n
```

### **Vendor-Specific Operations**
```bash
# Backup only Arista switches
./infra/scripts/backup_network_switches.sh -v arista

# Backup only Nexus switches with 60-day retention
./infra/scripts/backup_network_switches.sh -v nexus -r 60

# Backup only Catalyst switches with compression
./infra/scripts/backup_network_switches.sh -v catalyst -c
```

### **Advanced Operations**
```bash
# Full backup with all options
./infra/scripts/backup_network_switches.sh \
  -v all \
  -l /opt/network_backups \
  -r 90 \
  -c

# Emergency backup before maintenance
./infra/scripts/backup_network_switches.sh \
  -l /backup/emergency/$(date +%Y%m%d_%H%M) \
  -c \
  -f
```

## 📊 Monitoring & Reporting

### **Backup Summary Report**
Each backup generates a detailed summary:
- Device count and success rate
- Vendor breakdown
- File locations and sizes
- Failed device details
- Next steps and recommendations

### **Log Files**
- **Execution Logs**: `/opt/network_backups/logs/`
- **Ansible Logs**: Detailed playbook execution
- **Error Logs**: Device-specific failure details
- **Summary Reports**: Human-readable backup summaries

### **Health Monitoring**
```bash
# Check backup health
/opt/network_backups/check_backup_status.sh

# Monitor backup size trends
du -sh /opt/network_backups/daily/* | tail -10

# Check for backup failures
grep -r "FAILED" /opt/network_backups/logs/
```

## 🔒 Security Considerations

### **Credential Management**
- ✅ **Environment Variables**: Credentials stored in Semaphore environment
- ✅ **No Plaintext**: No passwords in playbooks or scripts
- ✅ **Vendor-Specific**: Separate credentials per device type
- ✅ **Rotation-Ready**: Easy credential updates

### **Access Control**
- **File Permissions**: Restricted access to backup files
- **Network Access**: Backup server has limited network access
- **Audit Trail**: All backup operations logged
- **Encryption**: Optional backup file encryption

### **Compliance**
- **Retention Policies**: Configurable retention periods
- **Change Tracking**: Configuration drift detection
- **Documentation**: Self-documenting backup process
- **Recovery Testing**: Built-in restore verification

## 🚨 Troubleshooting

### **Common Issues**

#### **Authentication Failures**
```bash
# Check credentials in Semaphore environment
# Update: Project → Environment → Multi-Vendor Switch Credentials

# Test connectivity
ansible arista_devices -i inventories/prod/hosts.yml -m ping
ansible cisco_nxos_devices -i inventories/prod/hosts.yml -m ping
ansible cisco_ios_devices -i inventories/prod/hosts.yml -m ping
```

#### **Storage Issues**
```bash
# Check disk space
df -h /opt/network_backups

# Check permissions
ls -la /opt/network_backups

# Clean old backups manually
find /opt/network_backups -mtime +30 -delete
```

#### **Network Connectivity**
```bash
# Test device reachability
ansible all -i inventories/prod/hosts.yml -m ping --limit "arista_devices"

# Check SSH connectivity
ssh admin@172.23.5.1  # Arista
ssh admin@172.23.5.2  # Nexus
ssh admin@172.23.5.10 # Catalyst
```

## 🔄 Disaster Recovery

### **Configuration Restore**
```bash
# Restore Arista configuration
scp backup_file.cfg admin@172.23.5.1:/mnt/flash/
# Then via CLI: copy flash:backup_file.cfg running-config

# Restore Nexus configuration  
scp backup_file.cfg admin@172.23.5.2:backup_file.cfg
# Then via CLI: copy backup_file.cfg running-config

# Restore Catalyst configuration
scp backup_file.cfg admin@172.23.5.10:backup_file.cfg
# Then via CLI: copy backup_file.cfg running-config
```

### **Emergency Procedures**
1. **Identify failed device** from monitoring alerts
2. **Locate latest backup** in `/opt/network_backups/`
3. **Verify backup integrity** before restore
4. **Execute restore procedure** for specific vendor
5. **Validate configuration** after restore
6. **Update documentation** with incident details

## 📈 Operational Benefits

### **✅ Automated Protection**
- **Daily Backups**: Protect against configuration drift
- **Change Tracking**: Compare configurations over time
- **Compliance**: Meet regulatory backup requirements
- **Disaster Recovery**: Rapid restoration capabilities

### **✅ Operational Efficiency**
- **Multi-Vendor**: Single process for all switch types
- **Scalable**: Easy to add new devices
- **Centralized**: All backups in one location
- **Automated**: No manual intervention required

### **✅ Risk Mitigation**
- **Configuration Loss**: Protect against accidental changes
- **Hardware Failure**: Rapid device replacement
- **Human Error**: Rollback capabilities
- **Compliance**: Audit trail for changes

---

## 🎮 **Your Network Backup Runbook is Ready!**

### **🚀 To Execute:**
1. **Manual Backup**: `./infra/scripts/backup_network_switches.sh`
2. **Scheduled Backup**: Run `schedule_backups.yml` playbook
3. **Monitor Status**: Use `/opt/network_backups/check_backup_status.sh`

### **📋 What Gets Backed Up:**
- ✅ **Arista Core Switch** (172.23.5.1) - Running + Startup configs
- ✅ **Nexus Aggregation Switch** (172.23.5.2) - Running + Startup configs  
- ✅ **Catalyst Access Switches** (172.23.5.10-11) - Running + Startup configs
- ✅ **System Information** - Hardware details, interfaces, vendor-specific data
- ✅ **Backup Reports** - Detailed success/failure summaries

### **🔐 Security Features:**
- ✅ **Secure Credentials** - Environment variable storage
- ✅ **Access Control** - Restricted file permissions
- ✅ **Audit Trail** - Complete backup logging
- ✅ **Retention Management** - Automatic cleanup

**Your multi-vendor network switch backup runbook is complete and ready for production use!** 🎉
