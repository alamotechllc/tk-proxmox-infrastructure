# GitHub SSH Setup Guide for Semaphore

## SSH Keys Generated Successfully ✅

I've generated SSH keys for GitHub integration. Here's how to complete the setup:

## Step 1: Add Public Key to GitHub

1. **Go to GitHub**: https://github.com/settings/keys
2. **Click**: "New SSH key"
3. **Title**: `Semaphore-TK-Proxmox`
4. **Key type**: `Authentication Key`
5. **Key**: Copy and paste this public key:

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGOl0YviIY9bZtVk0AVjHY+ETA77iyB9zczdBl9VDHKB semaphore@github.com
```

6. **Click**: "Add SSH key"

## Step 2: Add Private Key to Semaphore

1. **Go to Semaphore UI**: http://172.23.5.22:3000
2. **Navigate to**: Project Settings → Keys
3. **Click**: "Create new key"
4. **Fill in**:
   - **Name**: `GitHub-Repository-Access`
   - **Type**: `SSH`
   - **Data**: Copy and paste this private key:

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACBjpdGL4iGPW2bVZNAFYx2PhEwO+4sgfc3M3QZfVQxygQAAAJhJ0FAQSdBQ
EAAAAAtzc2gtZWQyNTUxOQAAACBjpdGL4iGPW2bVZNAFYx2PhEwO+4sgfc3M3QZfVQxygQ
AAAEBmj3EDMFuU4o60LHBu7sOyVPGsrcDXrCZPSEON4edj9WOl0YviIY9bZtVk0AVjHY+E
TA77iyB9zczdBl9VDHKBAAAAFHNlbWFwaG9yZUBnaXRodWIuY29tAQ==
-----END OPENSSH PRIVATE KEY-----
```

5. **Click**: "Save"

## Step 3: Update Repository Configuration

1. **In Semaphore UI**: Go to Project Settings → Repositories
2. **Edit Repository ID 1**:
   - **Name**: `TK-Proxmox-Infrastructure-GitHub`
   - **Git URL**: `https://github.com/alamotechllc/tk-proxmox-infrastructure.git`
   - **Git Branch**: `main`
   - **SSH Key**: Select `GitHub-Repository-Access` (the key you just created)
3. **Click**: "Save"

## Step 4: Test the Integration

1. **Go to Templates**: http://172.23.5.22:3000/project/4/templates
2. **Run Template 22**: "List Switch Interfaces (with Survey)"
3. **Select**: Any switch from the dropdown
4. **Click**: "Run"

## Troubleshooting

### Issue: "Repository access denied"
**Solution**: 
- Verify the SSH key is added to GitHub
- Check that the repository URL is correct
- Ensure the SSH key is selected in repository settings

### Issue: "Playbook not found"
**Solution**:
- Verify the playbook path is correct: `infra/ansible/playbooks/network/list_switch_interfaces.yml`
- Check that the repository was cloned successfully
- Look at the task logs for detailed error messages

### Issue: "SSH key not working"
**Solution**:
- Verify the private key was copied completely (including BEGIN/END lines)
- Check that the public key is in GitHub
- Try regenerating the SSH key pair if needed

## Verification Commands

Test SSH connection to GitHub:
```bash
ssh -T -i ~/.ssh/semaphore_github git@github.com
```

Expected output:
```
Hi alamotechllc! You've successfully authenticated, but GitHub does not provide shell access.
```

## File Locations

- **Private Key**: `~/.ssh/semaphore_github`
- **Public Key**: `~/.ssh/semaphore_github.pub`
- **GitHub Repository**: https://github.com/alamotechllc/tk-proxmox-infrastructure

## Security Notes

- The SSH keys are generated locally on your machine
- The private key should only be used in Semaphore
- The public key is safe to share (it's already in this document)
- Never share the private key content

## Next Steps

After completing the setup:

1. **Test both templates** to ensure they work with GitHub
2. **Remove local file setup scripts** (no longer needed)
3. **Update documentation** to reflect GitHub integration
4. **Set up automated deployments** if desired

---

*SSH keys generated: September 25, 2025*
*Ready for GitHub integration*
