#!/usr/bin/env bash
#
# Security Migration Script
# Converts environment variables to secure secrets in Semaphore
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
SEMAPHORE_URL="http://172.23.5.22:3000"
PROJECT_ID="4"

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

show_migration_plan() {
    log_header "🔒 SECURITY MIGRATION PLAN"
    echo ""
    echo "This script will help you migrate from environment variables to secure secrets."
    echo ""
    echo "CURRENT ENVIRONMENT VARIABLES TO MIGRATE:"
    echo ""
    echo "📡 Network Device Credentials:"
    echo "  • ARISTA_ADMIN_USER / ARISTA_ADMIN_PASS"
    echo "  • ARISTA_ENABLE_PASS"
    echo "  • NEXUS_ADMIN_USER / NEXUS_ADMIN_PASS"
    echo "  • CATALYST_ADMIN_USER / CATALYST_ADMIN_PASS / CATALYST_ENABLE_PASS"
    echo "  • Various SNMP communities"
    echo ""
    echo "🔥 Firewall Credentials:"
    echo "  • OPNSENSE_ADMIN_USER / OPNSENSE_ADMIN_PASS"
    echo "  • OPNSENSE_API_KEY / OPNSENSE_API_SECRET"
    echo ""
    echo "📊 Service Credentials:"
    echo "  • BACKUP_SERVER_USER / BACKUP_SERVER_PASS"
    echo "  • NMS_DATABASE_URL"
    echo ""
    echo "RECOMMENDED SECRET STRUCTURE:"
    echo ""
    echo "1. Arista Admin Credentials (login_password)"
    echo "2. Arista Enable Password (password)"
    echo "3. Nexus Admin Credentials (login_password)"
    echo "4. Catalyst Admin Credentials (login_password)"
    echo "5. Catalyst Enable Password (password)"
    echo "6. OPNsense Admin Credentials (login_password)"
    echo "7. OPNsense API Credentials (login_password)"
    echo "8. Network Backup Credentials (login_password)"
    echo "9. SNMP Communities (password)"
    echo ""
}

create_secret_template() {
    local secret_name="$1"
    local secret_type="$2"
    local description="$3"
    
    cat << EOF

==========================================
SECRET: $secret_name
==========================================
Type: $secret_type
Description: $description

To create via Semaphore Web Interface:
1. Go to: http://172.23.5.22:3000
2. Navigate: Network Infrastructure → Keys
3. Click: "Add Key"
4. Fill in:
   - Name: "$secret_name"
   - Type: $secret_type
   - Credentials: [Your actual credentials]

To create via API:
curl "$SEMAPHORE_URL/api/project/$PROJECT_ID/keys" -X POST \\
  -H "Cookie: \$COOKIE" \\
  -H "Content-Type: application/json" \\
  -d '{
    "project_id": $PROJECT_ID,
    "name": "$secret_name",
    "type": "$secret_type",
    $(if [[ "$secret_type" == "login_password" ]]; then
        echo '"login_password": {"login": "admin", "password": "YOUR_PASSWORD"}'
    elif [[ "$secret_type" == "password" ]]; then
        echo '"string": "YOUR_PASSWORD"'
    elif [[ "$secret_type" == "ssh" ]]; then
        echo '"ssh": {"login": "admin", "passphrase": "", "private_key": "YOUR_SSH_KEY"}'
    fi)
  }'

==========================================

EOF
}

show_playbook_updates() {
    log_header "📝 PLAYBOOK UPDATES REQUIRED"
    echo ""
    echo "After creating secrets, update playbooks to reference them:"
    echo ""
    echo "BEFORE (Environment Variables):"
    echo '  ansible_user: "{{ lookup('"'"'env'"'"', '"'"'ARISTA_ADMIN_USER'"'"') }}"'
    echo '  ansible_password: "{{ lookup('"'"'env'"'"', '"'"'ARISTA_ADMIN_PASS'"'"') }}"'
    echo ""
    echo "AFTER (Secrets):"
    echo '  ansible_user: "{{ arista_admin_credentials.login }}"'
    echo '  ansible_password: "{{ arista_admin_credentials.password }}"'
    echo ""
    echo "FILES TO UPDATE:"
    echo "  • infra/ansible/playbooks/network/backup_switches.yml"
    echo "  • infra/ansible/playbooks/network/vlan_port_assignment.yml"
    echo "  • infra/ansible/playbooks/network/port_management.yml"
    echo "  • All network device inventories"
    echo ""
}

interactive_migration() {
    log_header "🔄 Interactive Secret Migration"
    echo ""
    
    echo "This will guide you through creating each secret."
    echo "You can create them via web interface or provide credentials for API creation."
    echo ""
    
    read -p "Do you want to create secrets via web interface (w) or API (a)? [w/a]: " METHOD
    
    if [[ "$METHOD" == "w" || "$METHOD" == "W" ]]; then
        echo ""
        log_info "Web Interface Method Selected"
        echo ""
        echo "Please create the following secrets via the web interface:"
        echo "URL: $SEMAPHORE_URL"
        echo "Path: Network Infrastructure → Keys → Add Key"
        echo ""
        
        create_secret_template "Arista Admin Credentials" "login_password" "Admin login for Arista switches"
        create_secret_template "Arista Enable Password" "password" "Enable password for Arista switches"
        create_secret_template "Nexus Admin Credentials" "login_password" "Admin login for Nexus switches"
        create_secret_template "Catalyst Admin Credentials" "login_password" "Admin login for Catalyst switches"
        create_secret_template "Catalyst Enable Password" "password" "Enable password for Catalyst switches"
        create_secret_template "OPNsense Admin Credentials" "login_password" "Admin login for OPNsense firewall"
        create_secret_template "Network Backup Credentials" "login_password" "Credentials for backup operations"
        
    elif [[ "$METHOD" == "a" || "$METHOD" == "A" ]]; then
        echo ""
        log_info "API Method Selected"
        echo ""
        log_warning "You will need to provide actual credentials for API creation."
        echo "Credentials will be sent securely via API calls."
        echo ""
        
        read -p "Are you ready to provide actual device credentials? [y/N]: " CONFIRM
        if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
            log_info "Migration cancelled. Use web interface method instead."
            exit 0
        fi
        
        log_info "Please provide credentials for API migration..."
        echo "Note: This would require actual credential input here."
        
    else
        log_error "Invalid selection. Please choose 'w' for web interface or 'a' for API."
        exit 1
    fi
}

show_updated_inventory_syntax() {
    log_header "📋 UPDATED INVENTORY SYNTAX"
    echo ""
    echo "After creating secrets, your inventories will reference them like this:"
    echo ""
    cat << 'EOF'
# Updated Core Network Infrastructure Inventory
arista_switches:
  hosts:
    arista-core-01:
      ansible_host: 172.23.5.1
      ansible_connection: network_cli
      ansible_network_os: eos
      # UPDATED: Reference secrets instead of environment variables
      ansible_user: "{{ arista_admin_credentials.login }}"
      ansible_password: "{{ arista_admin_credentials.password }}"
      ansible_become_password: "{{ arista_enable_password.password }}"

nexus_switches:
  hosts:
    nexus-agg-01:
      ansible_host: 172.23.5.2
      ansible_connection: network_cli
      ansible_network_os: nxos
      # UPDATED: Reference secrets instead of environment variables
      ansible_user: "{{ nexus_admin_credentials.login }}"
      ansible_password: "{{ nexus_admin_credentials.password }}"

catalyst_switches:
  hosts:
    catalyst-access-01:
      ansible_host: 172.23.5.10
      ansible_connection: network_cli
      ansible_network_os: ios
      # UPDATED: Reference secrets instead of environment variables
      ansible_user: "{{ catalyst_admin_credentials.login }}"
      ansible_password: "{{ catalyst_admin_credentials.password }}"
      ansible_become_password: "{{ catalyst_enable_password.password }}"
EOF
    echo ""
}

main() {
    log_header "🔒 SEMAPHORE SECURITY MIGRATION TOOL"
    echo ""
    
    show_migration_plan
    echo ""
    
    read -p "Proceed with migration planning? [y/N]: " PROCEED
    if [[ "$PROCEED" != "y" && "$PROCEED" != "Y" ]]; then
        log_info "Migration cancelled"
        exit 0
    fi
    
    interactive_migration
    show_playbook_updates
    show_updated_inventory_syntax
    
    echo ""
    log_success "Migration planning complete!"
    echo ""
    log_info "Next steps:"
    echo "1. Create secrets via chosen method"
    echo "2. Update playbooks to reference secrets"
    echo "3. Test operations with new secrets"
    echo "4. Remove old environment variables"
    echo ""
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        show_migration_plan
        exit 0
        ;;
    --template)
        create_secret_template "Example Secret" "login_password" "Example description"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
