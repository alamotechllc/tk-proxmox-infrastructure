# OPNsense Integration Plan for TK-Proxmox Infrastructure

## 🎯 **Integration Strategy: API-First Approach**

### **Primary Method: OPNsense API**
- **Security**: API keys with granular permissions
- **Automation**: RESTful API for Ansible integration
- **Audit**: Comprehensive logging and change tracking
- **Scalability**: Easy to extend and maintain

### **Backup Method: SSH Access**
- **Emergency**: For API-unavailable scenarios
- **Advanced**: For complex configurations not covered by API
- **Limited**: Restricted to specific operations only

## 🔥 **OPNsense Current Configuration**

### **Device Details**
- **Hostname**: tks-fw-opnsense-1
- **Management IP**: 172.23.7.1
- **Model**: OPNsense HA Firewall
- **Features**: Tailscale Jump Host + Subnet Router

### **Interface Configuration**
| Interface | VLAN | Network | Description |
|-----------|------|---------|-------------|
| WAN | - | Internet | ISP connection |
| LAN | 7 | 172.23.7.0/24 | Management network |
| OPT1 | 2 | 172.23.2.0/24 | Server infrastructure |
| OPT2 | 3 | 172.23.3.0/24 | User workstations |
| OPT3 | 4 | 172.23.4.0/24 | Guest network |
| OPT4 | 5 | 172.23.5.0/24 | IoT devices |
| OPT5 | 6 | 172.23.6.0/24 | Gaming & entertainment |

### **Services**
- **DHCP Server**: All VLANs (2-7)
- **DNS Server**: Primary for all VLANs
- **Firewall Rules**: Inter-VLAN routing control
- **Tailscale**: Remote access and subnet routing
- **Gateway**: Default gateway for all VLANs

## 🔑 **API Integration Setup**

### **Step 1: Enable OPNsense API**

1. **Access OPNsense Web UI**: https://172.23.7.1
2. **Navigate to**: System → Settings → API
3. **Enable API**: Check "Enable API"
4. **Create API Key**:
   - **Name**: `TK-Proxmox-Automation`
   - **Permissions**: 
     - `core/firmware` (read-only)
     - `core/interface` (read/write)
     - `core/firewall` (read/write)
     - `core/dhcp` (read/write)
     - `core/dns` (read-only)
   - **IP Restrictions**: `172.23.7.0/24` (management network only)

### **Step 2: Test API Connectivity**

```bash
# Test API access
curl -k -u "api_key:api_secret" \
  https://172.23.7.1/api/core/interface/list

# Get system information
curl -k -u "api_key:api_secret" \
  https://172.23.7.1/api/core/system/info
```

### **Step 3: Ansible Integration**

Create OPNsense-specific Ansible playbooks:

```yaml
# opnsense_firewall_rules.yml
- name: Manage OPNsense Firewall Rules
  hosts: localhost
  gather_facts: false
  vars:
    opnsense_host: "172.23.7.1"
    opnsense_api_key: "{{ semaphore_opnsense_api_key }}"
    opnsense_api_secret: "{{ semaphore_opnsense_api_secret }}"
  
  tasks:
    - name: Get current firewall rules
      uri:
        url: "https://{{ opnsense_host }}/api/core/firewall/rule/list"
        method: GET
        user: "{{ opnsense_api_key }}"
        password: "{{ opnsense_api_secret }}"
        force_basic_auth: yes
        validate_certs: no
      register: firewall_rules
    
    - name: Display firewall rules
      debug:
        var: firewall_rules.json
```

## 🛡️ **SSH Integration (Backup Method)**

### **SSH Configuration**

1. **Enable SSH**: System → Settings → Admin Access
2. **Create Dedicated User**:
   - **Username**: `ansible-automation`
   - **Password**: Generate secure password
   - **Groups**: `wheel` (for sudo access)
   - **Shell**: `/bin/sh`
   - **Home Directory**: `/home/ansible-automation`

3. **Configure SSH Key**:
   ```bash
   # Generate SSH key for OPNsense
   ssh-keygen -t ed25519 -f ~/.ssh/opnsense_automation -C "opnsense@tk-proxmox"
   
   # Copy public key to OPNsense
   ssh-copy-id -i ~/.ssh/opnsense_automation.pub ansible-automation@172.23.7.1
   ```

### **SSH Commands for Automation**

```bash
# Get interface status
ssh ansible-automation@172.23.7.1 "ifconfig"

# Check firewall rules
ssh ansible-automation@172.23.7.1 "pfctl -sr"

# Get DHCP leases
ssh ansible-automation@172.23.7.1 "cat /var/dhcpd/var/db/dhcpd.leases"

# Check system status
ssh ansible-automation@172.23.7.1 "top -n 1"
```

## 📋 **Integration Use Cases**

### **Primary Automation Tasks**

1. **Firewall Rule Management**
   - Add/remove rules for new VLANs
   - Update inter-VLAN routing
   - Manage guest network restrictions

2. **DHCP Configuration**
   - Add DHCP pools for new VLANs
   - Update DHCP reservations
   - Monitor DHCP lease utilization

3. **Interface Monitoring**
   - Check interface status and statistics
   - Monitor bandwidth utilization
   - Alert on interface failures

4. **DNS Management**
   - Update DNS forwarders
   - Add custom DNS records
   - Monitor DNS resolution

### **Semaphore Template Integration**

Create OPNsense-specific Semaphore templates:

1. **OPNsense Firewall Management**
   - Survey variables: Rule action, source/destination, port
   - API-based rule creation/modification
   - Safety checks for critical rules

2. **OPNsense DHCP Management**
   - Survey variables: VLAN, IP range, lease time
   - DHCP pool configuration
   - Lease monitoring and reporting

3. **OPNsense Health Monitoring**
   - Interface status checks
   - System resource monitoring
   - Alert generation for issues

## 🔒 **Security Considerations**

### **API Security**
- **API Key Rotation**: Monthly rotation schedule
- **IP Restrictions**: Limit to management network
- **Permission Scope**: Minimal required permissions
- **Audit Logging**: Enable comprehensive logging

### **SSH Security**
- **Key-based Authentication**: No password authentication
- **User Restrictions**: Limited to automation tasks
- **Command Restrictions**: Use sudoers for specific commands
- **Network Restrictions**: SSH only from management VLAN

### **Network Security**
- **Management VLAN**: Isolate management traffic (VLAN 7)
- **VPN Access**: Use Tailscale for remote management
- **Firewall Rules**: Restrict management access
- **Monitoring**: Log all management access

## 🚀 **Implementation Timeline**

### **Phase 1: API Setup (Week 1)**
- Enable OPNsense API
- Create API keys with appropriate permissions
- Test API connectivity and basic operations
- Create initial Ansible playbooks

### **Phase 2: Ansible Integration (Week 2)**
- Develop comprehensive Ansible playbooks
- Create Semaphore templates for OPNsense
- Implement safety checks and validation
- Test automation workflows

### **Phase 3: SSH Backup (Week 3)**
- Configure SSH access for emergency scenarios
- Create SSH-based automation scripts
- Implement key-based authentication
- Test fallback procedures

### **Phase 4: Production Deployment (Week 4)**
- Deploy to production environment
- Train team on new automation tools
- Monitor and optimize performance
- Document operational procedures

## 📊 **Expected Benefits**

### **Operational Efficiency**
- **Automated Firewall Management**: Reduce manual rule creation time
- **Centralized Configuration**: Single point of management
- **Consistent Deployments**: Standardized configuration templates
- **Reduced Errors**: Automated validation and safety checks

### **Security Improvements**
- **Audit Trail**: Complete logging of all changes
- **Access Control**: Granular permissions and restrictions
- **Change Management**: Controlled and validated modifications
- **Compliance**: Automated compliance checking

### **Monitoring and Alerting**
- **Proactive Monitoring**: Early detection of issues
- **Automated Reporting**: Regular status and health reports
- **Integration**: Connect with existing monitoring systems
- **Alerting**: Real-time notifications for critical events

## 🔧 **Next Steps**

1. **Review and Approve Plan**: Validate approach with team
2. **Create API Keys**: Set up OPNsense API access
3. **Develop Playbooks**: Build Ansible automation
4. **Test Integration**: Validate with Semaphore templates
5. **Deploy to Production**: Roll out automation workflows

---

*OPNsense Integration Plan*  
*Date: September 26, 2025*  
*Status: Ready for Implementation* 🚀
