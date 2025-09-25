# Network Backup Runbook

## 🎯 Overview

The Network Backup Runbook is a comprehensive Ansible-based solution for backing up network infrastructure configurations with enterprise-grade features and best practices.

## 🚀 Features

### 🛡️ **Safety & Reliability**
- **Pre-backup Health Checks**: Validates device health before backup operations
- **Connectivity Validation**: Tests SSH reachability before proceeding
- **Serial Execution**: Prevents network overload with controlled concurrency
- **Graceful Error Handling**: Continues with other devices if one fails
- **Protected Operations**: Validates credentials and permissions

### 📋 **Comprehensive Backup**
- **Multi-Vendor Support**: Arista EOS, Cisco Nexus NX-OS, Cisco Catalyst IOS/IOS-XE
- **Configuration Backup**: Complete running configurations with timestamps
- **Change Detection**: Automatic comparison with previous backups
- **Health Monitoring**: CPU, memory, temperature, and interface status
- **Structured Storage**: Organized by vendor and date

### 🔧 **Automation & Efficiency**
- **Automated Retention**: Configurable cleanup of old backups
- **Compression Support**: Optional compression for storage efficiency
- **Parallel Processing**: Configurable concurrency for faster execution
- **Notification Integration**: Email and Slack notifications
- **HTML Reports**: Professional backup reports with statistics

### 🔒 **Security**
- **Semaphore Secrets**: Secure credential management
- **No Plaintext Passwords**: All credentials encrypted
- **Audit Trail**: Complete logging of all operations
- **Secure Permissions**: Proper file and directory permissions
- **Role-Based Access**: Integration with Semaphore RBAC

## 📁 Repository Structure

```
infra/
├── ansible/
│   ├── playbooks/network/
│   │   └── network_backup_runbook.yml      # Main backup playbook
│   └── templates/
│       └── backup_report_comprehensive.j2   # HTML report template
├── scripts/
│   └── run_network_backup.sh               # Execution wrapper script
└── NETWORK_BACKUP_RUNBOOK.md              # This documentation
```

## 🔧 Configuration

### Inventory Requirements

Your Ansible inventory must include network devices with the following structure:

```yaml
network_switches:
  children:
    core_switches:
      hosts:
        arista-core-01:
          ansible_host: 172.23.5.1
          device_type: arista_eos
        nexus-agg-01:
          ansible_host: 172.23.5.2
          device_type: cisco_nxos
    
    access_switches:
      hosts:
        catalyst-access-01:
          ansible_host: 172.23.5.10
          device_type: cisco_ios
        catalyst-access-02:
          ansible_host: 172.23.5.11
          device_type: cisco_ios
```

### Required Variables

The runbook uses the following variables (typically provided by Semaphore secrets):

```yaml
# Security (Semaphore Secrets)
semaphore_admin_user: admin
semaphore_admin_password: "{{ secret }}"
semaphore_enable_password: "{{ secret }}"

# Backup Configuration
backup_location: /opt/network_backups
backup_retention_days: 30
compress_backups: true
detect_changes: true
backup_concurrency: 2

# Notifications (Optional)
notification_email: admin@company.com
slack_webhook_url: https://hooks.slack.com/...
```

## 🚀 Usage

### Command Line Execution

```bash
# Basic backup of all switches
./infra/scripts/run_network_backup.sh

# Backup with custom settings
./infra/scripts/run_network_backup.sh \
  --devices core_switches \
  --location /backup/network \
  --retention 60 \
  --compress \
  --email admin@company.com

# Dry run to test configuration
./infra/scripts/run_network_backup.sh --dry-run --verbose
```

### Semaphore Template Execution

1. **Create Template** in Semaphore:
   - **Name**: Network Backup Runbook
   - **Playbook**: `infra/ansible/playbooks/network/network_backup_runbook.yml`
   - **Inventory**: Your network inventory
   - **Extra Variables**: See configuration section

2. **Configure Secrets**:
   - `semaphore_admin_user`: Network device admin username
   - `semaphore_admin_password`: Network device admin password
   - `semaphore_enable_password`: Enable/privileged mode password

3. **Execute Template** with desired parameters

### Available Options

| Option | Description | Default |
|--------|-------------|---------|
| `--devices GROUP` | Target device group | `network_switches` |
| `--location PATH` | Backup storage location | `/opt/network_backups` |
| `--retention DAYS` | Backup retention period | `30` |
| `--compress` | Enable backup compression | `true` |
| `--detect-changes` | Enable change detection | `true` |
| `--concurrency NUM` | Parallel device processing | `2` |
| `--email EMAIL` | Notification email address | None |
| `--slack-webhook URL` | Slack webhook for notifications | None |
| `--dry-run` | Test without making changes | `false` |
| `--verbose` | Detailed output | `false` |

## 📊 Output Structure

The runbook creates the following directory structure:

```
/opt/network_backups/
├── 2024-01-15/                    # Daily backup directory
│   ├── arista/                    # Arista EOS configurations
│   │   ├── arista-core-01_1642204800.cfg
│   │   └── arista-dist-01_1642204801.cfg
│   ├── nexus/                     # Cisco Nexus configurations
│   │   └── nexus-agg-01_1642204802.cfg
│   └── catalyst/                  # Cisco Catalyst configurations
│       ├── catalyst-access-01_1642204803.cfg
│       └── catalyst-access-02_1642204804.cfg
├── reports/                       # Analysis and reports
│   ├── network_backup_report_1642204800.html
│   ├── arista-core-01_changes_1642204800.diff
│   └── nexus-agg-01_changes_1642204801.txt
├── logs/                          # Execution and health logs
│   ├── arista-core-01_health_1642204800.log
│   └── backup_execution_1642204800.log
└── network_backup_2024-01-15_1642204800.tar.gz  # Compressed archive
```

## 🔍 Monitoring & Reporting

### Health Checks

Before each backup, the runbook performs:

- **Connectivity Test**: SSH reachability validation
- **System Health**: CPU, memory, temperature monitoring
- **Interface Status**: Network interface state verification
- **Environment Check**: Power supplies and cooling systems

### Change Detection

When enabled, the runbook:

- Compares current configuration with previous backup
- Generates unified diff files for changed devices
- Creates change summary reports
- Highlights configuration modifications

### Comprehensive Reports

The runbook generates HTML reports containing:

- **Executive Summary**: Backup statistics and status
- **Device Status Table**: Per-device backup results
- **Health Check Results**: System health analysis
- **Change Detection**: Configuration change summary
- **Security Audit**: Security features verification

## 🛠️ Best Practices Implementation

### Network Automation Standards

- **Idempotent Operations**: Safe to run multiple times
- **Vendor Abstraction**: Consistent interface across vendors
- **Error Recovery**: Graceful handling of device failures
- **Logging Standards**: Structured logging for troubleshooting

### Security Best Practices

- **Credential Protection**: No plaintext passwords in logs
- **Secure Storage**: Encrypted credential management
- **Audit Compliance**: Complete operation tracking
- **Access Control**: Role-based permission management

### Operational Excellence

- **Automated Retention**: Prevents storage overflow
- **Performance Optimization**: Parallel processing support
- **Notification Integration**: Proactive alerting
- **Documentation**: Self-documenting reports and logs

## 🔧 Customization

### Adding New Vendors

To support additional network vendors:

1. **Add Device Detection**:
   ```yaml
   - name: Get device info (New Vendor)
     new_vendor_command:
       commands:
         - "show version"
         - "show system"
     when: device_type == "new_vendor"
   ```

2. **Add Backup Logic**:
   ```yaml
   - name: Backup New Vendor configuration
     new_vendor_config:
       backup: yes
       backup_options:
         filename: "{{ inventory_hostname }}_{{ backup_timestamp }}.cfg"
         dir_path: "{{ backup_base_path }}/{{ backup_date }}/new_vendor/"
     when: device_type == "new_vendor"
   ```

3. **Update Directory Structure**: Add vendor-specific directories

### Custom Health Checks

Add vendor-specific health monitoring:

```yaml
- name: Custom health check
  new_vendor_command:
    commands:
      - "show environment"
      - "show processes"
  register: custom_health
  when: device_type == "new_vendor"
```

### Notification Customization

Extend notification support:

```yaml
- name: Custom notification
  uri:
    url: "{{ custom_webhook_url }}"
    method: POST
    body_format: json
    body:
      message: "Backup completed for {{ inventory_hostname }}"
  when: custom_webhook_url is defined
```

## 🚨 Troubleshooting

### Common Issues

1. **SSH Connection Failures**:
   - Verify device IP addresses and SSH access
   - Check firewall rules and network connectivity
   - Validate SSH key authentication

2. **Authentication Errors**:
   - Verify Semaphore secrets configuration
   - Check username and password validity
   - Ensure enable password is correct

3. **Permission Denied**:
   - Verify backup directory permissions
   - Check Ansible execution user privileges
   - Ensure sufficient disk space

4. **Network Module Errors**:
   - Install required Ansible collections:
     ```bash
     ansible-galaxy collection install arista.eos
     ansible-galaxy collection install cisco.nxos
     ansible-galaxy collection install cisco.ios
     ```

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
./infra/scripts/run_network_backup.sh --verbose --dry-run
```

### Log Analysis

Check the following locations for detailed information:

- **Execution Logs**: `{{ backup_location }}/logs/`
- **Ansible Output**: Standard Ansible logging
- **Health Reports**: Device-specific health status
- **Change Reports**: Configuration difference analysis

## 📚 Additional Resources

- [Ansible Network Automation Guide](https://docs.ansible.com/ansible/latest/network/index.html)
- [Arista EOS Collection](https://galaxy.ansible.com/arista/eos)
- [Cisco NX-OS Collection](https://galaxy.ansible.com/cisco/nxos)
- [Cisco IOS Collection](https://galaxy.ansible.com/cisco/ios)
- [Semaphore Documentation](https://docs.semaphoreui.com/)

## 🤝 Contributing

To contribute improvements:

1. Test changes in a lab environment
2. Follow Ansible best practices
3. Update documentation
4. Ensure backward compatibility
5. Add appropriate error handling

## 📄 License

This runbook is part of the TK-Proxmox infrastructure automation project.