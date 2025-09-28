# 🔒 Security Guidelines for Proxmox + Ansible Automation

This document outlines security best practices and guidelines for the Proxmox + Ansible automation baseline.

## 🛡️ Security Overview

The automation baseline implements multiple layers of security:

1. **API Token Authentication** - Secure Proxmox API access
2. **SSH Key-based Authentication** - No password authentication
3. **Vault Encryption** - Encrypted sensitive data storage
4. **Network Security** - UFW firewall configuration
5. **Access Control** - Least privilege principles
6. **Audit Logging** - Comprehensive operation logging

## 🔑 Authentication & Authorization

### Proxmox API Tokens

**Best Practices:**
- Use dedicated API tokens for automation (not user passwords)
- Implement token expiration where possible
- Use least privilege principle for token permissions
- Rotate tokens regularly (recommended: every 90 days)

**Token Configuration:**
```bash
# Example token creation
User: root@pam
Token ID: ansible-automation
Privilege Separation: ❌ (disabled for full access)
Expiration: 2024-12-31
```

**Security Considerations:**
- Store tokens in encrypted vault files only
- Never commit tokens to version control
- Use environment variables for temporary access
- Monitor token usage via Proxmox logs

### SSH Key Management

**Key Generation:**
```bash
# Generate Ed25519 key pair (recommended)
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -C "ansible-control-$(hostname)"

# Set proper permissions
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

**Key Distribution:**
- Distribute public keys via cloud-init during VM creation
- Use SSH key forwarding for secure access
- Implement key rotation procedures
- Monitor SSH access logs

**SSH Configuration:**
```bash
# Secure SSH client configuration
Host *
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    ControlMaster auto
    ControlPath /tmp/ansible-ssh-%h-%p-%r
    ControlPersist 60s
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

## 🔐 Data Protection

### Vault Encryption

**Ansible Vault Usage:**
```bash
# Encrypt sensitive files
ansible-vault encrypt group_vars/all/vault.yml

# Edit encrypted files
ansible-vault edit group_vars/all/vault.yml

# View encrypted files
ansible-vault view group_vars/all/vault.yml

# Decrypt temporarily (use with caution)
ansible-vault decrypt group_vars/all/vault.yml
```

**Vault File Contents:**
```yaml
# Encrypted vault variables
vault_proxmox_api_url: "https://proxmox:8006/api2/json"
vault_proxmox_username: "root@pam"
vault_proxmox_token_name: "ansible-automation"
vault_proxmox_token_value: "actual-token-value"

vault_ssh_public_key: "ssh-ed25519 AAAA... key"
vault_ssh_private_key: "-----BEGIN OPENSSH PRIVATE KEY-----..."

# Additional secrets
vault_grafana_admin_password: "secure-password"
vault_monitoring_api_key: "api-key"
```

**Vault Security:**
- Use strong, unique passwords for vault files
- Store vault passwords securely (password managers)
- Implement vault password rotation
- Use multiple vault files for different environments
- Never commit vault passwords to version control

### Environment Variables

**Secure Environment Management:**
```bash
# Use environment files with restricted permissions
chmod 600 .env
chmod 600 .env.production

# Load environment securely
source .env

# Clear sensitive environment variables
unset PROXMOX_TOKEN_VALUE
```

## 🌐 Network Security

### Firewall Configuration

**Default UFW Rules:**
```bash
# Default policies
ufw default deny incoming
ufw default allow outgoing

# Allow SSH
ufw allow ssh

# Allow HTTP/HTTPS (if needed)
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw --force enable
```

**Network Segmentation:**
- Isolate management networks from production
- Use VPN for remote access
- Implement network monitoring
- Regular security audits

### Proxmox Network Security

**Bridge Configuration:**
```bash
# Secure bridge configuration
auto vmbr0
iface vmbr0 inet static
    address 192.168.1.1/24
    bridge_ports eno1
    bridge_stp off
    bridge_fd 0
```

**VM Network Isolation:**
- Use separate VLANs for different VM types
- Implement network policies
- Monitor network traffic
- Regular network security assessments

## 👥 Access Control

### User Management

**Ansible Control Node:**
```bash
# Create dedicated automation user
useradd -m -s /bin/bash ansible
usermod -aG sudo ansible

# Disable password authentication
passwd -l ansible

# Configure sudo access
echo "ansible ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/ansible
```

**Proxmox User Management:**
- Create dedicated automation users
- Use role-based access control (RBAC)
- Implement user account expiration
- Regular user access reviews

### File Permissions

**Directory Permissions:**
```bash
# Ansible directories
chmod 755 ~/infra
chmod 755 ~/infra/ansible
chmod 700 ~/.ansible
chmod 600 ~/.ansible/vault_pass

# SSH directories
chmod 700 ~/.ssh
chmod 600 ~/.ssh/config
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub

# Log directories
chmod 755 ~/infra/logs
```

## 📊 Monitoring & Auditing

### Log Management

**Log Files:**
```bash
# Ansible logs
~/infra/logs/ansible.log

# Proxmox API logs
~/infra/logs/proxmox-*.log

# System logs
/var/log/auth.log
/var/log/syslog
```

**Log Rotation:**
```bash
# Configure logrotate
cat > /etc/logrotate.d/ansible-automation << EOF
~/infra/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ansible ansible
}
EOF
```

### Security Monitoring

**Audit Trail:**
- Log all Proxmox API calls
- Monitor SSH access attempts
- Track Ansible playbook executions
- Alert on security events

**Monitoring Tools:**
```bash
# SSH monitoring
grep "Failed password" /var/log/auth.log

# Ansible execution monitoring
tail -f ~/infra/logs/ansible.log

# Proxmox API monitoring
grep "POST\|PUT\|DELETE" ~/infra/logs/proxmox-*.log
```

## 🔄 Security Maintenance

### Regular Security Tasks

**Daily:**
- Review authentication logs
- Check for failed login attempts
- Monitor system resource usage

**Weekly:**
- Review Ansible execution logs
- Check vault file access
- Update security patches

**Monthly:**
- Rotate API tokens
- Review user access permissions
- Security configuration audit

**Quarterly:**
- Comprehensive security review
- Penetration testing
- Disaster recovery testing

### Patch Management

**System Updates:**
```bash
# Update Ansible control node
sudo apt update && sudo apt upgrade -y

# Update Ansible collections
ansible-galaxy collection install -r requirements.yml --force

# Update Python packages
pip install --user --upgrade ansible proxmoxer
```

**Proxmox Updates:**
- Monitor Proxmox security advisories
- Plan maintenance windows for updates
- Test updates in development environment
- Document update procedures

## 🚨 Incident Response

### Security Incident Procedures

**Detection:**
1. Monitor security logs
2. Set up alerting for suspicious activity
3. Regular security scans

**Response:**
1. Isolate affected systems
2. Preserve evidence
3. Document incident details
4. Notify relevant stakeholders

**Recovery:**
1. Remove threats
2. Restore from clean backups
3. Update security measures
4. Post-incident review

### Backup & Recovery

**Backup Strategy:**
```bash
# Backup Ansible configurations
tar -czf ansible-backup-$(date +%Y%m%d).tar.gz ~/infra/

# Backup SSH keys (encrypted)
gpg --symmetric ~/.ssh/id_ed25519

# Backup vault files
cp group_vars/all/vault.yml vault-backup-$(date +%Y%m%d).yml
```

**Recovery Procedures:**
1. Restore from clean backups
2. Verify integrity of restored files
3. Update credentials if compromised
4. Test automation functionality

## 📋 Security Checklist

### Pre-Deployment
- [ ] API tokens configured with least privilege
- [ ] SSH keys generated and distributed
- [ ] Vault files encrypted
- [ ] Firewall rules configured
- [ ] User accounts secured

### Post-Deployment
- [ ] Security monitoring enabled
- [ ] Log rotation configured
- [ ] Backup procedures tested
- [ ] Incident response plan documented
- [ ] Security training completed

### Ongoing
- [ ] Regular security reviews
- [ ] Patch management process
- [ ] Access control audits
- [ ] Security testing
- [ ] Documentation updates

## 🔗 Additional Resources

- [Proxmox Security Hardening](https://pve.proxmox.com/wiki/Security_Model)
- [Ansible Security Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)
- [SSH Security Guidelines](https://infosec.mozilla.org/guidelines/openssh)
- [OWASP Security Guidelines](https://owasp.org/www-project-top-ten/)

---

**Remember**: Security is an ongoing process, not a one-time setup. Regular reviews, updates, and testing are essential for maintaining a secure automation environment.
