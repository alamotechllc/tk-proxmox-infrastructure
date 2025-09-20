#!/usr/bin/env bash
#
# Safe VLAN Port Assignment Script
# Assigns access ports to VLANs with comprehensive safety checks
# PROTECTION: Cannot modify trunk ports or critical uplinks
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ANSIBLE_DIR="$PROJECT_ROOT/ansible"
PLAYBOOK="$ANSIBLE_DIR/playbooks/network/vlan_port_assignment.yml"
INVENTORY="$ANSIBLE_DIR/inventories/prod/hosts.yml"

# Available switches and VLANs
AVAILABLE_SWITCHES=(
    "catalyst-access-01:172.23.5.10:C9300-48P:Floor_1_IDF"
    "catalyst-access-02:172.23.5.11:C9300-24P:Floor_2_IDF"
    "nexus-agg-01:172.23.5.2:N9K-C93180YC-EX:Aggregation_Rack"
    "arista-core-01:172.23.5.1:DCS-7280SR-48C6:Core_Rack"
)

AVAILABLE_VLANS=(
    "10:SERVERS:Production_Servers"
    "20:WORKSTATIONS:User_Workstations"
    "30:GUEST:Guest_Network"
    "60:IOT:IoT_Devices"
    "100:VOICE:VoIP_Phones"
)

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "${CYAN}$1${NC}"
}

show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Safe VLAN Port Assignment Tool

DESCRIPTION:
    Safely assigns access ports to VLANs with comprehensive protection against
    modifying trunk ports, uplinks, or critical infrastructure ports.

OPTIONS:
    -h, --help                  Show this help message
    -s, --switch SWITCH         Target switch hostname
    -p, --port PORT             Target port interface
    -v, --vlan VLAN_ID          Target VLAN ID
    -d, --description DESC      Port description
    -l, --list-switches         List available switches
    -L, --list-vlans           List available VLANs
    -n, --dry-run              Show what would be changed without executing
    -i, --interactive          Interactive mode (guided setup)

EXAMPLES:
    # Interactive mode (recommended for beginners)
    $0 -i

    # Assign port to VLAN
    $0 -s catalyst-access-01 -p GigabitEthernet1/0/10 -v 20 -d "John's Workstation"

    # Assign VoIP phone port
    $0 -s catalyst-access-01 -p GigabitEthernet1/0/15 -v 100 -d "Conference Room Phone"

    # Dry run to test
    $0 -s catalyst-access-01 -p GigabitEthernet1/0/20 -v 10 -n

SAFETY FEATURES:
    ✅ Trunk port protection        - Cannot modify trunk ports
    ✅ Uplink protection           - Critical uplinks are protected  
    ✅ VLAN validation            - Only approved VLANs allowed
    ✅ Pre-change backup          - Configuration backed up before changes
    ✅ Change verification        - Post-change validation
    ✅ Detailed logging           - Complete audit trail

PROTECTED PORTS (CANNOT BE MODIFIED):
    • TenGigabitEthernet1/1/1     - Uplink to core
    • TenGigabitEthernet1/1/2     - Uplink to core
    • GigabitEthernet1/0/1        - Inter-switch link
    • GigabitEthernet1/0/2        - Inter-switch link

EOF
}

list_switches() {
    log_header "Available Network Switches:"
    echo ""
    printf "%-20s %-15s %-20s %s\n" "HOSTNAME" "IP ADDRESS" "MODEL" "LOCATION"
    printf "%-20s %-15s %-20s %s\n" "--------" "----------" "-----" "--------"
    
    for switch_info in "${AVAILABLE_SWITCHES[@]}"; do
        IFS=':' read -r hostname ip model location <<< "$switch_info"
        printf "%-20s %-15s %-20s %s\n" "$hostname" "$ip" "$model" "$location"
    done
    echo ""
}

list_vlans() {
    log_header "Available VLANs:"
    echo ""
    printf "%-8s %-15s %s\n" "VLAN ID" "NAME" "DESCRIPTION"
    printf "%-8s %-15s %s\n" "-------" "----" "-----------"
    
    for vlan_info in "${AVAILABLE_VLANS[@]}"; do
        IFS=':' read -r vlan_id name description <<< "$vlan_info"
        printf "%-8s %-15s %s\n" "$vlan_id" "$name" "$description"
    done
    echo ""
}

interactive_mode() {
    log_header "🔧 Interactive VLAN Port Assignment"
    echo ""
    
    # Select switch
    echo "1. Select target switch:"
    list_switches
    read -p "Enter switch hostname: " SWITCH_NAME
    
    # Validate switch
    if ! printf '%s\n' "${AVAILABLE_SWITCHES[@]}" | grep -q "^$SWITCH_NAME:"; then
        log_error "Invalid switch name: $SWITCH_NAME"
        exit 1
    fi
    
    # Select VLAN
    echo ""
    echo "2. Select target VLAN:"
    list_vlans
    read -p "Enter VLAN ID: " VLAN_ID
    
    # Validate VLAN
    if ! printf '%s\n' "${AVAILABLE_VLANS[@]}" | grep -q "^$VLAN_ID:"; then
        log_error "Invalid VLAN ID: $VLAN_ID"
        exit 1
    fi
    
    # Get port
    echo ""
    echo "3. Enter port interface:"
    echo "   Examples: GigabitEthernet1/0/10, GigabitEthernet1/0/15"
    echo "   Safe ranges: GigabitEthernet1/0/3-48 (avoid 1-2 for uplinks)"
    read -p "Enter port interface: " PORT_INTERFACE
    
    # Get description
    echo ""
    echo "4. Enter port description:"
    read -p "Enter description (e.g., 'John Smith Workstation'): " PORT_DESC
    
    # Confirmation
    echo ""
    log_header "🔍 Configuration Summary:"
    echo "  Switch: $SWITCH_NAME"
    echo "  Port: $PORT_INTERFACE"
    echo "  VLAN: $VLAN_ID ($(printf '%s\n' "${AVAILABLE_VLANS[@]}" | grep "^$VLAN_ID:" | cut -d: -f2))"
    echo "  Description: $PORT_DESC"
    echo ""
    
    read -p "Proceed with this configuration? (y/N): " CONFIRM
    if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
        log_info "Operation cancelled by user"
        exit 0
    fi
    
    # Execute the change
    execute_vlan_assignment "$SWITCH_NAME" "$PORT_INTERFACE" "$VLAN_ID" "$PORT_DESC" "false"
}

execute_vlan_assignment() {
    local switch_name="$1"
    local port_interface="$2"
    local vlan_id="$3"
    local port_desc="$4"
    local dry_run="$5"
    
    log_info "Executing VLAN port assignment..."
    
    # Create change directory
    mkdir -p /tmp/network_changes
    
    # Build ansible command
    local ansible_cmd=(
        "ansible-playbook"
        "-i" "$INVENTORY"
        "$PLAYBOOK"
        "--limit" "$switch_name"
        "-e" "port_interface=$port_interface"
        "-e" "vlan_id=$vlan_id"
        "-e" "port_desc=$port_desc"
        "-v"
    )
    
    if [[ "$dry_run" == "true" ]]; then
        ansible_cmd+=("--check" "--diff")
        log_warning "DRY RUN MODE - No changes will be made"
    fi
    
    log_info "Executing command:"
    log_info "${ansible_cmd[*]}"
    echo ""
    
    # Change to ansible directory and execute
    cd "$ANSIBLE_DIR"
    
    if "${ansible_cmd[@]}"; then
        log_success "VLAN port assignment completed successfully!"
        
        if [[ "$dry_run" != "true" ]]; then
            echo ""
            log_header "📋 Post-Change Information:"
            echo "  • Pre-change backup: /tmp/network_changes/${switch_name}_pre_change_*.cfg"
            echo "  • Change log: /tmp/network_changes/${switch_name}_vlan_change_*.log"
            echo "  • Verification: Port should now be in VLAN $vlan_id"
            echo ""
            log_header "🔍 Verification Commands:"
            echo "  ssh admin@$(get_switch_ip "$switch_name")"
            echo "  show interface $port_interface switchport"
            echo "  show interface $port_interface status"
            echo "  show vlan id $vlan_id"
        fi
    else
        log_error "VLAN port assignment failed!"
        echo ""
        log_info "Troubleshooting:"
        echo "  1. Check switch connectivity"
        echo "  2. Verify credentials in Semaphore"
        echo "  3. Ensure port is not protected"
        echo "  4. Check logs in /tmp/network_changes/"
        exit 1
    fi
}

get_switch_ip() {
    local switch_name="$1"
    for switch_info in "${AVAILABLE_SWITCHES[@]}"; do
        if [[ "$switch_info" == "$switch_name:"* ]]; then
            echo "$switch_info" | cut -d: -f2
            return
        fi
    done
    echo "unknown"
}

validate_inputs() {
    local switch_name="$1"
    local port_interface="$2" 
    local vlan_id="$3"
    
    # Validate switch
    if ! printf '%s\n' "${AVAILABLE_SWITCHES[@]}" | grep -q "^$switch_name:"; then
        log_error "Invalid switch name: $switch_name"
        echo ""
        list_switches
        exit 1
    fi
    
    # Validate VLAN
    if ! printf '%s\n' "${AVAILABLE_VLANS[@]}" | grep -q "^$vlan_id:"; then
        log_error "Invalid VLAN ID: $vlan_id"
        echo ""
        list_vlans
        exit 1
    fi
    
    # Basic port format validation
    if [[ ! "$port_interface" =~ ^(GigabitEthernet|TenGigabitEthernet|Ethernet)[0-9/]+ ]]; then
        log_error "Invalid port format: $port_interface"
        log_info "Examples: GigabitEthernet1/0/10, TenGigabitEthernet1/1/1, Ethernet1/1"
        exit 1
    fi
    
    log_success "Input validation passed"
}

# Default values
SWITCH_NAME=""
PORT_INTERFACE=""
VLAN_ID=""
PORT_DESC=""
DRY_RUN="false"
INTERACTIVE="false"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -s|--switch)
            SWITCH_NAME="$2"
            shift 2
            ;;
        -p|--port)
            PORT_INTERFACE="$2"
            shift 2
            ;;
        -v|--vlan)
            VLAN_ID="$2"
            shift 2
            ;;
        -d|--description)
            PORT_DESC="$2"
            shift 2
            ;;
        -l|--list-switches)
            list_switches
            exit 0
            ;;
        -L|--list-vlans)
            list_vlans
            exit 0
            ;;
        -n|--dry-run)
            DRY_RUN="true"
            shift
            ;;
        -i|--interactive)
            INTERACTIVE="true"
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    log_header "🔧 Safe VLAN Port Assignment Tool"
    echo ""
    
    if [[ "$INTERACTIVE" == "true" ]]; then
        interactive_mode
    else
        # Validate required parameters
        if [[ -z "$SWITCH_NAME" || -z "$PORT_INTERFACE" || -z "$VLAN_ID" ]]; then
            log_error "Missing required parameters"
            echo ""
            log_info "Required: --switch, --port, --vlan"
            log_info "Use --interactive for guided setup"
            log_info "Use --help for detailed usage"
            exit 1
        fi
        
        # Set default description if not provided
        if [[ -z "$PORT_DESC" ]]; then
            PORT_DESC="Access port - VLAN $VLAN_ID"
        fi
        
        # Validate inputs
        validate_inputs "$SWITCH_NAME" "$PORT_INTERFACE" "$VLAN_ID"
        
        # Execute the assignment
        execute_vlan_assignment "$SWITCH_NAME" "$PORT_INTERFACE" "$VLAN_ID" "$PORT_DESC" "$DRY_RUN"
    fi
}

main "$@"
