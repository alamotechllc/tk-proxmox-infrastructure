#!/bin/bash

# Simple VLAN Assignment Script
# Usage: ./assign_vlan_simple.sh <switch> <port> <vlan_id> [description]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo -e "${BLUE}Simple VLAN Assignment Script${NC}"
    echo ""
    echo "Usage: $0 <switch> <port> <vlan_id> [description]"
    echo ""
    echo "Switches:"
    echo "  arista_core    - Arista Core Switch (tks-sw-arista-core-1)"
    echo "  cisco_nexus    - Cisco Nexus Switch (tks-sw-cis-nexus-1)"
    echo "  access_switch  - Access Layer Switch (8-port)"
    echo ""
    echo "Examples:"
    echo "  $0 arista_core Ethernet1/10 3 'Office Workstation'"
    echo "  $0 cisco_nexus Ethernet1/20 6 'Gaming Console'"
    echo "  $0 access_switch GigabitEthernet0/3 5 'IoT Device'"
    echo ""
    echo "VLAN IDs:"
    echo "  2 - SERVERS (172.23.2.0/24)"
    echo "  3 - WORKSTATIONS (172.23.3.0/24)"
    echo "  4 - GUEST (172.23.4.0/24)"
    echo "  5 - IOT (172.23.5.0/24)"
    echo "  6 - GAMING (172.23.6.0/24)"
    echo "  7 - MANAGEMENT (172.23.7.0/24)"
    echo ""
    exit 1
}

# Check arguments
if [ $# -lt 3 ]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    usage
fi

SWITCH="$1"
PORT="$2"
VLAN_ID="$3"
DESCRIPTION="${4:-Ansible managed port}"

# Validate switch
case "$SWITCH" in
    arista_core|cisco_nexus|access_switch)
        ;;
    *)
        echo -e "${RED}Error: Invalid switch '$SWITCH'${NC}"
        echo "Valid switches: arista_core, cisco_nexus, access_switch"
        exit 1
        ;;
esac

# Validate VLAN ID
if ! [[ "$VLAN_ID" =~ ^[0-9]+$ ]] || [ "$VLAN_ID" -lt 2 ] || [ "$VLAN_ID" -gt 7 ]; then
    echo -e "${RED}Error: VLAN ID must be between 2-7${NC}"
    exit 1
fi

# Display operation details
echo -e "${BLUE}=== VLAN Assignment Operation ===${NC}"
echo "Switch: $SWITCH"
echo "Port: $PORT"
echo "VLAN: $VLAN_ID"
echo "Description: $DESCRIPTION"
echo "================================"
echo ""

# Confirm operation
read -p "Do you want to proceed? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Operation cancelled${NC}"
    exit 0
fi

# Run the Ansible playbook
echo -e "${GREEN}Running VLAN assignment...${NC}"

cd "$(dirname "$0")/.."

ansible-playbook \
    -i inventories/network_switches.yml \
    playbooks/network/switch_specific_vlan_assignment.yml \
    -e "switch_name=$SWITCH" \
    -e "port_interface=$PORT" \
    -e "vlan_id=$VLAN_ID" \
    -e "port_desc=$DESCRIPTION" \
    --ask-vault-pass \
    -v

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ VLAN assignment completed successfully!${NC}"
    echo -e "${GREEN}Port $PORT on $SWITCH is now assigned to VLAN $VLAN_ID${NC}"
else
    echo -e "${RED}❌ VLAN assignment failed${NC}"
    exit 1
fi

