# Semaphore Template Setup Guide

## 🎯 Switch-Specific VLAN Assignment Template Configuration

### Template Settings in Semaphore UI

**Basic Template Information:**
- **Name**: `Switch-Specific VLAN Assignment`
- **Playbook**: `playbooks/network/switch_specific_vlan_assignment.yml`
- **Inventory**: `inventories/network_switches.yml`
- **Repository**: Your tk-proxmox repository
- **Environment**: Production

### Required Extra Variables

Configure these variables in the Semaphore template:

| Variable Name | Type | Required | Default | Description | Example |
|---------------|------|----------|---------|-------------|---------|
| `switch_name` | String | ✅ Yes | - | Target switch to configure | `arista_core` |
| `port_interface` | String | ✅ Yes | - | Port interface to configure | `Ethernet1/10` |
| `vlan_id` | String | ✅ Yes | - | VLAN ID to assign (2-7) | `3` |
| `port_desc` | String | ❌ No | `Ansible managed` | Port description | `Office Workstation` |

### Required Secrets

Configure these as Semaphore secrets:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `semaphore_admin_user` | Network admin username | `admin` |
| `semaphore_admin_password` | Network admin password | `your_password` |
| `semaphore_enable_password` | Enable/privilege password | `your_enable_password` |

### Valid Values

#### Switch Names:
- `arista_core` - Arista Core Switch (tks-sw-arista-core-1)
- `cisco_nexus` - Cisco Nexus Switch (tks-sw-cis-nexus-1)  
- `access_switch` - Access Layer Switch (8-port)

#### VLAN IDs:
- `2` - SERVERS (172.23.2.0/24)
- `3` - WORKSTATIONS (172.23.3.0/24)
- `4` - GUEST (172.23.4.0/24)
- `5` - IOT (172.23.5.0/24)
- `6` - GAMING (172.23.6.0/24)
- `7` - MANAGEMENT (172.23.7.0/24)

#### Port Interfaces by Switch:

**Arista Core (`arista_core`):**
- Safe ports: `Ethernet1-48`
- Protected: `Ethernet49/1`, `Ethernet50/1`, `Management1`
- Example: `Ethernet1/10`

**Cisco Nexus (`cisco_nexus`):**
- Safe ports: `Ethernet1/1-17`, `Ethernet1/18-46`, `Ethernet1/47-48`
- Protected: `Ethernet1/50`, `Ethernet1/52`, `port-channel1`, `mgmt0`
- Example: `Ethernet1/20`

**Access Switch (`access_switch`):**
- Safe ports: `GigabitEthernet0/1-7`
- Protected: `GigabitEthernet0/8`
- Example: `GigabitEthernet0/3`

### Template Configuration Steps

1. **Create New Template:**
   - Go to Semaphore UI → Templates → Create Template
   - Name: `Switch-Specific VLAN Assignment`

2. **Configure Playbook:**
   - Playbook: `playbooks/network/switch_specific_vlan_assignment.yml`
   - Inventory: `inventories/network_switches.yml`

3. **Add Extra Variables:**
   ```
   switch_name: arista_core
   port_interface: Ethernet1/10
   vlan_id: 3
   port_desc: "Office Workstation"
   ```

4. **Configure Secrets:**
   - Go to Semaphore UI → Keys → Create Key
   - Add your network credentials as secrets

5. **Test Template:**
   - Use dry-run mode first
   - Verify variable validation works
   - Test with actual switch

### Example Template Usage

**Via Semaphore UI:**
1. Navigate to Templates → Switch-Specific VLAN Assignment
2. Fill in variables:
   - `switch_name`: `arista_core`
   - `port_interface`: `Ethernet1/10`
   - `vlan_id`: `3`
   - `port_desc`: `New User Workstation`
3. Click "Run Task"

**Via API/CLI:**
```bash
# Example API call
curl -X POST http://semaphore-url/api/project/1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": 14,
    "extra_vars": {
      "switch_name": "arista_core",
      "port_interface": "Ethernet1/10", 
      "vlan_id": "3",
      "port_desc": "Office Workstation"
    }
  }'
```

### Troubleshooting

#### Common Issues:

1. **"Mandatory variable 'switch_name' not defined"**
   - Solution: Ensure `switch_name` is set in Semaphore extra variables

2. **"Switch 'xxx' not found in configuration"**
   - Solution: Use valid switch names: `arista_core`, `cisco_nexus`, `access_switch`

3. **"Port 'xxx' is protected and cannot be modified"**
   - Solution: Use safe port ranges for each switch type

4. **"VLAN 'xxx' is not approved"**
   - Solution: Use VLAN IDs 2-7 only

5. **Inventory parsing errors**
   - Solution: Ensure `inventories/network_switches.yml` is properly formatted

### Safety Features

✅ **Protected Port Validation** - Critical uplinks cannot be modified  
✅ **Approved VLAN Enforcement** - Only VLANs 2-7 allowed  
✅ **Switch-Specific Validation** - Port ranges validated per switch  
✅ **Complete Audit Trail** - All operations logged  
✅ **Variable Validation** - Required parameters checked  

### Testing the Template

1. **Dry Run Test:**
   ```bash
   ansible-playbook -i inventories/network_switches.yml \
     playbooks/network/switch_specific_vlan_assignment.yml \
     -e "switch_name=arista_core" \
     -e "port_interface=Ethernet1/10" \
     -e "vlan_id=3" \
     -e "port_desc=Test Port" \
     --check --diff
   ```

2. **Variable Validation Test:**
   ```bash
   # This should fail with helpful error message
   ansible-playbook -i inventories/network_switches.yml \
     playbooks/network/switch_specific_vlan_assignment.yml \
     -e "switch_name=invalid_switch"
   ```

### Next Steps

1. ✅ Fix inventory parsing issue in Semaphore
2. ✅ Configure template with required variables
3. ✅ Test with dry-run mode
4. ✅ Execute actual VLAN assignment
5. ✅ Document successful operations

---

**The template is ready for production use once Semaphore variables are properly configured!** 🎉
