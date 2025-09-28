# Complete Semaphore SSH Setup Guide

## Current Status

✅ **SSH Keys Generated**: ED25519 key pair ready  
✅ **GitHub Repository**: Created and accessible  
✅ **Semaphore Repository**: Configured (ID: 1)  
✅ **Current SSH Key**: Using ID 4 (Network Device Admin Credentials)  

## SSH Key Details

### 🔑 **Public Key** (Add to GitHub):
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGOl0YviIY9bZtVk0AVjHY+ETA77iyB9zczdBl9VDHKB semaphore@github.com
```

### 🔐 **Private Key** (Add to Semaphore):
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACBjpdGL4iGPW2bVZNAFYx2PhEwO+4sgfc3M3QZfVQxygQAAAJhJ0FAQSdBQ
EAAAAAtzc2gtZWQyNTUxOQAAACBjpdGL4iGPW2bVZNAFYx2PhEwO+4sgfc3M3QZfVQxygQ
AAAEBmj3EDMFuU4o60LHBu7sOyVPGsrcDXrCZPSEON4edj9WOl0YviIY9bZtVk0AVjHY+E
TA77iyB9zczdBl9VDHKBAAAAFHNlbWFwaG9yZUBnaXRodWIuY29tAQ==
-----END OPENSSH PRIVATE KEY-----
```

## Step-by-Step Setup

### Step 1: Add Public Key to GitHub

1. **Navigate to Repository Settings**:
   - Go to: https://github.com/alamotechllc/tk-proxmox-infrastructure/settings/keys

2. **Add Deploy Key**:
   - Click: **"Add deploy key"**
   - **Title**: `Semaphore-Access`
   - **Key**: Copy the public key above
   - **✅ Check**: "Allow write access"
   - Click: **"Add key"**

### Step 2: Add Private Key to Semaphore

1. **Access Semaphore UI**:
   - Go to: http://172.23.5.22:3000
   - Login with admin credentials

2. **Navigate to Keys**:
   - Go to: **Project Settings** → **Keys**

3. **Create New SSH Key**:
   - Click: **"Create new key"**
   - **Name**: `GitHub-Repository-Access`
   - **Type**: `SSH`
   - **Data**: Copy the private key above (including BEGIN/END lines)
   - Click: **"Save"**

### Step 3: Update Repository Configuration

1. **Navigate to Repositories**:
   - Go to: **Project Settings** → **Repositories**

2. **Edit Repository**:
   - Click on: **"TK-Proxmox-Infrastructure-GitHub"**
   - **SSH Key**: Select **"GitHub-Repository-Access"** (the new key)
   - **Save** changes

### Step 4: Test the Integration

1. **Run Interface Listing Template**:
   - Go to: **Templates** → **"List Switch Interfaces (with Survey)"**
   - Click: **"Run"**
   - Select: Any switch from the dropdown
   - Click: **"Run Task"**

2. **Verify Success**:
   - Check that playbooks are found from GitHub
   - Verify no "playbook not found" errors
   - Confirm interface listing works correctly

## Current Configuration

### Repository Details:
- **ID**: 1
- **Name**: TK-Proxmox-Infrastructure-GitHub
- **Git URL**: https://github.com/alamotechllc/tk-proxmox-infrastructure.git
- **Branch**: main
- **Current SSH Key**: ID 4 (will be updated to new key)

### Available SSH Keys:
- **ID 4**: Network Device Admin Credentials (current)
- **ID 5**: GitHub (none) (will be replaced)

## Verification Commands

After setup, you can verify the integration by running these templates:

### Template 22: List Switch Interfaces
- **Purpose**: Lists available interfaces for selected switch
- **Survey Variables**: Switch selection dropdown
- **Expected Result**: Interface listing with port descriptions

### Template 14: Switch-Specific VLAN Assignment  
- **Purpose**: Assigns VLANs to switch ports
- **Survey Variables**: Switch, port, and VLAN selection
- **Expected Result**: VLAN assignment simulation

## Troubleshooting

### Issue: "Playbook not found"
**Solution**: Verify GitHub repository has the playbook files and SSH key has read access

### Issue: "Permission denied"
**Solution**: Check that deploy key has "Allow write access" enabled in GitHub

### Issue: "SSH key not found"
**Solution**: Verify private key was added correctly to Semaphore with proper formatting

### Issue: "Repository update failed"
**Solution**: Check that the new SSH key exists and is properly formatted

## Success Indicators

✅ **GitHub Deploy Key**: Added with write access  
✅ **Semaphore SSH Key**: Created and configured  
✅ **Repository Updated**: Using new SSH key  
✅ **Template Execution**: No playbook errors  
✅ **GitHub Access**: Playbooks loaded from repository  

## Next Steps After Setup

1. **Test Both Templates**: Verify VLAN assignment and interface listing
2. **Document Results**: Record any issues or successes
3. **Monitor Performance**: Check template execution times
4. **Backup Configuration**: Save working configuration
5. **Team Training**: Share setup with team members

---

*SSH Setup Guide - Ready for Implementation*  
*Date: September 26, 2025*  
*Keys Generated: ED25519 (High Security)*
