#!/usr/bin/env python3
"""
Debug Semaphore API 400 error
"""

import sys
import json
import requests
from pathlib import Path

# Add the scripts directory to the path to import semaphore_api_client
sys.path.append(str(Path(__file__).parent))

from semaphore_api_client import SemaphoreAPIClient

def debug_api_call():
    """Debug the API call to understand the 400 error"""
    
    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "semaphore_config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Initialize Semaphore client
    semaphore_config = config['semaphore']
    client = SemaphoreAPIClient(
        base_url=semaphore_config['base_url'],
        username=semaphore_config['username'],
        password=semaphore_config['password']
    )
    
    # Authenticate
    if not client.authenticate():
        print("❌ Failed to authenticate with Semaphore")
        return False
    
    print("✅ Successfully authenticated with Semaphore")
    
    # Get project ID
    project_id = config['projects']['network_infrastructure']['id']
    
    # Get current templates
    templates = client.get_templates(project_id)
    
    # Find the VLAN assignment template
    vlan_template = None
    for template in templates:
        if "vlan" in template.get('name', '').lower():
            vlan_template = template
            break
    
    if not vlan_template:
        print("❌ VLAN assignment template not found")
        return False
    
    template_id = vlan_template['id']
    print(f"🎯 Found VLAN template: {vlan_template['name']} (ID: {template_id})")
    
    # Let's try a minimal update first
    print("\n🔍 Testing minimal update...")
    
    # Try updating just the name to see if the API works at all
    minimal_update = {
        "name": "Switch-Specific VLAN Assignment"  # Same name, just testing
    }
    
    print(f"📝 Minimal update data: {minimal_update}")
    
    # Make the request manually to see the exact error
    url = f"{client.api_url}/project/{project_id}/templates/{template_id}"
    print(f"🌐 URL: {url}")
    
    try:
        response = client.session.put(url, json=minimal_update)
        print(f"📊 Response status: {response.status_code}")
        print(f"📊 Response headers: {dict(response.headers)}")
        print(f"📊 Response content: {response.text}")
        
        if response.status_code == 200:
            print("✅ Minimal update successful!")
            return True
        else:
            print(f"❌ Minimal update failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False
    
    # Now let's try to understand what fields are required
    print("\n🔍 Checking what fields are required for template updates...")
    
    # Get the template again to see current structure
    template_details = client.get_project(project_id)
    if template_details:
        print("📋 Project details:")
        print(json.dumps(template_details, indent=2))
    
    return False

def test_different_update_approaches():
    """Test different approaches to updating the template"""
    
    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "semaphore_config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Initialize Semaphore client
    semaphore_config = config['semaphore']
    client = SemaphoreAPIClient(
        base_url=semaphore_config['base_url'],
        username=semaphore_config['username'],
        password=semaphore_config['password']
    )
    
    if not client.authenticate():
        print("❌ Failed to authenticate with Semaphore")
        return False
    
    project_id = config['projects']['network_infrastructure']['id']
    
    # Get current templates
    templates = client.get_templates(project_id)
    
    # Find the VLAN assignment template
    vlan_template = None
    for template in templates:
        if "vlan" in template.get('name', '').lower():
            vlan_template = template
            break
    
    if not vlan_template:
        print("❌ VLAN assignment template not found")
        return False
    
    template_id = vlan_template['id']
    
    # Test 1: Try updating with all current fields preserved
    print("\n🧪 Test 1: Update with all current fields...")
    
    update_data = {
        "name": vlan_template.get('name'),
        "playbook": vlan_template.get('playbook'),
        "inventory_id": vlan_template.get('inventory_id'),
        "repository_id": vlan_template.get('repository_id'),
        "environment_id": vlan_template.get('environment_id'),
        "survey_vars": json.dumps(vlan_template.get('survey_vars', []))
    }
    
    print(f"📝 Update data: {json.dumps(update_data, indent=2)}")
    
    url = f"{client.api_url}/project/{project_id}/templates/{template_id}"
    
    try:
        response = client.session.put(url, json=update_data)
        print(f"📊 Response status: {response.status_code}")
        print(f"📊 Response content: {response.text}")
        
        if response.status_code == 200:
            print("✅ Test 1 successful!")
            return True
        else:
            print(f"❌ Test 1 failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test 1 request failed: {e}")
    
    # Test 2: Try using the API client method
    print("\n🧪 Test 2: Using API client method...")
    
    try:
        result = client.update_template(project_id, template_id, **update_data)
        print(f"📊 Result: {result}")
        
        if result:
            print("✅ Test 2 successful!")
            return True
        else:
            print("❌ Test 2 failed")
            
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
    
    return False

def main():
    """Main debug function"""
    print("🔍 Debugging Semaphore API 400 error...")
    
    # First, test minimal update
    if debug_api_call():
        print("\n✅ Minimal update works, investigating further...")
        test_different_update_approaches()
    else:
        print("\n❌ Even minimal update fails, checking API structure...")

if __name__ == "__main__":
    main()
