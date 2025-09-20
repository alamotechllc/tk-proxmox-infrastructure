# 🔌 Safe VLAN Port Assignment Runbook

## 🎯 Overview

A secure, user-friendly runbook for assigning access ports to VLANs with comprehensive safety protections. This runbook **CANNOT** modify trunk ports, uplinks, or critical infrastructure connections.

## 🛡️ Safety Features

### **🚨 CRITICAL PROTECTIONS:**
- **❌ Trunk Port Protection**: Cannot modify any trunk ports
- **❌ Uplink Protection**: Critical uplinks are completely protected
- **❌ Inter-Switch Links**: Stack and aggregation links protected
- **✅ Access Ports Only**: Only access layer ports can be modified
- **✅ VLAN Validation**: Only approved VLANs can be assigned
- **✅ Pre-Change Backup**: Configuration backed up before any change
- **✅ Change Verification**: Post-change validation ensures success

### **🔒 Protected Infrastructure:**
```
NEVER MODIFIED BY THIS RUNBOOK:
• TenGigabitEthernet1/1/1-2    (Uplinks to core/aggregation)
• GigabitEthernet1/0/1-2       (Inter-switch links)
• Ethernet49/1-52/1            (Arista uplinks)
• Ethernet1/49-52              (Nexus uplinks)
• Any port with "trunk" in description
• Any port currently in trunk mode
```

## 🎮 Usage Methods

### **🚀 Method 1: Interactive Mode (Recommended)**
```bash
cd /Users/mike.turner/APP_Projects/tk-proxmox
./infra/scripts/assign_vlan_port.sh -i
```

**Interactive walkthrough:**
1. **Select Switch**: Choose from available switches
2. **Select VLAN**: Choose from approved VLANs
3. **Enter Port**: Specify the interface (e.g., GigabitEthernet1/0/10)
4. **Add Description**: Describe the port usage
5. **Confirm**: Review and confirm the change

### **🖥️ Method 2: Command Line**
```bash
# Basic VLAN assignment
./infra/scripts/assign_vlan_port.sh \
  -s catalyst-access-01 \
  -p GigabitEthernet1/0/10 \
  -v 20 \
  -d "John Smith Workstation"

# VoIP phone assignment
./infra/scripts/assign_vlan_port.sh \
  -s catalyst-access-01 \
  -p GigabitEthernet1/0/15 \
  -v 100 \
  -d "Conference Room Phone"

# Server port assignment
./infra/scripts/assign_vlan_port.sh \
  -s catalyst-access-01 \
  -p GigabitEthernet1/0/20 \
  -v 10 \
  -d "Web Server 03"
```

### **🔍 Method 3: Dry Run (Testing)**
```bash
# Test without making changes
./infra/scripts/assign_vlan_port.sh \
  -s catalyst-access-01 \
  -p GigabitEthernet1/0/25 \
  -v 30 \
  -d "Guest Kiosk" \
  -n
```

## 📋 Available Resources

### **🔌 Your Network Switches:**
| Hostname | IP Address | Model | Location | Safe Ports |
|----------|------------|-------|----------|------------|
| `catalyst-access-01` | 172.23.5.10 | C9300-48P | Floor 1 IDF | Gi1/0/3-48 |
| `catalyst-access-02` | 172.23.5.11 | C9300-24P | Floor 2 IDF | Gi1/0/3-24 |
| `nexus-agg-01` | 172.23.5.2 | N9K-C93180YC-EX | Agg Rack | Eth1/1-48 |
| `arista-core-01` | 172.23.5.1 | DCS-7280SR-48C6 | Core Rack | Eth1-48 |

### **🏷️ Approved VLANs:**
| VLAN ID | Name | Description | Use Case |
|---------|------|-------------|----------|
| **10** | SERVERS | Production Servers | Database, Web, App servers |
| **20** | WORKSTATIONS | User Workstations | Employee computers |
| **30** | GUEST | Guest Network | Visitor devices |
| **60** | IOT | IoT Devices | Smart devices, sensors |
| **100** | VOICE | VoIP Phones | IP phones, video conf |

## 🔧 Common Use Cases

### **👤 User Workstation Setup**
```bash
# New employee workstation
./infra/scripts/assign_vlan_port.sh \
  -s catalyst-access-01 \
  -p GigabitEthernet1/0/12 \
  -v 20 \
  -d "Sarah Johnson - Marketing"

# Developer workstation
./infra/scripts/assign_vlan_port.sh \
  -s catalyst-access-02 \
  -p GigabitEthernet1/0/8 \
  -v 20 \
  -d "Dev Team - Linux Workstation"
```

### **📞 VoIP Phone Setup**
```bash
# Conference room phone
./infra/scripts/assign_vlan_port.sh \
  -s catalyst-access-01 \
  -p GigabitEthernet1/0/24 \
  -v 100 \
  -d "Main Conference Room Phone"

# Reception desk phone
./infra/scripts/assign_vlan_port.sh \
  -s catalyst-access-01 \
  -p GigabitEthernet1/0/5 \
  -v 100 \
  -d "Reception Desk Phone"
```

### **🖥️ Server Connections**
```bash
# New server connection
./infra/scripts/assign_vlan_port.sh \
  -s catalyst-access-01 \
  -p GigabitEthernet1/0/30 \
  -v 10 \
  -d "Application Server 04"

# Backup server
./infra/scripts/assign_vlan_port.sh \
  -s catalyst-access-02 \
  -p GigabitEthernet1/0/18 \
  -v 10 \
  -d "Backup Server - Secondary"
```

### **🌐 Guest and IoT Devices**
```bash
# Guest kiosk
./infra/scripts/assign_vlan_port.sh \
  -s catalyst-access-01 \
  -p GigabitEthernet1/0/35 \
  -v 30 \
  -d "Lobby Guest Kiosk"

# IoT sensor
./infra/scripts/assign_vlan_port.sh \
  -s catalyst-access-02 \
  -p GigabitEthernet1/0/22 \
  -v 60 \
  -d "Temperature Sensor - Server Room"
```

## 🔍 Verification & Monitoring

### **📊 Change Tracking**
Every port assignment creates:
- **Pre-change backup**: Full interface configuration before change
- **Change report**: Detailed operation log with before/after states
- **Verification results**: Post-change validation data
- **Audit trail**: Complete record for compliance

### **📁 File Locations**
```
/tmp/network_changes/
├── catalyst-access-01_GigabitEthernet1_0_10_pre_change_[timestamp].cfg
├── catalyst-access-01_GigabitEthernet1_0_10_change_[timestamp].log
├── nexus-agg-01_Ethernet1_15_pre_change_[timestamp].cfg
└── nexus-agg-01_Ethernet1_15_change_[timestamp].log
```

### **🔧 Verification Commands**
After any change, verify with:
```bash
# SSH to the switch
ssh admin@172.23.5.10  # Catalyst
ssh admin@172.23.5.2   # Nexus  
ssh admin@172.23.5.1   # Arista

# Check port status
show interface GigabitEthernet1/0/10 switchport
show interface GigabitEthernet1/0/10 status
show vlan id 20
```

## 🚨 Error Handling

### **Common Safety Blocks:**

#### **🛑 Trunk Port Protection**
```
🚨 TRUNK PORT PROTECTION ACTIVATED!

Port GigabitEthernet1/0/1 is currently configured as a trunk port.
This runbook is designed for ACCESS PORTS ONLY.
```

#### **🛑 Critical Uplink Protection**
```
🚨 CRITICAL UPLINK PROTECTION ACTIVATED!

Port TenGigabitEthernet1/1/1 is identified as a critical uplink port.
These ports connect to core infrastructure and should NEVER be modified.
```

#### **🛑 Invalid VLAN**
```
🚨 INVALID VLAN DETECTED!

VLAN 999 is not in the approved VLAN list.
Contact network team to add new VLANs.
```

### **🔧 Troubleshooting**
```bash
# Check switch connectivity
ansible catalyst-access-01 -i inventories/prod/hosts.yml -m ping

# Test credentials
ssh admin@172.23.5.10

# View recent changes
ls -la /tmp/network_changes/

# Check change logs
cat /tmp/network_changes/*_change_*.log
```

## 🎯 Operational Workflows

### **📋 New Employee Setup**
1. **Identify Requirements**: Department, location, device type
2. **Select Switch**: Based on physical location
3. **Choose VLAN**: Based on department/role
4. **Find Available Port**: Use safe port ranges
5. **Execute Assignment**: Use interactive mode
6. **Verify Connection**: Test device connectivity
7. **Document**: Update network documentation

### **📞 VoIP Phone Deployment**
1. **Plan Installation**: Phone location and extension
2. **Verify PoE**: Ensure switch port supports PoE
3. **Assign VLAN 100**: Use voice VLAN
4. **Configure Phone**: Set VLAN tagging if needed
5. **Test Connectivity**: Verify phone registration
6. **Update Directory**: Add to phone system

### **🖥️ Server Connection**
1. **Server Requirements**: Bandwidth, redundancy needs
2. **Select Appropriate Switch**: Based on server location
3. **Assign Server VLAN**: Usually VLAN 10
4. **Configure NIC**: Set server network configuration
5. **Test Connectivity**: Verify server communication
6. **Monitor Performance**: Check interface utilization

## 📚 Advanced Operations

### **🔄 Bulk Port Assignment**
For multiple ports, create a CSV file and use:
```bash
# Example CSV: hostname,port,vlan,description
# catalyst-access-01,GigabitEthernet1/0/10,20,John Workstation
# catalyst-access-01,GigabitEthernet1/0/11,20,Jane Workstation

# Process CSV file (custom script)
while IFS=, read -r switch port vlan desc; do
    ./infra/scripts/assign_vlan_port.sh -s "$switch" -p "$port" -v "$vlan" -d "$desc"
done < port_assignments.csv
```

### **📊 Port Audit**
```bash
# Generate port usage report
ansible-playbook playbooks/network/port_audit.yml
```

## 🔐 Security & Compliance

### **✅ Change Control**
- **Pre-approval**: VLAN assignments require approved VLAN list
- **Documentation**: Every change is logged and tracked
- **Rollback**: Pre-change backups enable quick rollback
- **Verification**: Post-change validation ensures correctness

### **✅ Audit Trail**
- **Who**: Operator identification in logs
- **What**: Detailed configuration changes
- **When**: Precise timestamps
- **Why**: Port descriptions and business justification
- **How**: Complete command history

### **✅ Risk Mitigation**
- **Network Isolation**: Cannot break critical infrastructure
- **Change Validation**: Multiple verification steps
- **Automated Backup**: No manual backup steps required
- **Error Recovery**: Clear rollback procedures

---

## 🎉 **Safe VLAN Port Assignment Runbook Complete!**

### **🚀 Quick Start:**
```bash
# Interactive mode (easiest)
./infra/scripts/assign_vlan_port.sh -i

# Direct assignment
./infra/scripts/assign_vlan_port.sh -s catalyst-access-01 -p GigabitEthernet1/0/10 -v 20 -d "New User"

# Test first (dry run)
./infra/scripts/assign_vlan_port.sh -s catalyst-access-01 -p GigabitEthernet1/0/10 -v 20 -n
```

### **🛡️ Safety Guarantees:**
- ✅ **Trunk ports are 100% protected**
- ✅ **Critical uplinks cannot be touched**
- ✅ **Only approved VLANs can be assigned**
- ✅ **Complete audit trail for all changes**
- ✅ **Automatic rollback capability**

### **📋 Your Network Setup:**
- **Arista Core**: Protected uplinks, access ports available
- **Nexus Aggregation**: Protected uplinks, access ports available  
- **Catalyst Access**: Protected uplinks, ports 3-48 available
- **OPNsense Firewall**: All VLAN gateways configured

**The runbook is production-ready and safe for daily network operations!** 🎉
