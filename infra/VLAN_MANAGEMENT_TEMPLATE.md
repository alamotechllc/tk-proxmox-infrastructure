# VLAN Management Template

## 🎯 Overview

The VLAN Management Template provides variable-based VLAN operations on selected network switches with comprehensive safety validation and multi-vendor support.

## 🚀 Key Features

### 🛡️ **Safety & Validation**
- **Protected Port Validation**: Prevents modification of critical uplink ports
- **Approved VLAN Validation**: Only allows operations on pre-approved VLANs
- **Reserved VLAN Protection**: Protects system VLANs from modification
- **Operation Parameter Validation**: Ensures all required parameters are provided
- **Trunk VLAN Validation**: All trunk VLANs must be in approved list

### 🔧 **Supported Operations**
- **assign**: Assign port to access VLAN
- **create**: Create new VLAN
- **delete**: Delete VLAN (with safety checks)
- **port_enable**: Enable a network port
- **port_disable**: Disable a network port
- **trunk_add**: Add VLANs to trunk port
- **trunk_remove**: Remove VLANs from trunk port
- **show_config**: Display current configuration

### 🌐 **Multi-Vendor Support**
- **Arista EOS**: Complete command support
- **Cisco Nexus NX-OS**: Full feature compatibility
- **Cisco Catalyst IOS/IOS-XE**: Comprehensive support
- **Generic**: Basic operation support

## 📋 Template Configuration

### Required Variables (Semaphore Extra Variables)

| Variable | Description | Required For | Example |
|----------|-------------|--------------|---------|
| `vlan_operation` | Operation type | All | `assign`, `create`, `delete` |
| `target_switch` | Switch hostname/IP | All | `catalyst-access-01` |
| `port_interface` | Port interface name | Port operations | `GigabitEthernet1/0/10` |
| `vlan_id` | VLAN ID number | VLAN operations | `20` |
| `vlan_name` | VLAN name | VLAN creation | `WORKSTATIONS` |
| `port_description` | Port description | Port operations | `John Workstation` |
| `trunk_vlans` | Comma-separated VLANs | Trunk operations | `10,20,30` |

### Security Variables (Semaphore Secrets)

| Variable | Description | Source |
|----------|-------------|--------|
| `semaphore_admin_user` | Network admin username | Semaphore Secret |
| `semaphore_admin_password` | Network admin password | Semaphore Secret |
| `semaphore_enable_password` | Enable/privilege password | Semaphore Secret |

## 🔐 Approved VLANs

The template includes a comprehensive approved VLAN list:

| VLAN | Name | Description | Type |
|------|------|-------------|------|
| 10 | SERVERS | Production servers | production |
| 20 | WORKSTATIONS | User workstations | user |
| 30 | GUEST | Guest network | guest |
| 40 | DMZ | DMZ servers | production |
| 50 | SECURITY | Security systems | infrastructure |
| 60 | IOT | IoT devices | iot |
| 70 | PRINTERS | Network printers | infrastructure |
| 80 | WIRELESS | Wireless access points | infrastructure |
| 90 | CAMERAS | IP cameras | security |
| 100 | VOICE | VoIP phones | voice |
| 110 | BACKUP | Backup network | infrastructure |
| 120 | STORAGE | Storage network | infrastructure |
| 999 | QUARANTINE | Quarantine VLAN | security |

## 🛡️ Protected Ports

The following ports are protected from modification:

- **Core Uplinks**: `TenGigabitEthernet1/1/1`, `TenGigabitEthernet1/1/2`
- **Nexus Uplinks**: `TenGigE1/1/1`, `TenGigE1/1/2`
- **Management Ports**: `GigabitEthernet1/0/1`, `GigabitEthernet1/0/2`
- **Arista Uplinks**: `Ethernet1/49`, `Ethernet1/50`, `Ethernet49/1`, `Ethernet50/1`
- **Management Interfaces**: `mgmt0`, `Management1`

## 📚 Usage Examples

### Command Line Execution

```bash
# Assign port to VLAN
./infra/scripts/run_vlan_management.sh assign \
  --switch catalyst-access-01 \
  --port GigabitEthernet1/0/10 \
  --vlan 20 \
  --description "John Workstation"

# Create new VLAN
./infra/scripts/run_vlan_management.sh create \
  --switch arista-core-01 \
  --vlan 150 \
  --name "NEW_DEPT"

# Enable/disable port
./infra/scripts/run_vlan_management.sh port_enable \
  --switch nexus-agg-01 \
  --port Ethernet1/10

# Trunk management
./infra/scripts/run_vlan_management.sh trunk_add \
  --switch catalyst-access-01 \
  --port GigabitEthernet1/0/48 \
  --trunk-vlans "10,20,30"

# Show configuration
./infra/scripts/run_vlan_management.sh show_config \
  --switch arista-core-01 \
  --port Ethernet1/1

# Dry run
./infra/scripts/run_vlan_management.sh assign \
  --switch catalyst-access-01 \
  --port GigabitEthernet1/0/10 \
  --vlan 20 \
  --dry-run
```

### Semaphore Template Configuration

**Template Settings:**
- **Name**: `VLAN Management`
- **Playbook**: `playbooks/network/vlan_management_template.yml`
- **Inventory**: Core Network Infrastructure
- **Repository**: Local

**Extra Variables Examples:**

```yaml
# Port VLAN Assignment
vlan_operation: assign
target_switch: catalyst-access-01
port_interface: GigabitEthernet1/0/10
vlan_id: 20
port_description: "User Workstation"

# VLAN Creation
vlan_operation: create
target_switch: arista-core-01
vlan_id: 150
vlan_name: "NEW_DEPARTMENT"

# Port Control
vlan_operation: port_enable
target_switch: nexus-agg-01
port_interface: Ethernet1/15

# Trunk Management
vlan_operation: trunk_add
target_switch: catalyst-access-01
port_interface: GigabitEthernet1/0/48
trunk_vlans: "10,20,30,100"
```

## 🔍 Operation Details

### Port VLAN Assignment (`assign`)

**Purpose**: Assign a port to an access VLAN
**Required Variables**: `target_switch`, `port_interface`, `vlan_id`
**Optional Variables**: `port_description`

**Safety Checks**:
- Port must not be in protected ports list
- VLAN must be in approved VLANs list
- All required parameters must be provided

**Generated Commands** (Cisco IOS example):
```
interface GigabitEthernet1/0/10
description User Workstation
switchport mode access
switchport access vlan 20
spanning-tree portfast
no shutdown
```

### VLAN Creation (`create`)

**Purpose**: Create a new VLAN on the switch
**Required Variables**: `target_switch`, `vlan_id`, `vlan_name`

**Safety Checks**:
- VLAN ID must not be reserved (1, 1002-1005)
- VLAN ID must be in valid range (2-4094)

**Generated Commands** (Cisco IOS example):
```
vlan 150
name NEW_DEPARTMENT
exit
```

### Port Control (`port_enable`, `port_disable`)

**Purpose**: Enable or disable a network port
**Required Variables**: `target_switch`, `port_interface`

**Safety Checks**:
- Port must not be in protected ports list (for disable operations)

**Generated Commands**:
```
interface GigabitEthernet1/0/10
no shutdown  # for enable
shutdown     # for disable
```

### Trunk Management (`trunk_add`, `trunk_remove`)

**Purpose**: Add or remove VLANs from trunk ports
**Required Variables**: `target_switch`, `port_interface`, `trunk_vlans`

**Safety Checks**:
- Port must not be in protected ports list
- All VLANs must be in approved VLANs list

**Generated Commands**:
```
interface GigabitEthernet1/0/48
switchport mode trunk
switchport trunk allowed vlan add 10,20,30  # for add
switchport trunk allowed vlan remove 30     # for remove
```

## 📊 Reporting & Logging

The template generates comprehensive reports for each operation:

**Report Location**: `/tmp/vlan_operations/`
**Report Format**: `{switch}_{operation}_{timestamp}.log`

**Report Contents**:
- Operation details and parameters
- Security validation results
- Commands that would be executed
- Execution status and results
- Audit trail information

## 🔧 Customization

### Adding New VLANs

To add new approved VLANs, update the `approved_vlans` section:

```yaml
approved_vlans:
  200: { name: "NEW_VLAN", description: "New department VLAN", type: "user" }
```

### Adding Protected Ports

To protect additional ports, update the `protected_ports` list:

```yaml
protected_ports:
  - "GigabitEthernet1/0/48"  # New protected port
```

### Adding New Operations

To add new operations, update the `valid_operations` list and add corresponding task blocks.

## 🚨 Error Handling

The template includes comprehensive error handling:

### Common Error Scenarios

1. **Protected Port Modification**:
   ```
   PROTECTED PORT ALERT!
   Port GigabitEthernet1/0/1 is protected and cannot be modified.
   ```

2. **Unapproved VLAN**:
   ```
   UNAPPROVED VLAN!
   VLAN 999 is not in the approved VLAN list.
   ```

3. **Missing Parameters**:
   ```
   VLAN assignment requires:
   - vlan_id: Target VLAN ID (1-4094)
   ```

4. **Invalid Switch**:
   ```
   Target switch must be specified!
   Use: -e target_switch=switch-hostname
   ```

### Troubleshooting Steps

1. **Verify switch hostname** exists in inventory
2. **Check port interface name** format matches switch type
3. **Ensure VLAN** is in approved list
4. **Verify port** is not in protected list
5. **Review parameter** requirements for operation

## 🔒 Security Features

- **✅ Semaphore Secrets Integration**: All credentials encrypted
- **✅ Protected Port Validation**: Critical ports cannot be modified
- **✅ Approved VLAN Enforcement**: Only pre-approved VLANs allowed
- **✅ Reserved VLAN Protection**: System VLANs protected
- **✅ Complete Audit Trail**: All operations logged
- **✅ Parameter Validation**: All inputs validated
- **✅ Operation Authorization**: Only valid operations allowed

## 📈 Best Practices

1. **Always test with dry-run** before executing changes
2. **Use descriptive port descriptions** for documentation
3. **Follow naming conventions** for VLANs
4. **Review protected ports** before modifications
5. **Check approved VLAN list** before assignments
6. **Monitor operation reports** for audit compliance
7. **Use trunk operations carefully** on production switches

## 🤝 Integration

The template integrates seamlessly with:

- **Semaphore UI**: Create templates with variable inputs
- **Ansible Tower/AWX**: Use as job templates
- **Command Line**: Direct execution via wrapper script
- **CI/CD Pipelines**: Automated network provisioning
- **Change Management**: Integration with ITSM systems

## 📄 Template Files

- **Playbook**: `infra/ansible/playbooks/network/vlan_management_template.yml`
- **Execution Script**: `infra/scripts/run_vlan_management.sh`
- **Documentation**: `infra/VLAN_MANAGEMENT_TEMPLATE.md`

This template provides enterprise-grade VLAN management with comprehensive safety features and multi-vendor support!
