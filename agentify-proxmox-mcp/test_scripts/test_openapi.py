#!/usr/bin/env python3
"""
Test OpenAPI functionality
"""
import requests
import json
import os

# Get base URL from environment variable or use default localhost
BASE_URL = os.getenv('OPENAPI_BASE_URL', 'http://localhost:8811')

def test_basic_endpoints():
    """Test basic API endpoints"""
    
    print("🔍 Test basic API endpoints")
    print(f"🌐 Using base URL: {BASE_URL}")
    print("=" * 50)
    
    # Test get nodes
    try:
        response = requests.post(f"{BASE_URL}/get_nodes")
        print(f"✅ get_nodes: {response.status_code} - {len(response.text)} chars")
    except Exception as e:
        print(f"❌ get_nodes error: {e}")
    
    # Test get VM list
    try:
        response = requests.post(f"{BASE_URL}/get_vms")
        print(f"✅ get_vms: {response.status_code} - {len(response.text)} chars")
        if response.status_code == 200:
            # Check if our test VMs are included
            if "test-vm" in response.text:
                print("  📋 Test VM found")
    except Exception as e:
        print(f"❌ get_vms error: {e}")

def test_vm_creation_api():
    """Test VM creation API"""
    
    print("\n🎉 Test VM creation API - user requested configuration")
    print("=" * 50)
    print("Configuration: 1 CPU core, 2GB RAM, 10GB storage")
    
    # VM creation parameters
    create_data = {
        "node": "pve",
        "vmid": "996",  # Use new VM ID
        "name": "user-requested-vm",
        "cpus": 1,
        "memory": 2048,  # 2GB in MB
        "disk_size": 10  # 10GB
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/create_vm",
            json=create_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📡 API response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ VM creation successful!")
            print(f"📄 Response content: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ VM creation failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server - please ensure OpenAPI service is running")
    except Exception as e:
        print(f"❌ API call error: {e}")

def test_vm_power_api():
    """Test VM power management API"""
    
    print("\n🚀 Test VM power management API")
    print("=" * 50)
    
    # Test starting VM 101 (VPN-Server)
    start_data = {
        "node": "pve",
        "vmid": "101"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/start_vm",
            json=start_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📡 Start VM 101 response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ VM start command successful!")
            print(f"📄 Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ VM start failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
    except Exception as e:
        print(f"❌ API call error: {e}")

def list_available_apis():
    """List all available API endpoints"""
    
    print("\n📋 Available API endpoints")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})
            
            print(f"Found {len(paths)} API endpoints:")
            for path, methods in paths.items():
                for method, details in methods.items():
                    summary = details.get("summary", "No summary")
                    print(f"  • {method.upper()} {path} - {summary}")
        else:
            print(f"❌ Cannot get API specification: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Get API list error: {e}")

if __name__ == "__main__":
    print("🔍 ProxmoxMCP OpenAPI functionality test")
    print("=" * 60)
    
    # List available APIs
    list_available_apis()
    
    # Test basic functionality
    test_basic_endpoints()
    
    # Test VM creation functionality
    test_vm_creation_api()
    
    # Test VM power management
    test_vm_power_api()
    
    print("\n✅ All tests completed")
    print("\n💡 Usage instructions:")
    print("When user says 'Can you create a VM with 1 cpu core and 2 GB ram with 10GB of storage disk',")
    print("the AI assistant can call create_vm API to complete the task!")
    print(f"\n🔧 To test with different server, set environment variable:")
    print("export OPENAPI_BASE_URL=http://your-server:8811") 