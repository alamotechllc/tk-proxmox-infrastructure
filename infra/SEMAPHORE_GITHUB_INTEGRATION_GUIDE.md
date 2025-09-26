# Semaphore GitHub Integration Guide

## Overview

Semaphore has built-in GitHub integration that's much more sophisticated and secure than manual SSH key management. This guide will help you set up proper GitHub integration.

## Benefits of Built-in GitHub Integration

✅ **Automatic Deploy Keys**: Semaphore generates deploy keys automatically
✅ **Proper Permissions**: GitHub App/OAuth handles permissions correctly  
✅ **Better Security**: No manual SSH key management required
✅ **Easier Setup**: No need to manually copy keys between systems
✅ **Automatic Updates**: Semaphore handles key rotation and updates

## Setup Options

### Option 1: GitHub OAuth App (Recommended for Personal Use)

1. **Connect Semaphore to GitHub**:
   - Go to Semaphore UI: http://172.23.5.22:3000
   - Navigate to Account Settings
   - Find "Git Integration" section
   - Click "Connect" next to GitHub
   - Sign in to your GitHub account
   - Choose access level:
     - **All repositories** (recommended for development)
     - **Only select repositories** (for production)

2. **Create New Repository in Semaphore**:
   - Go to Project Settings → Repositories
   - Click "Create new repository"
   - Select "GitHub" tab
   - Choose `alamotechllc/tk-proxmox-infrastructure` from the list
   - Complete the setup

### Option 2: GitHub App (Recommended for Organizations)

1. **Install GitHub App**:
   - Go to GitHub → Settings → Applications → GitHub Apps
   - Find "Semaphore" in the marketplace
   - Click "Install"
   - Choose repositories to grant access to
   - Complete installation

2. **Create Repository in Semaphore**:
   - Go to Project Settings → Repositories  
   - Click "Create new repository"
   - Select "GitHub App" tab
   - Choose your repository from the list

## Step-by-Step Setup

### Step 1: Connect Semaphore to GitHub

1. **Access Semaphore UI**: http://172.23.5.22:3000
2. **Go to Account Settings**: Click your profile → Settings
3. **Find Git Integration**: Look for "Git Integration" or "GitHub" section
4. **Click Connect**: Select GitHub and follow the OAuth flow
5. **Authorize Access**: Grant necessary permissions to your repositories

### Step 2: Create New Repository

1. **Navigate to Repositories**: Project Settings → Repositories
2. **Create New Repository**: Click "Create new repository"
3. **Select GitHub**: Choose "GitHub" tab (or "GitHub App" if using App)
4. **Select Repository**: Choose `alamotechllc/tk-proxmox-infrastructure`
5. **Configure Settings**:
   - **Name**: `TK-Proxmox-Infrastructure-GitHub`
   - **Branch**: `main`
   - **Path**: Leave default or specify if needed
6. **Save**: Complete the repository creation

### Step 3: Update Templates

After creating the new GitHub repository:

1. **Update Template 14**:
   - Go to Templates → Switch-Specific VLAN Assignment
   - Edit template settings
   - Change repository to the new GitHub repository
   - Save changes

2. **Update Template 22**:
   - Go to Templates → List Switch Interfaces (with Survey)
   - Edit template settings  
   - Change repository to the new GitHub repository
   - Save changes

### Step 4: Test Integration

1. **Run Template 22**: Test the interface listing template
2. **Verify Playbook Access**: Ensure playbooks are found from GitHub
3. **Check Survey Variables**: Confirm dropdown works correctly
4. **Review Logs**: Check task execution logs for any issues

## Troubleshooting

### Issue: "Repository not found in GitHub list"
**Solution**:
- Ensure GitHub integration is properly connected
- Check repository permissions in GitHub
- Verify the repository exists and is accessible

### Issue: "Playbook not found" 
**Solution**:
- Verify the playbook path in templates matches GitHub structure
- Check that files are committed to the repository
- Ensure the correct branch is selected

### Issue: "Access denied"
**Solution**:
- Check GitHub repository permissions
- Verify OAuth/App installation is complete
- Ensure deploy keys are properly configured

## Current Repository Structure

Our GitHub repository structure:
```
tk-proxmox-infrastructure/
├── infra/
│   ├── ansible/
│   │   ├── inventories/
│   │   │   ├── network_switches.yml
│   │   │   └── prod/hosts.yml
│   │   └── playbooks/
│   │       ├── network/
│   │       │   ├── list_switch_interfaces.yml
│   │       │   └── switch_specific_vlan_assignment.yml
│   │       └── monitoring/
│   └── scripts/
└── README.md
```

## Template Playbook Paths

After GitHub integration, templates should use:
- **Template 14**: `infra/ansible/playbooks/network/switch_specific_vlan_assignment.yml`
- **Template 22**: `infra/ansible/playbooks/network/list_switch_interfaces.yml`

## Migration from Current Setup

### Current Status
- ✅ Repository: https://github.com/alamotechllc/tk-proxmox-infrastructure
- ✅ Templates: 14 and 22 configured
- ✅ Survey Variables: Working correctly
- ⚠️ Authentication: Using manual SSH keys (should migrate to GitHub integration)

### Migration Steps
1. **Set up GitHub integration** (follow steps above)
2. **Create new GitHub repository** in Semaphore
3. **Update templates** to use new repository
4. **Test templates** to ensure they work
5. **Remove old repository** configuration
6. **Clean up manual SSH keys** (no longer needed)

## Security Benefits

### GitHub Integration vs Manual SSH Keys
- **Automatic Key Management**: No manual key generation/copying
- **Proper Permissions**: GitHub handles access control
- **Key Rotation**: Automatic key updates and rotation
- **Audit Trail**: Better logging and access tracking
- **Organization Control**: GitHub organization owners can manage access

## Next Steps

1. **Set up GitHub integration** in Semaphore
2. **Create new repository** using GitHub integration
3. **Update templates** to use new repository
4. **Test both templates** to ensure they work
5. **Document the new setup** for team members
6. **Remove old manual setup** files and configurations

---

*This approach is much more robust and follows Semaphore best practices*
*Last Updated: September 25, 2025*
