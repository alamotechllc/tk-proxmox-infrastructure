# Semaphore File Persistence Issue

## Problem Description

Semaphore templates fail with "playbook not found" errors because files in `/tmp/semaphore/` are not persisting between task runs. This is a known issue with Semaphore's file handling.

## Root Cause

Based on [GitHub Issue #225](https://github.com/semaphoreui/semaphore/issues/225), Semaphore has historical issues with:

1. **File Path Resolution**: Semaphore looks for playbooks in git repository structure (`/tmp/semaphore/playbooks/`) rather than template-specific directories
2. **Configuration Mismatch**: The actual `tmp_path` used by Semaphore may differ from configuration
3. **File Cleanup**: Files in `/tmp/semaphore/` may be cleaned up by system processes or Semaphore itself

## Current Solution

We've implemented a workaround by:

1. **Creating Git Repository Structure**: Copy files to `/tmp/semaphore/playbooks/network/`
2. **Automated Setup Script**: `setup_semaphore_files.sh` restores files when needed
3. **Dual File Placement**: Files are placed in both template directories and git repository structure

## File Locations

### Git Repository Structure (Where Semaphore Actually Looks)
```
/tmp/semaphore/
├── playbooks/network/
│   ├── list_switch_interfaces.yml
│   └── switch_specific_vlan_assignment.yml
└── inventories/
    ├── network_switches.yml
    └── prod/hosts.yml
```

### Template-Specific Directories (For Reference)
```
/tmp/semaphore/project_4/
├── repository_1_template_14/playbooks/network/
├── repository_1_template_22/playbooks/network/
└── inventory_7
```

## Manual Fix Commands

When templates fail with "playbook not found":

```bash
# Run the setup script to restore files
cd /Users/mike.turner/APP_Projects/tk-proxmox
./infra/scripts/setup_semaphore_files.sh

# Or manually copy files
cp infra/ansible/playbooks/network/list_switch_interfaces.yml /tmp/semaphore/playbooks/network/
cp infra/ansible/playbooks/network/switch_specific_vlan_assignment.yml /tmp/semaphore/playbooks/network/
cp infra/ansible/inventories/network_switches.yml /tmp/semaphore/inventories/
cp infra/ansible/inventories/prod/hosts.yml /tmp/semaphore/inventories/prod/
```

## Automated Solutions

### Option 1: Cron Job (Recommended)
Add to crontab to run every 5 minutes:

```bash
# Edit crontab
crontab -e

# Add this line
*/5 * * * * cd /Users/mike.turner/APP_Projects/tk-proxmox && ./infra/scripts/setup_semaphore_files.sh > /dev/null 2>&1
```

### Option 2: Systemd Service
Create a service that monitors and restores files:

```ini
[Unit]
Description=Semaphore File Persistence
After=network.target

[Service]
Type=oneshot
ExecStart=/Users/mike.turner/APP_Projects/tk-proxmox/infra/scripts/setup_semaphore_files.sh
User=mike.turner
WorkingDirectory=/Users/mike.turner/APP_Projects/tk-proxmox

[Install]
WantedBy=multi-user.target
```

### Option 3: File System Monitoring
Use `inotify` or similar to monitor `/tmp/semaphore/playbooks/` and restore files when they're deleted.

## Prevention Strategies

1. **Regular Monitoring**: Check file existence before running templates
2. **Automated Restoration**: Use cron job or systemd service
3. **Alternative Repository**: Consider using a persistent directory outside `/tmp/`
4. **Semaphore Configuration**: Investigate if `tmp_path` can be changed to a persistent location

## Verification Commands

Check if files exist:

```bash
# Check git repository structure
ls -la /tmp/semaphore/playbooks/network/

# Check template directories
ls -la /tmp/semaphore/project_4/repository_1_template_22/playbooks/network/

# Check inventory files
ls -la /tmp/semaphore/inventories/
```

## Related Issues

- [GitHub Issue #225](https://github.com/semaphoreui/semaphore/issues/225): Make Semaphore respect inventory file from playbook repo ansible.cfg
- [Semaphore API Documentation](https://semaphoreui.com/api-docs/)

## Status

- ✅ **Workaround Implemented**: Files are restored via setup script
- ✅ **Automation Ready**: Setup script can be automated
- ⚠️ **Persistence Issue**: Files may still disappear between runs
- 🔄 **Monitoring Needed**: Regular checks required

---

*Last Updated: September 25, 2025*
*Issue affects Templates 14 and 22*
