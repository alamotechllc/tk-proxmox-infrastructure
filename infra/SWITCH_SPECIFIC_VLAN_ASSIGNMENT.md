# Switch-Specific VLAN Assignment

## 🎯 Overview

Simplified VLAN assignment template designed specifically for your 3 network switches. This replaces the complex generic VLAN management with a straightforward, switch-specific approach.

## 🔌 Your 3 Switches

### 1. **Arista Core Switch** (`arista_core`)
- **Name**: tks-sw-arista-core-1
- **IP**: 172.23.7.10
- **Safe Ports**: Ethernet1-48 (access ports only)
- **Protected Ports**: Ethernet49/1, Ethernet50/1, Management1 (uplinks)

### 2. **Cisco Nexus Switch** (`cisco_nexus`)
- **Name**: tks-sw-cis-nexus-1
- **IP**: 210.141.77.15
- **Safe Ports**: Ethernet1/1-17, Ethernet1/18-46, Ethernet1/47-48
- **Protected Ports**: Ethernet1/50, Ethernet1/52, port-channel1, mgmt0 (trunks)

### 3. **Access Switch** (`access_switch`)
- **Name**: tks-sw-access-1
- **IP**: 172.23.7.20 (example - update with actual)
- **Safe Ports**: GigabitEthernet0/1-7 (access ports)
- **Protected Ports**: GigabitEthernet0/8 (uplink)

## 📋 VLAN Definitions

| VLAN ID | Name | Description | Subnet |
|---------|------|-------------|---------|
| 2 | SERVERS | Server infrastructure | 172.23.2.0/24 |
| 3 | WORKSTATIONS | User workstations | 172.23.3.0/24 |
| 4 | GUEST | Guest network | 172.23.4.0/24 |
| 5 | IOT | IoT devices | 172.23.5.0/24 |
| 6 | GAMING | Gaming/entertainment | 172.23.6.0/24 |
| 7 | MANAGEMENT | Network management | 172.23.7.0/24 |

## 🚀 Usage

### Via Semaphore UI

1. **Navigate to**: http://172.23.5.22:3000
2. **Go to**: Templates → Switch-Specific VLAN Assignment
3. **Fill in**:
   - `switch_name`: `arista_core`, `cisco_nexus`, or `access_switch`
   - `port_interface`: Port to configure (e.g., `Ethernet1/10`)
   - `vlan_id`: VLAN number (2-7)
   - `port_desc`: Description (optional)

### Via Command Line

```bash
# Arista Core Switch
./assign_vlan_simple.sh arista_core Ethernet1/10 3 "Office Workstation"

# Cisco Nexus Switch  
./assign_vlan_simple.sh cisco_nexus Ethernet1/20 6 "Gaming Console"

# Access Switch
./assign_vlan_simple.sh access_switch GigabitEthernet0/3 5 "IoT Device"
```

## 🔒 Safety Features

### Protected Ports
- **Arista**: Ethernet49/1, Ethernet50/1, Management1
- **Nexus**: Ethernet1/50, Ethernet1/52, port-channel1, mgmt0
- **Access**: GigabitEthernet0/8 (uplink)

### Validation
- ✅ Port must be in safe range for the switch
- ✅ VLAN must be approved (2-7)
- ✅ Protected ports cannot be modified
- ✅ One switch at a time (serial execution)

## 📝 Examples

### Office Workstation on Arista Core
```bash
./assign_vlan_simple.sh arista_core Ethernet1/15 3 "Mac Studio"
```

### Gaming Console on Nexus
```bash
./assign_vlan_simple.sh cisco_nexus Ethernet1/25 6 "Xbox Series X"
```

### IoT Device on Access Switch
```bash
./assign_vlan_simple.sh access_switch GigabitEthernet0/4 5 "Smart Home Hub"
```

## 🛠️ Configuration

### Switch-Specific Settings

Each switch has predefined configurations:

```yaml
switch_configs:
  arista_core:
    safe_ports: ["Ethernet1-48"]
    protected_ports: ["Ethernet49/1", "Ethernet50/1", "Management1"]
    
  cisco_nexus:
    safe_ports: ["Ethernet1/1-17", "Ethernet1/18-46", "Ethernet1/47-48"]
    protected_ports: ["Ethernet1/50", "Ethernet1/52", "port-channel1", "mgmt0"]
    
  access_switch:
    safe_ports: ["GigabitEthernet0/1-7"]
    protected_ports: ["GigabitEthernet0/8"]
```

## 🔧 Troubleshooting

### Common Issues

1. **Port not in safe range**
   - Check if port is in the safe_ports list for your switch
   - Verify port naming convention

2. **VLAN not approved**
   - Only VLANs 2-7 are allowed
   - Check VLAN definitions table

3. **Protected port error**
   - Cannot modify uplink or management ports
   - Use different port

### Validation Commands

```bash
# Check port status on Arista
show interfaces status

# Check port status on Nexus
show interface status

# Check VLAN assignments
show vlan brief
```

## 📊 Benefits

- **Simplified**: No complex variable logic
- **Safe**: Built-in protection for critical ports
- **Specific**: Tailored to your actual switches
- **Clear**: Easy to understand and maintain
- **Fast**: Direct port configuration

## 🎯 Next Steps

1. **Update Access Switch IP**: Replace `172.23.7.20` with actual IP
2. **Test Each Switch**: Verify connectivity and credentials
3. **Document Port Assignments**: Track what's connected where
4. **Create Port Map**: Visual reference for your network

---

**Ready to simplify your VLAN management!** 🎉

