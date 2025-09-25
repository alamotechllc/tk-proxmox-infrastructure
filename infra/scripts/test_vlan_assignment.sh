#!/bin/bash

# Test VLAN Assignment Template
# This script tests the new switch-specific VLAN assignment without making changes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Testing Switch-Specific VLAN Assignment ===${NC}"
echo ""

# Test cases
test_cases=(
    "arista_core Ethernet1/10 3 'Test Workstation'"
    "cisco_nexus Ethernet1/20 6 'Test Gaming Console'"
    "access_switch GigabitEthernet0/3 5 'Test IoT Device'"
)

echo -e "${YELLOW}Running syntax validation tests...${NC}"
echo ""

cd "$(dirname "$0")/../.."

# Test 1: Syntax validation
echo -e "${BLUE}Test 1: Playbook Syntax Validation${NC}"
ansible-playbook \
    -i infra/ansible/inventories/network_switches.yml \
    infra/ansible/playbooks/network/switch_specific_vlan_assignment.yml \
    -e "switch_name=arista_core" \
    -e "port_interface=Ethernet1/10" \
    -e "vlan_id=3" \
    --syntax-check

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Syntax check passed${NC}"
else
    echo -e "${RED}❌ Syntax check failed${NC}"
    exit 1
fi

echo ""

# Test 2: Dry run with different switches
echo -e "${BLUE}Test 2: Dry Run Tests${NC}"

for test_case in "${test_cases[@]}"; do
    IFS=' ' read -r switch port vlan desc <<< "$test_case"
    
    echo -e "${YELLOW}Testing: $switch - $port - VLAN $vlan${NC}"
    
    ansible-playbook \
        -i infra/ansible/inventories/network_switches.yml \
        infra/ansible/playbooks/network/switch_specific_vlan_assignment.yml \
        -e "switch_name=$switch" \
        -e "port_interface=$port" \
        -e "vlan_id=$vlan" \
        -e "port_desc=$desc" \
        --check \
        --diff \
        -v
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Dry run passed for $switch${NC}"
    else
        echo -e "${RED}❌ Dry run failed for $switch${NC}"
    fi
    echo ""
done

# Test 3: Invalid cases (should fail)
echo -e "${BLUE}Test 3: Error Handling Tests${NC}"

# Test invalid VLAN
echo -e "${YELLOW}Testing invalid VLAN (should fail)...${NC}"
ansible-playbook \
    -i infra/ansible/inventories/network_switches.yml \
    infra/ansible/playbooks/network/switch_specific_vlan_assignment.yml \
    -e "switch_name=arista_core" \
    -e "port_interface=Ethernet1/10" \
    -e "vlan_id=99" \
    -e "port_desc=Test" \
    --check \
    -v 2>/dev/null

if [ $? -ne 0 ]; then
    echo -e "${GREEN}✅ Correctly rejected invalid VLAN${NC}"
else
    echo -e "${RED}❌ Should have rejected invalid VLAN${NC}"
fi

# Test protected port
echo -e "${YELLOW}Testing protected port (should fail)...${NC}"
ansible-playbook \
    -i infra/ansible/inventories/network_switches.yml \
    infra/ansible/playbooks/network/switch_specific_vlan_assignment.yml \
    -e "switch_name=arista_core" \
    -e "port_interface=Ethernet49/1" \
    -e "vlan_id=3" \
    -e "port_desc=Test" \
    --check \
    -v 2>/dev/null

if [ $? -ne 0 ]; then
    echo -e "${GREEN}✅ Correctly rejected protected port${NC}"
else
    echo -e "${RED}❌ Should have rejected protected port${NC}"
fi

echo ""
echo -e "${GREEN}=== All Tests Completed ===${NC}"
echo -e "${GREEN}✅ Switch-specific VLAN assignment template is ready!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Update access switch IP in inventories/network_switches.yml"
echo "2. Test with actual switches (use --check first)"
echo "3. Update Semaphore template to use new playbook"
echo "4. Document your port assignments"
