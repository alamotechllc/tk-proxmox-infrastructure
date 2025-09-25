#!/usr/bin/env python3
"""
Fix Semaphore template update with correct app_id
"""

import sys
import json
import requests
from pathlib import Path

# Add the scripts directory to the path to import semaphore_api_client
sys.path.append(str(Path(__file__).parent))

from semaphore_api_client import SemaphoreAPIClient

def main():
    """Fix template update with correct app_id"""
    
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
    
    # Get current survey variables
    current_vars = vlan_template.get('survey_vars', [])
    print(f"📋 Current survey variables: {len(current_vars)}")
    
    # Check if port_interface and port_desc are missing
    existing_var_names = [var.get('name') for var in current_vars]
    
    missing_vars = []
    if 'port_interface' not in existing_var_names:
        missing_vars.append({
            "name": "port_interface",
            "title": "Port Interface",
            "required": True,
            "type": "string",
            "description": "Port interface to configure (e.g., Ethernet1/10)",
            "default_value": "Ethernet1/10"
        })
    
    if 'port_desc' not in existing_var_names:
        missing_vars.append({
            "name": "port_desc",
            "title": "Port Description", 
            "required": False,
            "type": "string",
            "description": "Port description",
            "default_value": "Ansible managed port"
        })
    
    if not missing_vars:
        print("✅ All required survey variables are already configured!")
        return True
    
    print(f"🔧 Adding {len(missing_vars)} missing survey variables...")
    
    # Combine existing and new variables
    updated_vars = current_vars + missing_vars
    
    # Update template with ALL required fields including app_id
    update_data = {
        "name": vlan_template.get('name'),
        "playbook": vlan_template.get('playbook'),
        "inventory_id": vlan_template.get('inventory_id'),
        "repository_id": vlan_template.get('repository_id'),
        "environment_id": vlan_template.get('environment_id'),
        "app_id": 1,  # Ansible app ID - this was missing!
        "survey_vars": json.dumps(updated_vars)
    }
    
    print(f"📝 Update data: {json.dumps(update_data, indent=2)}")
    
    url = f"{client.api_url}/project/{project_id}/templates/{template_id}"
    print(f"🌐 URL: {url}")
    
    try:
        response = client.session.put(url, json=update_data)
        print(f"📊 Response status: {response.status_code}")
        print(f"📊 Response content: {response.text}")
        
        if response.status_code == 200:
            print("✅ Successfully updated template with missing survey variables!")
            print("\n📋 Added variables:")
            for var in missing_vars:
                print(f"  - {var['name']}: {var['type']} ({'Required' if var.get('required') else 'Optional'})")
            
            print("\n🎯 Template is now complete and ready for use!")
            return True
        else:
            print(f"❌ Update failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Operation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Operation failed!")
        sys.exit(1)
