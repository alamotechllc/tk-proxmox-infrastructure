#!/usr/bin/env bash

# VLAN Management Template Execution Script
# Variable-based VLAN operations on selected network switches
# Supports: Port assignment, VLAN creation, port control, trunk management

# --- Configuration ---
INVENTORY="/Users/mike.turner/APP_Projects/tk-proxmox/infra/ansible/inventories/prod/hosts.yml"
PLAYBOOK="/Users/mike.turner/APP_Projects/tk-proxmox/infra/ansible/playbooks/network/vlan_management_template.yml"

# --- Logging Functions ---
log_info() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

log_warning() {
    echo -e "\033[1;33m[WARNING]\033[0m $1"
}

log_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

log_header() {
    echo -e "\033[0;36m$1\033[0m"
}

log_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

# --- Usage Information ---
show_usage() {
    log_header "Usage: $0 OPERATION [OPTIONS]"
    echo ""
    log_header "VLAN Management Template - Variable-based VLAN Operations"
    echo ""
    log_header "OPERATIONS:"
    echo "    assign          Assign port to access VLAN"
    echo "    create          Create new VLAN"
    echo "    delete          Delete VLAN (if unused)"
    echo "    port_enable     Enable a port"
    echo "    port_disable    Disable a port"
    echo "    trunk_add       Add VLANs to trunk port"
    echo "    trunk_remove    Remove VLANs from trunk port"
    echo "    show_config     Display current configuration"
    echo ""
    log_header "GLOBAL OPTIONS:"
    echo "    -h, --help              Show this help message"
    echo "    -s, --switch SWITCH     Target switch hostname or IP (required)"
    echo "    -p, --port PORT         Port interface (required for port operations)"
    echo "    -v, --vlan VLAN         VLAN ID (required for VLAN operations)"
    echo "    -n, --name NAME         VLAN name (required for VLAN creation)"
    echo "    -d, --description DESC  Port description"
    echo "    -t, --trunk-vlans LIST  Comma-separated VLAN list for trunk operations"
    echo "    --dry-run              Show what would be done without executing"
    echo "    --verbose              Verbose output"
    echo ""
    log_header "EXAMPLES:"
    echo ""
    echo "  📌 Assign port to VLAN:"
    echo "    $0 assign -s catalyst-access-01 -p GigabitEthernet1/0/10 -v 20 -d \"John Workstation\""
    echo ""
    echo "  📌 Create new VLAN:"
    echo "    $0 create -s arista-core-01 -v 150 -n \"NEW_DEPT\""
    echo ""
    echo "  📌 Enable/disable port:"
    echo "    $0 port_enable -s nexus-agg-01 -p Ethernet1/10"
    echo "    $0 port_disable -s nexus-agg-01 -p Ethernet1/15"
    echo ""
    echo "  📌 Trunk management:"
    echo "    $0 trunk_add -s catalyst-access-01 -p GigabitEthernet1/0/48 -t \"10,20,30\""
    echo "    $0 trunk_remove -s catalyst-access-01 -p GigabitEthernet1/0/48 -t \"30\""
    echo ""
    echo "  📌 Show configuration:"
    echo "    $0 show_config -s arista-core-01 -p Ethernet1/1"
    echo ""
    echo "  📌 Dry run:"
    echo "    $0 assign -s catalyst-access-01 -p GigabitEthernet1/0/10 -v 20 --dry-run"
    echo ""
    log_header "AVAILABLE SWITCHES:"
    echo "    arista-core-01          Arista core switch (172.23.5.1)"
    echo "    nexus-agg-01           Nexus aggregation switch (172.23.5.2)"
    echo "    catalyst-access-01     Catalyst access switch (172.23.5.10)"
    echo "    catalyst-access-02     Catalyst access switch (172.23.5.11)"
    echo ""
    log_header "APPROVED VLANS:"
    echo "    10    SERVERS           Production servers"
    echo "    20    WORKSTATIONS      User workstations"
    echo "    30    GUEST            Guest network"
    echo "    40    DMZ              DMZ servers"
    echo "    50    SECURITY         Security systems"
    echo "    60    IOT              IoT devices"
    echo "    70    PRINTERS         Network printers"
    echo "    80    WIRELESS         Wireless access points"
    echo "    90    CAMERAS          IP cameras"
    echo "    100   VOICE            VoIP phones"
    echo "    110   BACKUP           Backup network"
    echo "    120   STORAGE          Storage network"
    echo "    999   QUARANTINE       Quarantine VLAN"
    echo ""
    log_header "SAFETY FEATURES:"
    echo "    ✅ Protected port validation (prevents uplink modification)"
    echo "    ✅ Approved VLAN validation (only allowed VLANs)"
    echo "    ✅ Reserved VLAN protection (system VLANs protected)"
    echo "    ✅ Trunk VLAN validation (all VLANs must be approved)"
    echo "    ✅ Operation parameter validation"
    echo "    ✅ Complete audit trail and logging"
    echo ""
}

# --- Parameter Validation ---
validate_parameters() {
    if [[ -z "$SWITCH" ]]; then
        log_error "Switch is required for all operations. Use -s or --switch"
        exit 1
    fi
    
    case "$OPERATION" in
        assign)
            if [[ -z "$PORT" || -z "$VLAN" ]]; then
                log_error "Port assignment requires --port and --vlan"
                exit 1
            fi
            ;;
        create)
            if [[ -z "$VLAN" || -z "$VLAN_NAME" ]]; then
                log_error "VLAN creation requires --vlan and --name"
                exit 1
            fi
            ;;
        delete)
            if [[ -z "$VLAN" ]]; then
                log_error "VLAN deletion requires --vlan"
                exit 1
            fi
            ;;
        port_enable|port_disable)
            if [[ -z "$PORT" ]]; then
                log_error "Port operations require --port"
                exit 1
            fi
            ;;
        trunk_add|trunk_remove)
            if [[ -z "$PORT" || -z "$TRUNK_VLANS" ]]; then
                log_error "Trunk operations require --port and --trunk-vlans"
                exit 1
            fi
            ;;
        show_config)
            # No additional validation needed
            ;;
        *)
            log_error "Invalid operation: $OPERATION"
            show_usage
            exit 1
            ;;
    esac
    
    if [[ ! -f "$INVENTORY" ]]; then
        log_error "Inventory file not found: $INVENTORY"
        exit 1
    fi
    
    if [[ ! -f "$PLAYBOOK" ]]; then
        log_error "Playbook file not found: $PLAYBOOK"
        exit 1
    fi
}

# --- Main Execution Function ---
execute_vlan_operation() {
    local operation="$1"
    local switch="$2"
    local port="$3"
    local vlan="$4"
    local vlan_name="$5"
    local description="$6"
    local trunk_vlans="$7"
    local dry_run="$8"
    local verbose="$9"
    
    log_info "Executing VLAN management operation..."
    
    # Create operations directory
    mkdir -p /tmp/vlan_operations
    
    # Build ansible command
    local ansible_cmd=(
        "ansible-playbook"
        "-i" "$INVENTORY"
        "$PLAYBOOK"
        "-e" "vlan_operation=$operation"
        "-e" "target_switch=$switch"
    )
    
    # Add operation-specific parameters
    [[ -n "$port" ]] && ansible_cmd+=("-e" "port_interface=$port")
    [[ -n "$vlan" ]] && ansible_cmd+=("-e" "vlan_id=$vlan")
    [[ -n "$vlan_name" ]] && ansible_cmd+=("-e" "vlan_name=$vlan_name")
    [[ -n "$description" ]] && ansible_cmd+=("-e" "port_description=$description")
    [[ -n "$trunk_vlans" ]] && ansible_cmd+=("-e" "trunk_vlans=$trunk_vlans")
    
    # Add Semaphore secrets (these would be provided by Semaphore in production)
    ansible_cmd+=(
        "-e" "semaphore_admin_user=admin"
        "-e" "semaphore_admin_password=8fewWER8382"
        "-e" "semaphore_enable_password=8fewWER8382"
    )
    
    # Add dry-run and verbose flags
    [[ "$dry_run" == "true" ]] && ansible_cmd+=("--check" "--diff") && log_warning "DRY RUN MODE - No changes will be made"
    [[ "$verbose" == "true" ]] && ansible_cmd+=("-v")

    log_info "Executing: ${ansible_cmd[*]}"
    "${ansible_cmd[@]}"
    
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        log_success "VLAN management operation completed successfully!"
        echo ""
        log_info "Operation Details:"
        echo "  🔧 Operation: $operation"
        echo "  🎯 Switch: $switch"
        [[ -n "$port" ]] && echo "  🔌 Port: $port"
        [[ -n "$vlan" ]] && echo "  🏷️  VLAN: $vlan"
        [[ -n "$vlan_name" ]] && echo "  📛 Name: $vlan_name"
        [[ -n "$description" ]] && echo "  📝 Description: $description"
        [[ -n "$trunk_vlans" ]] && echo "  🔗 Trunk VLANs: $trunk_vlans"
        echo ""
        if [[ "$dry_run" != "true" ]]; then
            log_info "Check operation report: /tmp/vlan_operations/${switch}_${operation}_*.log"
        fi
    else
        log_error "VLAN management operation failed with exit code: $exit_code"
        echo ""
        log_info "Troubleshooting:"
        echo "  1. Verify switch hostname and connectivity"
        echo "  2. Check port interface name format"
        echo "  3. Ensure VLAN is in approved list"
        echo "  4. Verify port is not protected"
        echo "  5. Review Ansible output for specific errors"
        exit $exit_code
    fi
}

# --- Default Values ---
OPERATION=""
SWITCH=""
PORT=""
VLAN=""
VLAN_NAME=""
DESCRIPTION=""
TRUNK_VLANS=""
DRY_RUN="false"
VERBOSE="false"

# --- Parse Arguments ---
if [[ $# -eq 0 ]]; then
    show_usage
    exit 1
fi

OPERATION="$1"
shift

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            show_usage
            exit 0
            ;;
        -s|--switch)
            SWITCH="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -v|--vlan)
            VLAN="$2"
            shift 2
            ;;
        -n|--name)
            VLAN_NAME="$2"
            shift 2
            ;;
        -d|--description)
            DESCRIPTION="$2"
            shift 2
            ;;
        -t|--trunk-vlans)
            TRUNK_VLANS="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        --verbose)
            VERBOSE="true"
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# --- Validate and Execute ---
validate_parameters

log_header "🔧 VLAN Management Template"
echo ""

execute_vlan_operation "$OPERATION" "$SWITCH" "$PORT" "$VLAN" "$VLAN_NAME" "$DESCRIPTION" "$TRUNK_VLANS" "$DRY_RUN" "$VERBOSE"
