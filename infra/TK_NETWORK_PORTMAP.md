# TK Network Port Mapping Reference

## 🌐 Network Topology Overview

This document provides comprehensive port mapping for the TK network infrastructure based on the network diagram and current configuration.

## 🔥 OPNsense Firewall (tks-fw-opnsense-1)

**Management IP**: 172.23.7.1  
**Model**: OPNsense HA Firewall  
**Features**: Tailscale Jump Host + Subnet Router

### Interface Assignments

| Interface | VLAN | Network | Description |
|-----------|------|---------|-------------|
| WAN | - | Internet | ISP connection |
| LAN | 7 | 172.23.7.0/24 | Management network |
| OPT1 | 2 | 172.23.2.0/24 | Server infrastructure |
| OPT2 | 3 | 172.23.3.0/24 | User workstations |
| OPT3 | 4 | 172.23.4.0/24 | Guest network |
| OPT4 | 5 | 172.23.5.0/24 | IoT devices |
| OPT5 | 6 | 172.23.6.0/24 | Gaming & entertainment |

### Services Configuration

- **DHCP Server**: All VLANs (2-7)
- **DNS Server**: Primary for all VLANs
- **Firewall Rules**: Inter-VLAN routing control
- **Tailscale**: Remote access and subnet routing
- **Gateway**: Default gateway for all VLANs

## 🔄 Arista Core Switch (tks-sw-arista-core-1)

**Management IP**: 172.23.7.10  
**Model**: DCS-7050T-64  
**Management VLAN**: 7

### Port Channel Configuration

| Port Channel | Members | Destination | Protocol | VLANs |
|--------------|---------|-------------|----------|-------|
| Po1 | Multiple ports | Cisco Nexus | LACP | 2-7 (Trunk) |
| Po2 | Multiple ports | OPNsense | LACP | 2-7 (Trunk) |

### High-Speed Port Assignments

| Port | Speed | Destination | VLAN/Type | Status |
|------|-------|-------------|-----------|---------|
| Ethernet49/1 | 10GbE | Core uplink | Trunk | Protected |
| Ethernet50/1 | 10GbE | Core uplink | Trunk | Protected |
| Ethernet1-48 | 1GbE | Various | Mixed | Available |

### Direct Connect Assignments (From Diagram)

| Port | Device | Connection Type | VLAN |
|------|--------|-----------------|------|
| Multiple | TSKI-Server | 1x40GbE Direct | 2 |
| Multiple | TrueNAS Personal | 2x40GbE Direct | 2 |
| Multiple | Game Server | 10GbE Direct | 2 |
| Multiple | 8x10gbe Node Server | 8x10GbE | 2 |
| Multiple | Intel Proxmox | 10GbE Direct | 2 |
| Multiple | Monitor | Direct | 3 |

## 🔌 Cisco Nexus Access Switch (tks-sw-cis-nexus-1)

**Management IP**: 210.141.77.15  
**Model**: Cisco Nexus NX-OS 9.3(8)  
**Management VLAN**: 99 (VRF 192.6.15.1)

### Trunk Port Configuration

| Port | Destination | VLANs | Purpose |
|------|-------------|-------|---------|
| Ethernet1/50 | Proxmox | 2-7 | Server virtualization trunk |
| Ethernet1/52 | TrueNAS | 2-7 | Storage system trunk |

### Port Channel Configuration

| Port Channel | Members | Destination | Protocol |
|--------------|---------|-------------|----------|
| port-channel1 | Multiple | Arista Po1 | LACP |

### Access Port Assignments

| Port Range | VLAN | Description | Device Types |
|------------|------|-------------|--------------|
| Ethernet1/18-46 | 6 | Gaming/Entertainment | Gaming consoles, entertainment systems |
| Ethernet1/1-17 | Various | Mixed access | Workstations, IoT, etc. |
| Ethernet1/47-48 | Management | Infrastructure | Management devices |

## 📍 Access Layer Port Mapping

### Office 8-Port Switch (1GbE)

Connected to Arista core switch via uplink

| Port | Device | VLAN | MAC/IP | Notes |
|------|--------|------|--------|-------|
| 1 | Desktop Main Backup | 3 | 172.23.3.11 | Backup workstation |
| 2 | Mac Studio | 3 | 172.23.3.10 | Primary workstation |
| 3 | Office Comms | 3 | 172.23.3.20 | Communications equipment |
| 4 | Office AP | 5 | 172.23.5.50 | Wireless access point |
| 5 | Xbox | 6 | 172.23.6.11 | Gaming console |
| 6 | Switch Console | 6 | 172.23.6.13 | Nintendo Switch |
| 7 | Available | - | - | Expansion port |
| 8 | **Uplink** | Trunk | - | **Connection to Arista** |

### Living Room 8-Port Switch (1GbE)

Connected to Arista core switch via uplink

| Port | Device | VLAN | MAC/IP | Notes |
|------|--------|------|--------|-------|
| 1 | PlayStation | 6 | 172.23.6.10 | Gaming console |
| 2 | Xbox | 6 | 172.23.6.11 | Gaming console |
| 3 | Switch Console | 6 | 172.23.6.13 | Nintendo Switch |
| 4 | Audio Receiver | 6 | 172.23.6.20 | Entertainment system |
| 5 | Steam Link | 6 | 172.23.6.12 | Streaming device |
| 6 | Available | - | - | Expansion port |
| 7 | Available | - | - | Expansion port |
| 8 | **Uplink** | Trunk | - | **Connection to Arista** |

### PoE Switch (2x1GbE PoE 10-Port)

Connected to Arista core switch

| Port | Device | VLAN | Power | Notes |
|------|--------|------|-------|-------|
| 1 | Garage Camera | 5 | PoE | IP security camera |
| 2 | Side Camera | 5 | PoE | IP security camera |
| 3 | Downstairs AP | 5 | PoE+ | Wireless access point |
| 4 | Upstairs AP | 5 | PoE+ | Wireless access point |
| 5 | SmartThings Hub | 5 | PoE | IoT hub |
| 6 | Smart Panels | 5 | PoE | Wall control panels |
| 7 | PoE Light Switches | 5 | PoE | Smart lighting |
| 8 | Garage Doors | 5 | PoE | Garage door controllers |
| 9 | Available | 5 | PoE | Expansion |
| 10 | **Uplink** | Trunk | - | **Connection to Arista** |

## 🖥️ Server Infrastructure Port Mapping

### High-Speed Server Connections

| Server | Connection | Speed | Ports | VLAN | IP Range |
|--------|------------|-------|-------|------|----------|
| TSKI-Server | Direct to Arista | 40GbE | 1x40G | 2 | 172.23.2.30 |
| TrueNAS Personal | Direct to Arista | 40GbE | 2x40G | 2 | 172.23.2.21 |
| 8x10gbe Node Server | Direct to Arista | 10GbE | 8x10G | 2 | 172.23.2.32 |
| Game Server | Direct to Arista | 10GbE | 1x10G | 2 | 172.23.2.31 |
| Intel Proxmox | Direct to Arista | 10GbE | 1x10G | 2 | 172.23.2.11 |

### Virtualization Infrastructure

| Host | Connection | VLANs | Trunk Ports | Management |
|------|------------|-------|-------------|------------|
| Epyc Proxmox | Nexus Eth1/50 | 2-7 | Trunk | 172.23.2.10 |
| TrueNAS Corp | Nexus Eth1/52 | 2-7 | Trunk | 172.23.2.20 |

## 🔒 Protected Ports

### Critical Infrastructure Ports (DO NOT MODIFY)

**Arista Core Switch:**
- `Ethernet49/1` - Core uplink
- `Ethernet50/1` - Core uplink
- `Management1` - Management interface

**Cisco Nexus:**
- `Ethernet1/50` - Proxmox trunk
- `Ethernet1/52` - TrueNAS trunk
- `port-channel1` - LAG to Arista
- `mgmt0` - Management interface

**OPNsense:**
- `WAN` - Internet connection
- `LAN` - Primary LAN interface

## 📊 VLAN Assignments by Device Type

### VLAN 2 (SERVERS) - 172.23.2.0/24
- **Gateway**: 172.23.2.1 (OPNsense)
- **Devices**: Proxmox hosts, TrueNAS, application servers
- **Ports**: High-speed direct connections and trunks

### VLAN 3 (WORKSTATIONS) - 172.23.3.0/24
- **Gateway**: 172.23.3.1 (OPNsense)
- **Devices**: Mac Studio, desktop systems, office equipment
- **Ports**: Access ports on office switches

### VLAN 4 (GUEST) - 172.23.4.0/24
- **Gateway**: 172.23.4.1 (OPNsense)
- **Devices**: Guest devices
- **Isolation**: Limited inter-VLAN access

### VLAN 5 (IOT) - 172.23.5.0/24
- **Gateway**: 172.23.5.1 (OPNsense)
- **Devices**: APs, cameras, smart home devices
- **Ports**: PoE switch ports, IoT-specific connections

### VLAN 6 (GAMING) - 172.23.6.0/24
- **Gateway**: 172.23.6.1 (OPNsense)
- **Devices**: Gaming consoles, entertainment systems
- **Ports**: Access ports Ethernet1/18-46 on Nexus

### VLAN 7 (MANAGEMENT) - 172.23.7.0/24
- **Gateway**: 172.23.7.1 (OPNsense)
- **Devices**: Network device management, monitoring
- **Access**: Restricted to administrators

## 🔧 Port Management Commands

### Arista EOS Commands

```bash
# Show port status
show interfaces status

# Configure access port
interface Ethernet1/10
 description User Workstation
 switchport mode access
 switchport access vlan 3
 spanning-tree portfast
 no shutdown

# Configure trunk port
interface Ethernet1/48
 description Uplink to Access Switch
 switchport mode trunk
 switchport trunk allowed vlan 2-7
 no shutdown
```

### Cisco Nexus Commands

```bash
# Show port status
show interface status

# Configure access port
interface Ethernet1/20
 description Gaming Console
 switchport mode access
 switchport access vlan 6
 spanning-tree port type edge
 no shutdown

# Configure trunk port
interface Ethernet1/50
 description Trunk to Proxmox
 switchport mode trunk
 switchport trunk allowed vlan 2-7
 no shutdown
```

## 🛡️ Security Considerations

### Port Security

- **Protected Ports**: Uplinks and management interfaces
- **Access Control**: VLAN-based segmentation
- **Monitoring**: Port status and utilization tracking
- **Documentation**: All changes must be documented

### VLAN Security

- **Inter-VLAN Routing**: Controlled by OPNsense firewall rules
- **Guest Isolation**: VLAN 4 has restricted access
- **Management Access**: VLAN 7 restricted to administrators
- **IoT Segmentation**: VLAN 5 isolated from critical systems

## 📋 Maintenance Procedures

### Port Assignment Workflow

1. **Identify Requirements**: Device type, VLAN, location
2. **Check Port Availability**: Use port mapping documentation
3. **Validate VLAN Assignment**: Ensure appropriate VLAN for device type
4. **Configure Port**: Use appropriate commands for switch type
5. **Test Connectivity**: Verify device connectivity and VLAN assignment
6. **Document Changes**: Update port mapping documentation

### Port Troubleshooting

```bash
# Check port status
show interface [port] status

# Check VLAN assignment
show vlan brief
show interface [port] switchport

# Check port statistics
show interface [port] counters

# Check spanning tree
show spanning-tree interface [port]
```

## 🔍 Monitoring & Alerting

### Port Monitoring

- **Utilization**: Monitor bandwidth usage on critical ports
- **Status**: Track up/down status of all ports
- **Errors**: Monitor for CRC errors, collisions, drops
- **Security**: Monitor for unauthorized device connections

### Critical Port Alerts

- **Uplink Ports**: Immediate alert on failure
- **Server Trunks**: High priority monitoring
- **Management Interfaces**: Security monitoring
- **PoE Ports**: Power and connectivity monitoring

## 📊 Port Utilization Planning

### Current Utilization

**Arista Core Switch (64 ports)**:
- **Used**: ~20 ports (servers, uplinks, trunks)
- **Available**: ~44 ports for expansion
- **High-speed**: 10GbE and 40GbE connections

**Cisco Nexus (48 ports)**:
- **Used**: ~30 ports (gaming devices, workstations)
- **Available**: ~18 ports for expansion
- **Trunks**: 2 critical trunk connections

### Expansion Planning

- **Office Growth**: Additional workstation ports available
- **IoT Expansion**: PoE switch has capacity for more devices
- **Server Growth**: High-speed ports available on Arista
- **Gaming**: Additional gaming device ports available

## 🛠️ Ansible Automation Integration

### Port Management Templates

The following Semaphore templates can manage these ports:

- **VLAN Management**: Variable-based port VLAN assignment
- **Network Operations**: Comprehensive port operations
- **Network Health Check**: Port status monitoring
- **Network Backup**: Configuration backup including port configs

### Automation Variables

```yaml
# Port assignment variables
target_switch: tks-sw-arista-core-1
port_interface: Ethernet1/10
vlan_id: 3
port_description: "User Workstation"

# Bulk operations
port_range: "Ethernet1/1-24"
vlan_assignment: 6
operation_type: "bulk_assign"
```

## 📁 Reference Files

- **Network Diagram**: Original network topology
- **Inventory Files**: Semaphore inventories with device mappings
- **Template Files**: Ansible templates for port management
- **Documentation**: This port mapping reference

---

**Last Updated**: Based on network diagram analysis and current infrastructure configuration.  
**Maintained By**: TK Network Infrastructure Team  
**Review Schedule**: Monthly or after major network changes
