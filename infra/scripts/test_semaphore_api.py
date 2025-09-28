#!/usr/bin/env python3
"""
Test Semaphore API endpoints to find correct structure
"""

import requests
import json

def test_api_endpoints():
    """Test various API endpoints to find the correct structure"""
    
    base_url = "http://172.23.5.22:3000"
    api_token = "ywg7silgm3-fxumm06rjdztw8th9dundrwe7fc73e2y="
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Test various endpoint patterns
    endpoints_to_test = [
        # Basic endpoints
        "/api",
        "/api/",
        "/api/version",
        "/api/status",
        
        # Project endpoints
        "/api/projects",
        "/api/project",
        "/api/project/",
        
        # Resource endpoints (different patterns)
        "/api/project/4/inventory",
        "/api/project/4/inventories", 
        "/api/project/4/inventory.json",
        "/api/inventory",
        "/api/inventories",
        "/api/inventory.json",
        
        # Repository endpoints
        "/api/project/4/repository",
        "/api/project/4/repositories",
        "/api/project/4/repository.json",
        "/api/repository",
        "/api/repositories",
        "/api/repository.json",
        
        # Key endpoints
        "/api/project/4/key",
        "/api/project/4/keys",
        "/api/project/4/key.json",
        "/api/key",
        "/api/keys",
        "/api/key.json",
        
        # Secret endpoints
        "/api/project/4/secret",
        "/api/project/4/secrets",
        "/api/project/4/secret.json",
        "/api/secret",
        "/api/secrets",
        "/api/secret.json",
        
        # Template endpoints
        "/api/project/4/template",
        "/api/project/4/templates",
        "/api/project/4/template.json",
        "/api/template",
        "/api/templates",
        "/api/template.json",
    ]
    
    print("🔍 Testing Semaphore API endpoints...")
    print("=" * 60)
    
    working_endpoints = []
    
    for endpoint in endpoints_to_test:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, headers=headers, timeout=5)
            status = response.status_code
            
            if status == 200:
                print(f"✅ {endpoint} - {status} OK")
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   📋 Returns array with {len(data)} items")
                    elif isinstance(data, dict):
                        print(f"   📄 Returns object with keys: {list(data.keys())}")
                    else:
                        print(f"   📝 Returns: {str(data)[:100]}...")
                except:
                    print(f"   📝 Returns non-JSON: {response.text[:100]}...")
                working_endpoints.append(endpoint)
                
            elif status == 404:
                print(f"❌ {endpoint} - {status} Not Found")
            elif status == 401:
                print(f"🔒 {endpoint} - {status} Unauthorized")
            elif status == 403:
                print(f"🚫 {endpoint} - {status} Forbidden")
            else:
                print(f"⚠️  {endpoint} - {status} {response.reason}")
                
        except requests.exceptions.RequestException as e:
            print(f"💥 {endpoint} - Error: {e}")
    
    print("\n" + "=" * 60)
    print(f"✅ Working endpoints found: {len(working_endpoints)}")
    for endpoint in working_endpoints:
        print(f"   • {endpoint}")
    
    return working_endpoints

if __name__ == "__main__":
    test_api_endpoints()
