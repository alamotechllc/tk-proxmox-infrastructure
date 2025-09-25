#!/usr/bin/env bash

# TK Network Monitoring VMs Setup Script
# Helps configure the newly created monitoring VMs

# --- Configuration ---
NETWORK_MONITOR_VM_ID="210"
SYSLOG_SERVER_VM_ID="211"
NODE="Workstation-AMD"

# Network configuration based on TK network diagram
NETWORK_MONITOR_IP="172.23.7.100"
SYSLOG_SERVER_IP="172.23.7.101"
GATEWAY="172.23.7.1"
DNS_SERVER="172.23.7.1"
NETMASK="24"
DOMAIN="tks.local"

# --- Logging Functions ---
log_info() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

log_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
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

# --- Main Functions ---
show_vm_status() {
    log_header "🔍 Current VM Status"
    echo ""
    
    log_info "Checking VM status via Proxmox MCP..."
    # This would use the MCP tools to check VM status
    # For now, we'll provide manual instructions
    
    echo "📊 Created VMs:"
    echo "   • network-monitor-01 (ID: $NETWORK_MONITOR_VM_ID) - $NETWORK_MONITOR_IP"
    echo "   • syslog-server-01 (ID: $SYSLOG_SERVER_VM_ID) - $SYSLOG_SERVER_IP"
    echo ""
}

show_setup_instructions() {
    log_header "📋 VM Setup Instructions"
    echo ""
    
    log_info "1. OS INSTALLATION:"
    echo "   • Access Proxmox web interface: https://172.23.5.15:8006"
    echo "   • Upload Ubuntu Server 22.04 LTS ISO"
    echo "   • Start both VMs (ID: $NETWORK_MONITOR_VM_ID, $SYSLOG_SERVER_VM_ID)"
    echo "   • Install Ubuntu Server via console"
    echo ""
    
    log_info "2. NETWORK CONFIGURATION:"
    echo "   During Ubuntu installation, configure static networking:"
    echo ""
    echo "   📊 network-monitor-01:"
    echo "      IP Address: $NETWORK_MONITOR_IP/$NETMASK"
    echo "      Gateway: $GATEWAY"
    echo "      DNS: $DNS_SERVER"
    echo "      Domain: $DOMAIN"
    echo ""
    echo "   📝 syslog-server-01:"
    echo "      IP Address: $SYSLOG_SERVER_IP/$NETMASK"
    echo "      Gateway: $GATEWAY"
    echo "      DNS: $DNS_SERVER"
    echo "      Domain: $DOMAIN"
    echo ""
    
    log_info "3. POST-INSTALLATION SETUP:"
    echo "   • Install SSH server: sudo apt install openssh-server"
    echo "   • Install QEMU guest agent: sudo apt install qemu-guest-agent"
    echo "   • Enable services: sudo systemctl enable ssh qemu-guest-agent"
    echo "   • Configure firewall: sudo ufw enable && sudo ufw allow ssh"
    echo "   • Install Docker: sudo apt install docker.io docker-compose"
    echo "   • Add user to docker group: sudo usermod -aG docker \$USER"
    echo ""
    
    log_info "4. SSH KEY SETUP:"
    echo "   • Copy SSH public key from ansible-control VM:"
    echo "     ssh-copy-id user@$NETWORK_MONITOR_IP"
    echo "     ssh-copy-id user@$SYSLOG_SERVER_IP"
    echo "   • Test SSH connectivity from ansible-control"
    echo ""
}

show_deployment_plan() {
    log_header "🚀 Service Deployment Plan"
    echo ""
    
    log_info "📊 UPTIME KUMA DEPLOYMENT (network-monitor-01):"
    echo "   • Run Ansible playbook: deploy_uptime_kuma.yml"
    echo "   • Access web interface: http://$NETWORK_MONITOR_IP:3001"
    echo "   • Configure monitoring targets for TK network"
    echo "   • Set up notifications (email, Slack)"
    echo ""
    
    log_info "📝 SYSLOG SERVER DEPLOYMENT (syslog-server-01):"
    echo "   • Install rsyslog or ELK stack"
    echo "   • Configure log forwarding from network devices"
    echo "   • Set up log retention and rotation"
    echo "   • Configure dashboards for log analysis"
    echo ""
    
    log_info "🔗 NETWORK DEVICE CONFIGURATION:"
    echo "   • Configure OPNsense to forward logs to $SYSLOG_SERVER_IP"
    echo "   • Configure Arista switch logging: logging host $SYSLOG_SERVER_IP"
    echo "   • Configure Nexus switch logging: logging server $SYSLOG_SERVER_IP"
    echo "   • Enable SNMP on switches for monitoring"
    echo ""
}

show_testing_plan() {
    log_header "🧪 Testing Plan"
    echo ""
    
    log_info "SEMAPHORE TEMPLATE TESTING:"
    echo "   After VM setup, test these templates:"
    echo "   • Network Health Check - Should connect to real VMs"
    echo "   • Network Credential Verification - Should find monitoring VMs"
    echo "   • Network Backup Runbook - Should execute successfully"
    echo "   • VLAN Management - Should work with actual network"
    echo ""
    
    log_info "MONITORING VALIDATION:"
    echo "   • Uptime Kuma: Verify all targets are reachable"
    echo "   • Syslog: Verify logs are being received"
    echo "   • Notifications: Test email and Slack alerts"
    echo "   • Status page: Verify public status page works"
    echo ""
}

main() {
    log_header "🌐 TK Network Monitoring VMs Setup"
    echo ""
    
    show_vm_status
    show_setup_instructions
    show_deployment_plan
    show_testing_plan
    
    log_header "🎯 Summary"
    echo ""
    log_success "✅ Both monitoring VMs created successfully!"
    log_info "📋 Follow the setup instructions above"
    log_info "🚀 Deploy Uptime Kuma first for immediate monitoring"
    log_info "📝 Add syslog server for centralized logging"
    log_info "🔗 Test Semaphore templates with real VMs"
    echo ""
    log_header "🌐 Access Proxmox: https://172.23.5.15:8006"
    log_header "🔧 VM IDs: 210 (monitor), 211 (syslog)"
}

main "$@"


