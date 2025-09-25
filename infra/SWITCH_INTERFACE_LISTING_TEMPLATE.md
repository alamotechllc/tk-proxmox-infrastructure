# Switch Interface Listing Template

## 🎯 Overview

The Switch Interface Listing Template provides a comprehensive view of all available interfaces on your network switches. This template helps users understand what ports are available, their current assignments, and which ports are safe to modify for VLAN assignments.

## 🚀 Key Features

### 📋 **Comprehensive Interface Information**
- **Available Access Ports**: Safe ports for VLAN assignment
- **Port Descriptions**: Current device assignments and availability
- **Protected Ports**: Uplinks, trunks, and management interfaces
- **Specialized Ports**: Gaming zones, high-speed ports, and PoE ports
- **VLAN Reference**: Complete list of available VLANs

### 🔧 **Switch-Specific Details**

#### **Arista Core Switch (tks-sw-arista-core-1)**
- **48 Access Ports**: Ethernet1/1 through Ethernet1/48
- **2 High-Speed Ports**: Ethernet49/1, Ethernet50/1 (10GbE - Protected)
- **Management Port**: Management1 (Protected)
- **Model**: DCS-7050T-64

#### **Cisco Nexus Switch (tks-sw-cis-nexus-1)**
- **48 Access Ports**: Ethernet1/1 through Ethernet1/48
- **Gaming Zone**: Ethernet1/18 through Ethernet1/46 (VLAN 6 recommended)
- **Trunk Ports**: Ethernet1/50 (Proxmox), Ethernet1/52 (TrueNAS)
- **Management**: mgmt0, port-channel1 (Protected)
- **Model**: N9K-C93180YC-EX

#### **Access Layer Switch (8-port)**
- **7 Access Ports**: GigabitEthernet0/1 through GigabitEthernet0/7
- **1 Uplink Port**: GigabitEthernet0/8 (Protected)
- **Current Assignments**: Office workstations, gaming consoles, IoT devices
- **Model**: 8-Port Gigabit Switch

## 📋 Template Configuration

### **Required Variables (Semaphore Extra Variables)**

| Variable | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `switch_name` | Multiple Choice | ✅ Yes | Target switch to query | `arista_core` |

### **Valid Switch Options**

| Value | Label | Description |
|-------|-------|-------------|
| `arista_core` | Arista Core Switch | Main core switch with 48 access ports |
| `cisco_nexus` | Cisco Nexus Switch | Access switch with gaming zone |
| `access_switch` | Access Layer Switch | 8-port office switch |

## 🎮 Usage Examples

### **Via Semaphore UI**

1. **Navigate to**: Templates → List Switch Interfaces
2. **Select Switch**: Choose from dropdown (arista_core, cisco_nexus, access_switch)
3. **Run Template**: Execute to see all available interfaces

### **Via Command Line**

```bash
# List Arista Core interfaces
ansible-playbook playbooks/network/list_switch_interfaces.yml \
  -e "switch_name=arista_core"

# List Cisco Nexus interfaces  
ansible-playbook playbooks/network/list_switch_interfaces.yml \
  -e "switch_name=cisco_nexus"

# List Access Switch interfaces
ansible-playbook playbooks/network/list_switch_interfaces.yml \
  -e "switch_name=access_switch"
```

## 📊 Sample Output

### **Arista Core Switch Example**
```
🔌 AVAILABLE ACCESS PORTS (Safe for VLAN Assignment)
===================================================
1. Ethernet1/1 - Available - Access Port
2. Ethernet1/2 - Available - Access Port
3. Ethernet1/3 - Available - Access Port
...
48. Ethernet1/48 - Available - Access Port

⚡ HIGH-SPEED PORTS (Arista Core - 10GbE)
=========================================
1. Ethernet49/1 (10GbE - Protected)
2. Ethernet50/1 (10GbE - Protected)

🛠️  MANAGEMENT PORTS (Protected - Do Not Modify)
===============================================
1. Management1 (Protected)
```

### **Access Switch Example**
```
🔌 AVAILABLE ACCESS PORTS (Safe for VLAN Assignment)
===================================================
1. GigabitEthernet0/1 - Office Workstation
2. GigabitEthernet0/2 - Mac Studio
3. GigabitEthernet0/3 - Office Communications
4. GigabitEthernet0/4 - Wireless Access Point
5. GigabitEthernet0/5 - Xbox Gaming Console
6. GigabitEthernet0/6 - Nintendo Switch
7. GigabitEthernet0/7 - Available - Access Port

🔗 UPLINK PORTS (Access Switch - Protected)
===========================================
1. GigabitEthernet0/8 (Uplink to Arista - Protected)
```

## 🏷️ VLAN Reference

| VLAN ID | Name | Description | Subnet |
|---------|------|-------------|---------|
| 2 | SERVERS | Server infrastructure | 172.23.2.0/24 |
| 3 | WORKSTATIONS | User workstations | 172.23.3.0/24 |
| 4 | GUEST | Guest network | 172.23.4.0/24 |
| 5 | IOT | IoT devices | 172.23.5.0/24 |
| 6 | GAMING | Gaming/entertainment | 172.23.6.0/24 |
| 7 | MANAGEMENT | Network management | 172.23.7.0/24 |

## 💡 Usage Recommendations

### **Port Selection Guidelines**

1. **Office Workstations**: Use VLAN 3 (WORKSTATIONS)
2. **Gaming Consoles**: Use VLAN 6 (GAMING) - especially on Cisco Nexus gaming zone
3. **IoT Devices**: Use VLAN 5 (IOT)
4. **Servers**: Use VLAN 2 (SERVERS)
5. **Guest Devices**: Use VLAN 4 (GUEST)

### **Switch-Specific Recommendations**

#### **Arista Core Switch**
- **High-density access**: 48 ports available
- **Server connections**: Use VLAN 2 for production servers
- **High-speed requirements**: Ethernet49/1 and Ethernet50/1 (10GbE)

#### **Cisco Nexus Switch**
- **Gaming zone**: Ports Ethernet1/18-46 optimized for gaming
- **Office workstations**: Ports Ethernet1/1-17 for regular office use
- **Server trunks**: Ethernet1/50 and Ethernet1/52 for virtualization

#### **Access Switch**
- **Small office**: 7 ports for local devices
- **Mixed usage**: Office equipment, gaming, and IoT devices
- **Port 7**: Available for new device connections

## 🔧 Integration with VLAN Assignment

This template works seamlessly with the **Switch-Specific VLAN Assignment** template:

1. **Run Interface Listing**: See available ports for your switch
2. **Note Port Names**: Copy exact interface names (e.g., `Ethernet1/10`)
3. **Run VLAN Assignment**: Use the port names in the VLAN assignment template
4. **Verify Results**: Check that the port was assigned correctly

### **Workflow Example**

```bash
# Step 1: List available interfaces
ansible-playbook list_switch_interfaces.yml -e "switch_name=arista_core"

# Step 2: Use port information for VLAN assignment
ansible-playbook switch_specific_vlan_assignment.yml \
  -e "switch_name=arista_core" \
  -e "port_interface=Ethernet1/10" \
  -e "vlan_id=3" \
  -e "port_desc=New Office Workstation"
```

## 🛡️ Safety Features

### **Protected Port Identification**
- **Uplink Ports**: Clearly marked as protected
- **Trunk Ports**: Server and core connections protected
- **Management Ports**: Network management interfaces protected
- **High-Speed Ports**: 10GbE connections marked appropriately

### **Port Status Information**
- **Available**: Ready for new device connections
- **Assigned**: Currently used by specific devices
- **Protected**: Cannot be modified (safety critical)

## 📁 Template Files

- **Playbook**: `infra/ansible/playbooks/network/list_switch_interfaces.yml`
- **Creation Script**: `infra/scripts/create_interface_listing_template.py`
- **Documentation**: `infra/SWITCH_INTERFACE_LISTING_TEMPLATE.md`

## 🎯 Benefits

✅ **User-Friendly**: Clear interface listings with descriptions  
✅ **Safety-First**: Protected ports clearly identified  
✅ **Comprehensive**: All port types and assignments shown  
✅ **Integrated**: Works seamlessly with VLAN assignment template  
✅ **Educational**: Helps users understand network topology  
✅ **Efficient**: Reduces errors in port selection  

## 🚀 Next Steps

1. **Create Semaphore Template**: Use the creation script to add to Semaphore UI
2. **Test Interface Listing**: Run for each switch type
3. **Use for VLAN Assignments**: Reference interface info when assigning VLANs
4. **Update Port Descriptions**: Keep interface assignments current
5. **Train Users**: Show team how to use interface listing before VLAN assignments

---

**The Switch Interface Listing Template makes network management safer and more user-friendly!** 🎉
