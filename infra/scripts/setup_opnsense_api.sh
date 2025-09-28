#!/bin/bash

# OPNsense API Setup Script
# Configures API access and tests connectivity

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
OPNSENSE_HOST="172.23.5.1"
PROJECT_ROOT="/Users/mike.turner/APP_Projects/tk-proxmox"
SECRETS_DIR="${PROJECT_ROOT}/infra/secrets"
API_CREDENTIALS_FILE="${SECRETS_DIR}/opnsense-api-credentials.txt"

echo -e "${BLUE}🔥 OPNsense API Setup Script${NC}"
echo -e "${BLUE}============================${NC}"
echo ""

# Check if credentials file exists
if [ ! -f "$API_CREDENTIALS_FILE" ]; then
    echo -e "${RED}❌ API credentials file not found: $API_CREDENTIALS_FILE${NC}"
    exit 1
fi

# Extract credentials
API_KEY=$(grep 'key=' "$API_CREDENTIALS_FILE" | cut -d'=' -f2 | tr -d '\r\n')
API_SECRET=$(grep 'secret=' "$API_CREDENTIALS_FILE" | cut -d'=' -f2 | tr -d '\r\n')

echo -e "${GREEN}✅ API Credentials Loaded${NC}"
echo -e "   Host: $OPNSENSE_HOST"
echo -e "   API Key: ${API_KEY:0:20}..."
echo -e "   API Secret: ${API_SECRET:0:20}..."
echo ""

# Test network connectivity
echo -e "${YELLOW}🔍 Testing Network Connectivity...${NC}"
if ping -c 1 -W 3 "$OPNSENSE_HOST" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ OPNsense host is reachable${NC}"
else
    echo -e "${RED}❌ Cannot reach OPNsense host: $OPNSENSE_HOST${NC}"
    echo -e "${YELLOW}   Please check network connectivity and firewall rules${NC}"
fi

# Test API connectivity
echo -e "${YELLOW}🧪 Testing API Connectivity...${NC}"
API_RESPONSE=$(curl -k -s -w "%{http_code}" -u "${API_KEY}:${API_SECRET}" \
    "https://${OPNSENSE_HOST}/api/core/system/info" \
    -o /tmp/opnsense_api_response.json)

HTTP_CODE="${API_RESPONSE: -3}"
API_BODY=$(cat /tmp/opnsense_api_response.json 2>/dev/null || echo "")

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ API connection successful!${NC}"
    echo -e "${GREEN}   HTTP Status: $HTTP_CODE${NC}"
    
    # Parse and display system info
    if [ -n "$API_BODY" ]; then
        echo -e "${BLUE}📊 OPNsense System Information:${NC}"
        echo "$API_BODY" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'   Version: {data.get(\"version\", \"Unknown\")}')
    print(f'   Uptime: {data.get(\"uptime\", \"Unknown\")}')
    print(f'   CPU Usage: {data.get(\"cpu_usage\", \"Unknown\")}%')
    print(f'   Memory Usage: {data.get(\"memory_usage\", \"Unknown\")}%')
except:
    print('   Unable to parse system information')
" 2>/dev/null || echo "   Unable to parse system information"
    fi
else
    echo -e "${RED}❌ API connection failed${NC}"
    echo -e "${RED}   HTTP Status: $HTTP_CODE${NC}"
    echo -e "${YELLOW}   Response: $API_BODY${NC}"
    
    # Provide troubleshooting steps
    echo -e "${YELLOW}🔧 Troubleshooting Steps:${NC}"
    echo -e "   1. Verify OPNsense API is enabled in Web UI"
    echo -e "   2. Check API key permissions and IP restrictions"
    echo -e "   3. Ensure HTTPS is accessible on port 443"
    echo -e "   4. Verify firewall rules allow API access"
    echo -e "   5. Check OPNsense logs for authentication errors"
fi

# Create Semaphore secrets configuration
echo -e "${YELLOW}📋 Creating Semaphore Secrets Configuration...${NC}"

cat > "${PROJECT_ROOT}/infra/opnsense_semaphore_secrets.md" << EOF
# OPNsense API Secrets for Semaphore

## Required Secrets

Add these secrets to your Semaphore project:

### 1. OPNsense API Key
- **Name**: \`OPNsense API Key\`
- **Type**: \`Text\`
- **Value**: \`$API_KEY\`
- **Description**: API key for OPNsense authentication

### 2. OPNsense API Secret
- **Name**: \`OPNsense API Secret\`
- **Type**: \`Password\`
- **Value**: \`$API_SECRET\`
- **Description**: API secret for OPNsense authentication

## Adding Secrets to Semaphore

1. Go to: http://172.23.5.22:3000
2. Navigate to: **Project Settings** → **Secrets**
3. Click: **"Create new secret"**
4. Add both secrets with the values above

## Testing Templates

After adding secrets, test the OPNsense templates:
- OPNsense Firewall Management
- OPNsense DHCP Management  
- OPNsense Health Monitoring

## Security Notes

- Keep these credentials secure
- Rotate API keys regularly
- Monitor API usage for security
- Use IP restrictions in OPNsense
EOF

echo -e "${GREEN}✅ Semaphore secrets configuration created${NC}"
echo -e "${GREEN}   File: ${PROJECT_ROOT}/infra/opnsense_semaphore_secrets.md${NC}"

# Create test script
echo -e "${YELLOW}🧪 Creating API Test Script...${NC}"

cat > "${PROJECT_ROOT}/infra/scripts/test_opnsense_api.py" << 'EOF'
#!/usr/bin/env python3
"""
OPNsense API Test Script
Tests various API endpoints to verify functionality
"""

import requests
import json
import sys
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings for testing
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Configuration
OPNSENSE_HOST = "172.23.7.1"
API_KEY = ""  # Will be loaded from credentials file
API_SECRET = ""  # Will be loaded from credentials file

def load_credentials():
    """Load API credentials from file"""
    global API_KEY, API_SECRET
    
    try:
        with open('infra/secrets/opnsense-api-credentials.txt', 'r') as f:
            for line in f:
                if line.startswith('key='):
                    API_KEY = line.strip().split('=', 1)[1]
                elif line.startswith('secret='):
                    API_SECRET = line.strip().split('=', 1)[1]
        
        if not API_KEY or not API_SECRET:
            print("❌ Failed to load API credentials")
            sys.exit(1)
            
        print(f"✅ Credentials loaded: {API_KEY[:20]}...")
        
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        sys.exit(1)

def test_api_endpoint(endpoint, description):
    """Test a specific API endpoint"""
    url = f"https://{OPNSENSE_HOST}/api/{endpoint}"
    
    try:
        response = requests.get(url, auth=(API_KEY, API_SECRET), verify=False, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {description}: OK")
            return True
        else:
            print(f"❌ {description}: Failed (HTTP {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ {description}: Error - {e}")
        return False

def main():
    """Main test function"""
    print("🔥 OPNsense API Endpoint Tests")
    print("=" * 40)
    
    load_credentials()
    
    # Test endpoints
    endpoints = [
        ("core/system/info", "System Information"),
        ("core/interface/list", "Interface List"),
        ("core/firewall/rule/list", "Firewall Rules"),
        ("core/dhcp/lease/list", "DHCP Leases"),
    ]
    
    results = []
    for endpoint, description in endpoints:
        results.append(test_api_endpoint(endpoint, description))
    
    print("\n" + "=" * 40)
    success_count = sum(results)
    total_count = len(results)
    
    if success_count == total_count:
        print(f"🎉 All tests passed! ({success_count}/{total_count})")
        sys.exit(0)
    else:
        print(f"⚠️  Some tests failed ({success_count}/{total_count})")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

chmod +x "${PROJECT_ROOT}/infra/scripts/test_opnsense_api.py"
echo -e "${GREEN}✅ API test script created${NC}"
echo -e "${GREEN}   File: ${PROJECT_ROOT}/infra/scripts/test_opnsense_api.py${NC}"

# Summary
echo ""
echo -e "${BLUE}🎯 Setup Complete!${NC}"
echo -e "${BLUE}=================${NC}"
echo ""
echo -e "${GREEN}Next Steps:${NC}"
echo -e "1. Add API secrets to Semaphore (see opnsense_semaphore_secrets.md)"
echo -e "2. Test API connectivity: python3 infra/scripts/test_opnsense_api.py"
echo -e "3. Deploy OPNsense templates to Semaphore"
echo -e "4. Test firewall management automation"
echo ""
echo -e "${YELLOW}Files Created:${NC}"
echo -e "• infra/secrets/opnsense-api-credentials.txt"
echo -e "• infra/opnsense_semaphore_secrets.md"
echo -e "• infra/scripts/test_opnsense_api.py"
echo ""
echo -e "${BLUE}Ready for OPNsense automation! 🔥${NC}"
