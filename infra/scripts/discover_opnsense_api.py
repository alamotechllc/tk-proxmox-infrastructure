#!/usr/bin/env python3
"""
OPNsense API Discovery Script
Discovers available API endpoints and tests connectivity
"""

import requests
import json
import sys
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings for testing
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Configuration
OPNSENSE_HOST = "172.23.5.1"
API_KEY = ""
API_SECRET = ""

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

def test_endpoint(endpoint, description=""):
    """Test a specific API endpoint"""
    url = f"https://{OPNSENSE_HOST}{endpoint}"
    
    try:
        response = requests.get(url, auth=(API_KEY, API_SECRET), verify=False, timeout=10)
        
        print(f"🔍 {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Success")
            try:
                data = response.json()
                if isinstance(data, dict):
                    print(f"   Keys: {list(data.keys())[:5]}...")
                elif isinstance(data, list):
                    print(f"   Items: {len(data)}")
            except:
                print(f"   Response: {response.text[:100]}...")
        else:
            print(f"   ❌ Failed: {response.text}")
        
        print()
        return response.status_code == 200
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print()
        return False

def main():
    """Main discovery function"""
    print("🔥 OPNsense API Discovery")
    print("=" * 50)
    
    load_credentials()
    
    # Common OPNsense API endpoints to test
    endpoints_to_test = [
        # Root endpoints
        ("/api", "Root API endpoint"),
        ("/api/", "Root API endpoint (with slash)"),
        
        # Core endpoints
        ("/api/core", "Core module"),
        ("/api/core/", "Core module (with slash)"),
        ("/api/core/system", "System module"),
        ("/api/core/system/", "System module (with slash)"),
        ("/api/core/system/info", "System info"),
        ("/api/core/system/info/", "System info (with slash)"),
        ("/api/core/interface", "Interface module"),
        ("/api/core/interface/", "Interface module (with slash)"),
        ("/api/core/interface/list", "Interface list"),
        ("/api/core/interface/list/", "Interface list (with slash)"),
        
        # Firewall endpoints
        ("/api/core/firewall", "Firewall module"),
        ("/api/core/firewall/", "Firewall module (with slash)"),
        ("/api/core/firewall/rule", "Firewall rules"),
        ("/api/core/firewall/rule/", "Firewall rules (with slash)"),
        ("/api/core/firewall/rule/list", "Firewall rule list"),
        ("/api/core/firewall/rule/list/", "Firewall rule list (with slash)"),
        
        # DHCP endpoints
        ("/api/core/dhcp", "DHCP module"),
        ("/api/core/dhcp/", "DHCP module (with slash)"),
        ("/api/core/dhcp/lease", "DHCP leases"),
        ("/api/core/dhcp/lease/", "DHCP leases (with slash)"),
        ("/api/core/dhcp/lease/list", "DHCP lease list"),
        ("/api/core/dhcp/lease/list/", "DHCP lease list (with slash)"),
        
        # Alternative endpoint formats
        ("/api/system/info", "System info (alt format)"),
        ("/api/interfaces", "Interfaces (alt format)"),
        ("/api/firewall/rules", "Firewall rules (alt format)"),
        ("/api/dhcp/leases", "DHCP leases (alt format)"),
        
        # Version endpoints
        ("/api/version", "API version"),
        ("/api/status", "API status"),
        ("/api/health", "API health"),
    ]
    
    successful_endpoints = []
    
    print(f"Testing {len(endpoints_to_test)} endpoints on {OPNSENSE_HOST}...")
    print()
    
    for endpoint, description in endpoints_to_test:
        if test_endpoint(endpoint, description):
            successful_endpoints.append(endpoint)
    
    print("=" * 50)
    print(f"✅ Successful endpoints: {len(successful_endpoints)}/{len(endpoints_to_test)}")
    
    if successful_endpoints:
        print("\n🎉 Working endpoints:")
        for endpoint in successful_endpoints:
            print(f"   • {endpoint}")
    else:
        print("\n❌ No working endpoints found")
        print("\nTroubleshooting steps:")
        print("1. Verify API is enabled in OPNsense Web UI")
        print("2. Check API key permissions")
        print("3. Verify IP restrictions")
        print("4. Check OPNsense logs")

if __name__ == "__main__":
    main()
