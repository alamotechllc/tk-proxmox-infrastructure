# OPNsense API Setup Guide

## 🔍 **Current Status**

**✅ API Credentials**: Successfully extracted and stored  
**✅ Network Connectivity**: OPNsense (172.23.5.1) is reachable  
**⚠️ API Endpoints**: Need proper configuration  

## 🔧 **API Setup Steps**

### **Step 1: Enable OPNsense API**

1. **Access OPNsense Web UI**: https://172.23.5.1
2. **Login** with your admin credentials
3. **Navigate to**: System → Settings → API
4. **Enable API**: Check "Enable API"
5. **Configure Settings**:
   - **API Enabled**: ✅ Checked
   - **API Key**: Your existing key is already generated
   - **Permissions**: Ensure proper permissions are set

### **Step 2: Verify API Permissions**

Your API key should have these permissions:
- `core/firmware` (read-only)
- `core/interface` (read/write)
- `core/firewall` (read/write)
- `core/dhcp` (read/write)
- `core/dns` (read-only)

### **Step 3: Test API with Correct Format**

The OPNsense API might require a different format. Try these commands:

```bash
# Test with different API formats
curl -k -u "API_KEY:API_SECRET" https://172.23.5.1/api/core/system/info
curl -k -u "API_KEY:API_SECRET" https://172.23.5.1/api/system/info
curl -k -u "API_KEY:API_SECRET" https://172.23.5.1/api/core/system/info/
```

## 🚀 **Alternative Integration Approach**

Since the API endpoints are not responding as expected, let's use **SSH-based automation** as the primary method:

### **SSH Integration Benefits**
- ✅ **Full Access**: Complete system control
- ✅ **Reliable**: Direct command execution
- ✅ **Flexible**: Any configuration possible
- ✅ **Immediate**: No API endpoint discovery needed

### **SSH Setup Steps**

1. **Enable SSH in OPNsense**:
   - System → Settings → Admin Access
   - Enable SSH
   - Create dedicated user for automation

2. **Create Automation User**:
   - Username: `ansible-automation`
   - Password: Generate secure password
   - Groups: `wheel` (for sudo access)

3. **Configure SSH Key Authentication**:
   ```bash
   # Generate SSH key for OPNsense
   ssh-keygen -t ed25519 -f ~/.ssh/opnsense_automation
   
   # Copy public key to OPNsense
   ssh-copy-id -i ~/.ssh/opnsense_automation.pub ansible-automation@172.23.5.1
   ```

## 📋 **Updated Integration Plan**

### **Primary Method: SSH Automation**
- **Firewall Rules**: Use `pfctl` commands
- **Interface Management**: Use `ifconfig` commands
- **DHCP Management**: Use `dhcpd` configuration files
- **System Monitoring**: Use standard Unix commands

### **Secondary Method: API (When Working)**
- **Future Enhancement**: Once API endpoints are properly configured
- **Hybrid Approach**: Use API where available, SSH for everything else

## 🔧 **SSH-Based Automation Commands**

### **Firewall Management**
```bash
# List firewall rules
ssh ansible-automation@172.23.5.1 "pfctl -sr"

# Add firewall rule
ssh ansible-automation@172.23.5.1 "pfctl -f /dev/stdin <<< 'pass in on em0 from 172.23.3.0/24 to any'"

# Reload firewall
ssh ansible-automation@172.23.5.1 "pfctl -f /etc/pf.conf"
```

### **Interface Management**
```bash
# List interfaces
ssh ansible-automation@172.23.5.1 "ifconfig"

# Interface statistics
ssh ansible-automation@172.23.5.1 "ifconfig em0"
```

### **DHCP Management**
```bash
# List DHCP leases
ssh ansible-automation@172.23.5.1 "cat /var/dhcpd/var/db/dhcpd.leases"

# Restart DHCP service
ssh ansible-automation@172.23.5.1 "service dhcpd restart"
```

## 🎯 **Next Steps**

### **Immediate Actions**
1. **Enable SSH** in OPNsense Web UI
2. **Create automation user** with appropriate permissions
3. **Configure SSH key authentication**
4. **Test SSH connectivity**

### **Development Actions**
1. **Update Ansible playbooks** to use SSH instead of API
2. **Create SSH-based Semaphore templates**
3. **Test automation workflows**
4. **Document SSH commands and procedures**

### **Future Enhancements**
1. **Troubleshoot API endpoints** with OPNsense support
2. **Implement hybrid API/SSH approach** when API is working
3. **Add comprehensive monitoring** and alerting

## 🔒 **Security Considerations**

### **SSH Security**
- **Key-based authentication** only
- **Limited user permissions** for automation
- **Network restrictions** (management VLAN only)
- **Audit logging** of all SSH access

### **Access Control**
- **Dedicated automation user** (not root)
- **Specific command permissions** via sudoers
- **Regular key rotation** schedule
- **Monitoring and alerting** for unauthorized access

---

## 📞 **Support and Troubleshooting**

### **API Issues**
- Check OPNsense API documentation
- Verify API permissions and settings
- Review OPNsense system logs
- Contact OPNsense community support

### **SSH Issues**
- Verify SSH service is running
- Check firewall rules for SSH access
- Validate user permissions and sudoers
- Test key-based authentication

---

**Current Recommendation: Proceed with SSH-based automation for immediate functionality, troubleshoot API integration in parallel.** 🚀
