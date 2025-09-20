#!/usr/bin/env bash
#
# Semaphore Bootstrap Script
# Deploys Ansible Semaphore to Proxmox VM
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ANSIBLE_DIR="$PROJECT_ROOT/ansible"

# Configuration
INVENTORY_FILE="$ANSIBLE_DIR/inventories/prod/hosts.yml"
PLAYBOOK_FILE="$ANSIBLE_DIR/playbooks/semaphore/install.yml"

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

check_requirements() {
    log_info "Checking requirements..."
    
    # Check if ansible is installed
    if ! command -v ansible-playbook &> /dev/null; then
        log_error "Ansible is not installed. Please install ansible first."
        exit 1
    fi
    
    # Check if inventory file exists
    if [[ ! -f "$INVENTORY_FILE" ]]; then
        log_error "Inventory file not found: $INVENTORY_FILE"
        exit 1
    fi
    
    # Check if playbook exists
    if [[ ! -f "$PLAYBOOK_FILE" ]]; then
        log_error "Playbook file not found: $PLAYBOOK_FILE"
        exit 1
    fi
    
    log_success "Requirements check passed"
}

check_vm_connectivity() {
    log_info "Testing VM connectivity..."
    
    if ansible control_nodes -i "$INVENTORY_FILE" -m ping > /dev/null 2>&1; then
        log_success "VM connectivity test passed"
    else
        log_error "Cannot connect to control node VM"
        log_info "Please ensure:"
        log_info "  1. VM is running and accessible"
        log_info "  2. SSH key is properly configured"
        log_info "  3. Inventory file has correct IP address"
        exit 1
    fi
}

deploy_semaphore() {
    log_info "Deploying Semaphore to VM..."
    
    # Change to ansible directory
    cd "$ANSIBLE_DIR"
    
    # Run the playbook
    ansible-playbook \
        -i "$INVENTORY_FILE" \
        "$PLAYBOOK_FILE" \
        --diff \
        -v
    
    if [[ $? -eq 0 ]]; then
        log_success "Semaphore deployment completed successfully!"
    else
        log_error "Semaphore deployment failed"
        exit 1
    fi
}

show_access_info() {
    # Extract VM IP from inventory
    local vm_ip
    vm_ip=$(grep -A 10 "ansible-control:" "$INVENTORY_FILE" | grep "ansible_host:" | awk '{print $2}' | tr -d '"')
    
    echo ""
    echo "=========================================="
    echo "🎉 ANSIBLE SEMAPHORE DEPLOYED!"
    echo "=========================================="
    echo ""
    echo "🌐 Access URL: http://${vm_ip}:3000"
    echo "👤 Username: admin"
    echo "📧 Email: admin@example.com"
    echo "🔑 Password: Check inventory file for vault_semaphore_admin_password"
    echo ""
    echo "🔧 Management Commands (run on VM):"
    echo "  sudo systemctl status semaphore-compose"
    echo "  sudo systemctl restart semaphore-compose"
    echo "  docker compose -f /opt/semaphore/docker-compose.yml ps"
    echo "  docker compose -f /opt/semaphore/docker-compose.yml logs -f"
    echo ""
    echo "📁 Data Location: /opt/semaphore/"
    echo "🔄 Auto-start: Enabled (survives reboots)"
    echo "=========================================="
}

main() {
    log_info "Starting Semaphore deployment..."
    
    check_requirements
    check_vm_connectivity
    deploy_semaphore
    show_access_info
    
    log_success "Bootstrap completed successfully!"
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [--help]"
        echo ""
        echo "This script deploys Ansible Semaphore to a Proxmox VM."
        echo ""
        echo "Prerequisites:"
        echo "  1. VM created with Ubuntu 22.04"
        echo "  2. SSH access configured"
        echo "  3. Inventory file updated with VM IP"
        echo ""
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
