#!/usr/bin/env python3
"""
OPNsense API Endpoint Tester
Tests API endpoints based on official OPNsense documentation
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

def test_get_endpoint(endpoint, description=""):
    """Test a GET endpoint"""
    url = f"https://{OPNSENSE_HOST}/api/{endpoint}"
    
    try:
        response = requests.get(url, auth=(API_KEY, API_SECRET), verify=False, timeout=10)
        
        print(f"🔍 GET {endpoint}")
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

def test_post_endpoint(endpoint, data, description=""):
    """Test a POST endpoint"""
    url = f"https://{OPNSENSE_HOST}/api/{endpoint}"
    
    try:
        response = requests.post(
            url, 
            auth=(API_KEY, API_SECRET), 
            json=data,
            verify=False, 
            timeout=10
        )
        
        print(f"🔍 POST {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Success")
            try:
                data = response.json()
                if isinstance(data, dict):
                    print(f"   Keys: {list(data.keys())[:5]}...")
                    if 'rows' in data:
                        print(f"   Rows: {len(data['rows'])}")
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
    """Main test function"""
    print("🔥 OPNsense API Endpoint Testing")
    print("=" * 50)
    
    load_credentials()
    
    # Test endpoints based on official documentation
    search_data = {"current": 1, "rowCount": 10, "sort": {}, "searchPhrase": ""}
    
    # Core API endpoints to test
    endpoints_to_test = [
        # GET endpoints
        ("core/system/info", "GET", None, "System Information"),
        ("core/firmware/status", "GET", None, "Firmware Status"),
        ("core/firmware/info", "GET", None, "Firmware Info"),
        
        # POST endpoints (search operations)
        ("core/service/search", "POST", search_data, "Service Search"),
        ("core/firewall/rule/search", "POST", search_data, "Firewall Rules Search"),
        ("core/interfaces/search", "POST", search_data, "Interfaces Search"),
        ("core/dhcpv4/lease/search", "POST", search_data, "DHCP Leases Search"),
        ("core/routes/search", "POST", search_data, "Routes Search"),
        ("core/diagnostics/interface/list", "POST", search_data, "Interface Diagnostics"),
        ("core/diagnostics/interface/getInterfaceStatistics", "POST", {"interface": "lan"}, "Interface Statistics"),
    ]
    
    successful_endpoints = []
    
    print(f"Testing {len(endpoints_to_test)} endpoints on {OPNSENSE_HOST}...")
    print()
    
    for endpoint, method, data, description in endpoints_to_test:
        if method == "GET":
            if test_get_endpoint(endpoint, description):
                successful_endpoints.append(f"GET {endpoint}")
        elif method == "POST":
            if test_post_endpoint(endpoint, data, description):
                successful_endpoints.append(f"POST {endpoint}")
    
    print("=" * 50)
    print(f"✅ Successful endpoints: {len(successful_endpoints)}/{len(endpoints_to_test)}")
    
    if successful_endpoints:
        print("\n🎉 Working endpoints:")
        for endpoint in successful_endpoints:
            print(f"   • {endpoint}")
        
        print("\n📋 Next Steps:")
        print("1. Update Ansible playbooks with working endpoints")
        print("2. Create Semaphore templates for OPNsense automation")
        print("3. Test firewall rule management")
        print("4. Test interface monitoring")
    else:
        print("\n❌ No working endpoints found")
        print("\nTroubleshooting steps:")
        print("1. Verify API is enabled in OPNsense Web UI")
        print("2. Check API key permissions")
        print("3. Verify IP restrictions")
        print("4. Check OPNsense logs")

if __name__ == "__main__":
    main()
