#!/usr/bin/env bash
#
# Create Semaphore VM Script
# Uses Proxmox MCP tools to create the ansible-control VM
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# VM Configuration
VM_ID="200"
VM_NAME="ansible-control"
VM_NODE="Workstation-AMD"
VM_CPUS="2"
VM_MEMORY="4096"  # 4GB in MB
VM_DISK_SIZE="20"  # 20GB

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

check_vm_exists() {
    log_info "Checking if VM $VM_ID already exists..."
    
    # This would be implemented with Proxmox MCP tools in practice
    # For now, we'll provide manual instructions
    
    echo ""
    echo "=========================================="
    echo "VM CREATION INSTRUCTIONS"
    echo "=========================================="
    echo ""
    echo "Please create a VM in Proxmox with these specifications:"
    echo ""
    echo "VM Configuration:"
    echo "  • VM ID: $VM_ID"
    echo "  • VM Name: $VM_NAME"
    echo "  • Node: $VM_NODE"
    echo "  • CPUs: $VM_CPUS cores"
    echo "  • Memory: ${VM_MEMORY}MB (4GB)"
    echo "  • Disk: ${VM_DISK_SIZE}GB"
    echo "  • OS: Ubuntu 22.04 LTS Server"
    echo ""
    echo "Network Configuration:"
    echo "  • Bridge: vmbr0 (or your default bridge)"
    echo "  • Firewall: Enabled"
    echo "  • DHCP: Enabled (or set static IP)"
    echo ""
    echo "After VM creation, install Ubuntu 22.04 LTS with:"
    echo "  • Username: ubuntu"
    echo "  • Enable SSH server"
    echo "  • Install security updates"
    echo ""
    echo "Then run the post-install configuration:"
    echo "  sudo apt update && sudo apt upgrade -y"
    echo "  sudo apt install -y curl wget git"
    echo ""
    echo "Copy your SSH key:"
    echo "  ssh-copy-id ubuntu@<VM_IP>"
    echo ""
    echo "Update the inventory file with the VM's IP address:"
    echo "  vim infra/ansible/inventories/prod/hosts.yml"
    echo ""
    echo "Finally, run the Semaphore deployment:"
    echo "  ./infra/scripts/semaphore_bootstrap.sh"
    echo ""
    echo "=========================================="
}

create_vm_with_mcp() {
    log_info "Creating VM using Proxmox MCP tools..."
    
    # Note: This is a placeholder for when MCP tools are fully integrated
    # The actual implementation would use the mcp_proxmox_create_vm function
    
    log_warning "MCP VM creation not yet implemented in this script"
    log_info "Please use the manual instructions above"
    
    return 1
}

main() {
    log_info "Starting VM creation for Semaphore..."
    
    echo ""
    echo "VM Specifications:"
    echo "  ID: $VM_ID"
    echo "  Name: $VM_NAME"
    echo "  Node: $VM_NODE"
    echo "  CPUs: $VM_CPUS"
    echo "  Memory: ${VM_MEMORY}MB"
    echo "  Disk: ${VM_DISK_SIZE}GB"
    echo ""
    
    check_vm_exists
    
    log_info "After VM creation and configuration, run:"
    log_info "  ./infra/scripts/semaphore_bootstrap.sh"
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [--help]"
        echo ""
        echo "This script provides instructions for creating the Semaphore VM."
        echo ""
        echo "VM Specifications:"
        echo "  • ID: $VM_ID"
        echo "  • Name: $VM_NAME"
        echo "  • CPUs: $VM_CPUS"
        echo "  • Memory: ${VM_MEMORY}MB"
        echo "  • Disk: ${VM_DISK_SIZE}GB"
        echo ""
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
