#!/usr/bin/env bash
#
# Network Switch Backup Script
# Executes the network switch backup runbook for all vendors
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ANSIBLE_DIR="$PROJECT_ROOT/ansible"
PLAYBOOK="$ANSIBLE_DIR/playbooks/network/backup_switches.yml"
INVENTORY="$ANSIBLE_DIR/inventories/prod/hosts.yml"
BACKUP_BASE="/opt/network_backups"

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

show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Network Switch Configuration Backup Script

OPTIONS:
    -h, --help              Show this help message
    -v, --vendor VENDOR     Backup specific vendor only (arista|nexus|catalyst|all)
    -l, --location PATH     Backup location (default: $BACKUP_BASE)
    -r, --retention DAYS    Retention period in days (default: 30)
    -c, --compress          Compress backup files
    -n, --dry-run           Show what would be backed up without executing
    -f, --force             Force backup even if recent backup exists

EXAMPLES:
    $0                                    # Backup all switches
    $0 -v arista                         # Backup only Arista switches
    $0 -v nexus -c                       # Backup Nexus switches with compression
    $0 -l /backup/network -r 60          # Custom location with 60-day retention
    $0 -n                                # Dry run to see what would be backed up

VENDOR TARGETS:
    arista      - Arista EOS switches only
    nexus       - Cisco Nexus NX-OS switches only  
    catalyst    - Cisco Catalyst IOS-XE switches only
    all         - All network switches (default)

EOF
}

check_requirements() {
    log_info "Checking requirements..."
    
    # Check if ansible is installed
    if ! command -v ansible-playbook &> /dev/null; then
        log_error "Ansible is not installed"
        exit 1
    fi
    
    # Check if playbook exists
    if [[ ! -f "$PLAYBOOK" ]]; then
        log_error "Backup playbook not found: $PLAYBOOK"
        exit 1
    fi
    
    # Check if inventory exists
    if [[ ! -f "$INVENTORY" ]]; then
        log_error "Inventory file not found: $INVENTORY"
        exit 1
    fi
    
    log_success "Requirements check passed"
}

run_backup() {
    local vendor_filter="$1"
    local backup_location="$2"
    local retention_days="$3"
    local compress="$4"
    local dry_run="$5"
    
    log_info "Starting network switch backup..."
    
    # Determine target hosts based on vendor filter
    local target_hosts="arista_switches:nexus_switches:catalyst_switches"
    case "$vendor_filter" in
        arista)
            target_hosts="arista_switches"
            ;;
        nexus)
            target_hosts="nexus_switches"
            ;;
        catalyst)
            target_hosts="catalyst_switches"
            ;;
        all)
            target_hosts="arista_switches:nexus_switches:catalyst_switches"
            ;;
    esac
    
    # Build ansible-playbook command
    local ansible_cmd=(
        "ansible-playbook"
        "-i" "$INVENTORY"
        "$PLAYBOOK"
        "--limit" "$target_hosts"
        "-e" "backup_location=$backup_location"
        "-e" "backup_retention_days=$retention_days"
        "-e" "compress_backups=$compress"
        "-v"
    )
    
    if [[ "$dry_run" == "true" ]]; then
        ansible_cmd+=("--check" "--diff")
        log_info "DRY RUN MODE - No changes will be made"
    fi
    
    log_info "Executing backup command:"
    log_info "${ansible_cmd[*]}"
    
    # Change to ansible directory and run
    cd "$ANSIBLE_DIR"
    
    if "${ansible_cmd[@]}"; then
        log_success "Network backup completed successfully!"
        
        if [[ "$dry_run" != "true" ]]; then
            echo ""
            echo "📁 Backup Location: $backup_location/$(date +%Y-%m-%d)"
            echo "🔍 View Summary: cat $backup_location/$(date +%Y-%m-%d)/backup_summary_*.txt"
            echo "📦 Compressed: ${compress}"
            echo "🗓️  Retention: ${retention_days} days"
            echo ""
            echo "🔧 Management Commands:"
            echo "  ls -la $backup_location/$(date +%Y-%m-%d)/"
            echo "  find $backup_location -name '*.cfg' -mtime -1"
            echo "  du -sh $backup_location/*"
        fi
    else
        log_error "Network backup failed!"
        exit 1
    fi
}

# Default values
VENDOR="all"
LOCATION="$BACKUP_BASE"
RETENTION="30"
COMPRESS="false"
DRY_RUN="false"
FORCE="false"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -v|--vendor)
            VENDOR="$2"
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
        -f|--force)
            FORCE="true"
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate vendor filter
case "$VENDOR" in
    arista|nexus|catalyst|all)
        ;;
    *)
        log_error "Invalid vendor filter: $VENDOR"
        log_info "Valid options: arista, nexus, catalyst, all"
        exit 1
        ;;
esac

# Main execution
main() {
    log_info "Network Switch Backup Script"
    echo ""
    echo "Configuration:"
    echo "  Vendor Filter: $VENDOR"
    echo "  Backup Location: $LOCATION"
    echo "  Retention: $RETENTION days"
    echo "  Compression: $COMPRESS"
    echo "  Dry Run: $DRY_RUN"
    echo ""
    
    check_requirements
    run_backup "$VENDOR" "$LOCATION" "$RETENTION" "$COMPRESS" "$DRY_RUN"
}

main "$@"
