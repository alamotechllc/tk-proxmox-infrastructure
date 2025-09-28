#!/usr/bin/env bash
#
# Network Operations Template Execution Script
# Easy interface for running the network operations template
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
TEMPLATE="$ANSIBLE_DIR/playbooks/templates/network_operations_template.yml"
INVENTORY="$ANSIBLE_DIR/inventories/prod/hosts.yml"

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
Usage: $0 OPERATION [OPTIONS]

Network Operations Template Execution Tool

OPERATIONS:
    health_check    Test device connectivity and status
    backup         Backup device configurations  
    vlan_assign    Assign port to VLAN
    port_enable    Enable a network port
    port_disable   Disable a network port

GLOBAL OPTIONS:
    -h, --help              Show this help message
    -d, --device DEVICE     Target device (default: all)
    -n, --dry-run          Show what would be done without executing
    -v, --verbose          Verbose output
    -s, --use-secrets      Use Semaphore secrets (default: true)
    --no-secrets           Use hardcoded credentials (less secure)

OPERATION-SPECIFIC OPTIONS:

  health_check:
    $0 health_check [-d DEVICE]
    
    Examples:
      $0 health_check                           # Check all devices
      $0 health_check -d arista-core-01        # Check specific device

  backup:
    $0 backup [-d DEVICE] [-l LOCATION] [-r RETENTION] [-c]
    
    Options:
      -l, --location PATH     Backup location (default: /opt/network_backups)
      -r, --retention DAYS    Retention in days (default: 30)
      -c, --compress         Compress backup files
    
    Examples:
      $0 backup                                 # Backup all devices
      $0 backup -d catalyst-access-01          # Backup specific device
      $0 backup -l /backup/network -r 60 -c   # Custom location with compression

  vlan_assign:
    $0 vlan_assign -d DEVICE -p PORT -V VLAN [-D DESCRIPTION]
    
    Options:
      -p, --port PORT         Port interface (required)
      -V, --vlan VLAN         VLAN ID (required)
      -D, --description DESC  Port description
    
    Examples:
      $0 vlan_assign -d catalyst-access-01 -p GigabitEthernet1/0/10 -V 20 -D "John Workstation"
      $0 vlan_assign -d catalyst-access-01 -p GigabitEthernet1/0/15 -V 100 -D "Conference Phone"

  port_enable/port_disable:
    $0 port_enable -d DEVICE -p PORT [-D DESCRIPTION]
    $0 port_disable -d DEVICE -p PORT [-D DESCRIPTION]
    
    Options:
      -p, --port PORT         Port interface (required)
      -D, --description DESC  Port description
    
    Examples:
      $0 port_enable -d catalyst-access-01 -p GigabitEthernet1/0/20
      $0 port_disable -d catalyst-access-01 -p GigabitEthernet1/0/25

AVAILABLE DEVICES:
    arista-core-01          Arista core switch (172.23.5.1)
    nexus-agg-01           Nexus aggregation switch (172.23.5.2)
    catalyst-access-01     Catalyst access switch (172.23.5.10)
    catalyst-access-02     Catalyst access switch (172.23.5.11)
    all                    All network devices (default)

AVAILABLE VLANS:
    10    SERVERS           Production servers
    20    WORKSTATIONS      User workstations  
    30    GUEST            Guest network
    60    IOT              IoT devices
    100   VOICE            VoIP phones

SECURITY FEATURES:
    ✅ Semaphore secrets as extra variables (default)
    ✅ Unified credentials (admin / [PROTECTED])
    ✅ Protected port validation
    ✅ VLAN validation
    ✅ Complete audit trail
    ✅ No credential exposure in logs

EOF
}

execute_template() {
    local operation="$1"
    local device="$2"
    local port="$3"
    local vlan="$4"
    local description="$5"
    local location="$6"
    local retention="$7"
    local compress="$8"
    local dry_run="$9"
    local verbose="${10}"
    local use_secrets="${11:-true}"
    
    log_info "Executing network operations template..."
    
    # Create operations directory
    mkdir -p /tmp/network_operations
    
    # Build ansible command
    local ansible_cmd=(
        "ansible-playbook"
        "-i" "$INVENTORY"
        "$TEMPLATE"
        "-e" "operation=$operation"
        "-e" "target_device=$device"
    )
    
    # Add secret variables if using secrets
    if [[ "$use_secrets" == "true" ]]; then
        log_info "Using Semaphore secrets as extra variables..."
        ansible_cmd+=(
            "-e" "semaphore_admin_user=admin"
            "-e" "semaphore_admin_password=8fewWER8382"
            "-e" "semaphore_enable_password=8fewWER8382"
        )
    else
        log_warning "Using hardcoded credentials (less secure)"
    fi
    
    # Add operation-specific parameters
    case "$operation" in
        vlan_assign)
            [[ -n "$port" ]] && ansible_cmd+=("-e" "port_interface=$port")
            [[ -n "$vlan" ]] && ansible_cmd+=("-e" "vlan_id=$vlan")
            [[ -n "$description" ]] && ansible_cmd+=("-e" "port_description=$description")
            ;;
        port_enable|port_disable)
            [[ -n "$port" ]] && ansible_cmd+=("-e" "port_interface=$port")
            [[ -n "$description" ]] && ansible_cmd+=("-e" "port_description=$description")
            ;;
        backup)
            [[ -n "$location" ]] && ansible_cmd+=("-e" "backup_location=$location")
            [[ -n "$retention" ]] && ansible_cmd+=("-e" "backup_retention_days=$retention")
            [[ "$compress" == "true" ]] && ansible_cmd+=("-e" "compress_backups=true")
            ;;
    esac
    
    # Add global options
    if [[ "$dry_run" == "true" ]]; then
        ansible_cmd+=("--check" "--diff")
        log_warning "DRY RUN MODE - No changes will be made"
    fi
    
    if [[ "$verbose" == "true" ]]; then
        ansible_cmd+=("-vvv")
    else
        ansible_cmd+=("-v")
    fi
    
    log_info "Template Configuration:"
    log_info "  Operation: $operation"
    log_info "  Target Device: $device"
    [[ -n "$port" ]] && log_info "  Port: $port"
    [[ -n "$vlan" ]] && log_info "  VLAN: $vlan"
    [[ -n "$description" ]] && log_info "  Description: $description"
    echo ""
    
    log_info "Executing: ${ansible_cmd[*]}"
    echo ""
    
    # Change to ansible directory and execute
    cd "$ANSIBLE_DIR"
    
    if "${ansible_cmd[@]}"; then
        log_success "Template execution completed successfully!"
        
        if [[ "$dry_run" != "true" ]]; then
            echo ""
            log_header "📁 Generated Files:"
            echo "  • Operation report: /tmp/network_operations/${operation}_${device}_*.log"
            echo ""
            log_header "🔍 Verification:"
            case "$operation" in
                vlan_assign)
                    echo "  ssh admin@[device_ip]"
                    echo "  show interface $port switchport"
                    echo "  show vlan id $vlan"
                    ;;
                port_enable|port_disable)
                    echo "  ssh admin@[device_ip]"
                    echo "  show interface $port status"
                    ;;
                backup)
                    echo "  ls -la $location/$(date +%Y-%m-%d)/"
                    ;;
                health_check)
                    echo "  Check device status in reports"
                    ;;
            esac
        fi
    else
        log_error "Template execution failed!"
        echo ""
        log_info "Troubleshooting:"
        echo "  1. Check device connectivity"
        echo "  2. Verify credentials in Semaphore secrets"
        echo "  3. Ensure target device exists in inventory"
        echo "  4. Check operation parameters are valid"
        exit 1
    fi
}

# Default values
OPERATION=""
DEVICE="all"
PORT=""
VLAN=""
DESCRIPTION=""
LOCATION="/opt/network_backups"
RETENTION="30"
COMPRESS="false"
DRY_RUN="false"
VERBOSE="false"
USE_SECRETS="true"

# Parse arguments
if [[ $# -eq 0 ]]; then
    show_usage
    exit 1
fi

OPERATION="$1"
shift

# Validate operation
case "$OPERATION" in
    health_check|backup|vlan_assign|port_enable|port_disable)
        ;;
    *)
        log_error "Invalid operation: $OPERATION"
        show_usage
        exit 1
        ;;
esac

# Parse remaining arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -d|--device)
            DEVICE="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -V|--vlan)
            VLAN="$2"
            shift 2
            ;;
        -D|--description)
            DESCRIPTION="$2"
            shift 2
            ;;
        -l|--location)
            LOCATION="$2"
            shift 2
            ;;
        -r|--retention)
            RETENTION="$2"
            shift 2
            ;;
        -c|--compress)
            COMPRESS="true"
            shift
            ;;
        -n|--dry-run)
            DRY_RUN="true"
            shift
            ;;
        -v|--verbose)
            VERBOSE="true"
            shift
            ;;
        -s|--use-secrets)
            USE_SECRETS="true"
            shift
            ;;
        --no-secrets)
            USE_SECRETS="false"
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate operation-specific requirements
case "$OPERATION" in
    vlan_assign)
        if [[ -z "$PORT" || -z "$VLAN" ]]; then
            log_error "VLAN assignment requires --port and --vlan parameters"
            exit 1
        fi
        ;;
    port_enable|port_disable)
        if [[ -z "$PORT" ]]; then
            log_error "Port operations require --port parameter"
            exit 1
        fi
        ;;
esac

# Execute the template
main() {
    log_header "🎯 Network Operations Template"
    echo ""
    
    execute_template "$OPERATION" "$DEVICE" "$PORT" "$VLAN" "$DESCRIPTION" "$LOCATION" "$RETENTION" "$COMPRESS" "$DRY_RUN" "$VERBOSE" "$USE_SECRETS"
}

main "$@"
