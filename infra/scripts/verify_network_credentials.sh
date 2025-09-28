#!/usr/bin/env bash
#
# Network Credential Verification Script
# Tests admin / 8fewWER8382 credentials on all network devices
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
PLAYBOOK="$ANSIBLE_DIR/playbooks/network/verify_credentials.yml"
INVENTORY="$ANSIBLE_DIR/inventories/prod/hosts.yml"

# Test credentials
TEST_USER="admin"
TEST_PASS="8fewWER8382"

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

Network Device Credential Verification Tool

DESCRIPTION:
    Tests the unified credentials (admin / 8fewWER8382) across all network devices
    to verify connectivity and authentication before creating Semaphore secrets.

OPTIONS:
    -h, --help              Show this help message
    -d, --device DEVICE     Test specific device only
    -t, --type TYPE         Test specific device type (arista|nexus|catalyst|opnsense|all)
    -q, --quick             Quick test (basic commands only)
    -v, --verbose           Verbose output
    -r, --report            Generate detailed report only

EXAMPLES:
    $0                                    # Test all devices
    $0 -d arista-core-01                 # Test specific device
    $0 -t catalyst                       # Test only Catalyst switches
    $0 -q                                # Quick connectivity test
    $0 -r                                # Generate report from previous test

DEVICE TYPES:
    arista      - Arista EOS switches
    nexus       - Cisco Nexus NX-OS switches
    catalyst    - Cisco Catalyst IOS-XE switches
    opnsense    - OPNsense firewall
    all         - All network devices (default)

CREDENTIALS BEING TESTED:
    Username: admin
    Password: 8fewWER8382
    Enable: 8fewWER8382

EOF
}

test_device_connectivity() {
    local device_filter="$1"
    local quick_test="$2"
    local verbose="$3"
    
    log_info "Testing network device credentials..."
    
    # Determine target hosts
    local target_hosts="all"
    case "$device_filter" in
        arista)
            target_hosts="arista_switches"
            ;;
        nexus)
            target_hosts="nexus_switches"
            ;;
        catalyst)
            target_hosts="catalyst_switches"
            ;;
        opnsense)
            target_hosts="opnsense_firewalls"
            ;;
        all)
            target_hosts="all"
            ;;
        *)
            # Specific device name
            target_hosts="$device_filter"
            ;;
    esac
    
    # Build ansible command
    local ansible_cmd=(
        "ansible-playbook"
        "-i" "$INVENTORY"
        "$PLAYBOOK"
        "--limit" "$target_hosts"
        "-e" "network_admin_user=$TEST_USER"
        "-e" "network_admin_pass=$TEST_PASS"
        "-e" "network_enable_pass=$TEST_PASS"
    )
    
    if [[ "$quick_test" == "true" ]]; then
        ansible_cmd+=("-e" "verification_mode=quick")
    fi
    
    if [[ "$verbose" == "true" ]]; then
        ansible_cmd+=("-vvv")
    else
        ansible_cmd+=("-v")
    fi
    
    log_info "Testing credentials on: $target_hosts"
    log_info "Credentials: $TEST_USER / [PROTECTED]"
    echo ""
    
    # Change to ansible directory and execute
    cd "$ANSIBLE_DIR"
    
    if "${ansible_cmd[@]}"; then
        log_success "Credential verification completed!"
        echo ""
        log_info "📁 Results available in: /tmp/credential_verification/"
        log_info "📋 View summary: cat /tmp/credential_verification/verification_summary_*.log"
        echo ""
        
        # Show quick summary
        if [[ -d "/tmp/credential_verification" ]]; then
            local latest_summary=$(ls -t /tmp/credential_verification/verification_summary_*.log 2>/dev/null | head -1)
            if [[ -n "$latest_summary" ]]; then
                log_header "📊 QUICK SUMMARY:"
                echo ""
                grep -E "(Total Devices|Successful|Failed|Success Rate)" "$latest_summary" | sed 's/^/  /'
                echo ""
            fi
        fi
        
        return 0
    else
        log_error "Credential verification failed!"
        echo ""
        log_info "Troubleshooting:"
        echo "  1. Check network connectivity to devices"
        echo "  2. Verify devices are configured with admin / 8fewWER8382"
        echo "  3. Check SSH/management access is enabled"
        echo "  4. Review logs in /tmp/credential_verification/"
        return 1
    fi
}

show_quick_connectivity_test() {
    log_header "🔍 Quick Connectivity Test"
    echo ""
    
    local devices=(
        "172.23.5.1:arista-core-01:Arista_Core"
        "172.23.5.2:nexus-agg-01:Nexus_Aggregation"
        "172.23.5.10:catalyst-access-01:Catalyst_Access_01"
        "172.23.5.11:catalyst-access-02:Catalyst_Access_02"
        "172.23.5.253:opnsense-fw-01:OPNsense_Firewall"
    )
    
    for device_info in "${devices[@]}"; do
        IFS=':' read -r ip hostname description <<< "$device_info"
        
        echo -n "Testing $description ($ip)... "
        
        # Test basic connectivity
        if timeout 5 bash -c "</dev/tcp/$ip/22" 2>/dev/null; then
            echo -e "${GREEN}SSH Port Open${NC}"
        else
            echo -e "${RED}SSH Port Closed${NC}"
        fi
    done
    
    echo ""
    log_info "For detailed authentication testing, run: $0"
}

generate_report_only() {
    log_header "📋 Credential Verification Report"
    echo ""
    
    if [[ ! -d "/tmp/credential_verification" ]]; then
        log_error "No verification results found. Run verification first."
        exit 1
    fi
    
    local latest_summary=$(ls -t /tmp/credential_verification/verification_summary_*.log 2>/dev/null | head -1)
    
    if [[ -n "$latest_summary" ]]; then
        log_info "Latest verification summary:"
        echo ""
        cat "$latest_summary"
    else
        log_error "No summary report found."
        exit 1
    fi
}

# Default values
DEVICE_FILTER="all"
QUICK_TEST="false"
VERBOSE="false"
REPORT_ONLY="false"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -d|--device)
            DEVICE_FILTER="$2"
            shift 2
            ;;
        -t|--type)
            DEVICE_FILTER="$2"
            shift 2
            ;;
        -q|--quick)
            QUICK_TEST="true"
            shift
            ;;
        -v|--verbose)
            VERBOSE="true"
            shift
            ;;
        -r|--report)
            REPORT_ONLY="true"
            shift
            ;;
        --connectivity-only)
            show_quick_connectivity_test
            exit 0
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
    log_header "🔐 Network Credential Verification Tool"
    echo ""
    
    if [[ "$REPORT_ONLY" == "true" ]]; then
        generate_report_only
        exit 0
    fi
    
    echo "Configuration:"
    echo "  Target: $DEVICE_FILTER"
    echo "  Credentials: $TEST_USER / [PROTECTED]"
    echo "  Quick Test: $QUICK_TEST"
    echo "  Verbose: $VERBOSE"
    echo ""
    
    test_device_connectivity "$DEVICE_FILTER" "$QUICK_TEST" "$VERBOSE"
}

main "$@"
