#!/usr/bin/env python3
"""
Create Semaphore template for listing switch interfaces
"""

import sys
import json
import requests
from pathlib import Path

# Add the scripts directory to the path to import semaphore_api_client
sys.path.append(str(Path(__file__).parent))

from semaphore_api_client import SemaphoreAPIClient

def create_interface_listing_template():
    """Create a new Semaphore template for listing switch interfaces"""
    
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
    print(f"📁 Using project ID: {project_id}")
    
    # Check if template already exists
    templates = client.get_templates(project_id)
    existing_template = None
    for template in templates:
        if "interface" in template.get('name', '').lower() and "list" in template.get('name', '').lower():
            existing_template = template
            break
    
    if existing_template:
        print(f"⚠️  Interface listing template already exists: {existing_template['name']} (ID: {existing_template['id']})")
        return True
    
    # Get required IDs (inventory, repository, key)
    inventories = client.get_inventories(project_id) if hasattr(client, 'get_inventories') else []
    repositories = client.get_repositories(project_id) if hasattr(client, 'get_repositories') else []
    keys = client.get_ssh_keys(project_id) if hasattr(client, 'get_ssh_keys') else []
    
    # Use defaults if not found
    inventory_id = inventories[0]['id'] if inventories else 7
    repository_id = repositories[0]['id'] if repositories else 1
    key_id = keys[0]['id'] if keys else 1
    
    print(f"📋 Using inventory ID: {inventory_id}")
    print(f"📁 Using repository ID: {repository_id}")
    print(f"🔑 Using key ID: {key_id}")
    
    # Define survey variables for the interface listing template
    survey_variables = [
        {
            "name": "switch_name",
            "title": "Switch to Query",
            "required": True,
            "type": "enum",
            "description": "Select the switch to list interfaces for",
            "values": [
                {"name": "Arista Core Switch", "value": "arista_core"},
                {"name": "Cisco Nexus Switch", "value": "cisco_nexus"},
                {"name": "Access Layer Switch", "value": "access_switch"}
            ],
            "default_value": "arista_core"
        }
    ]
    
    # Create the template
    template_data = {
        "name": "List Switch Interfaces",
        "playbook": "playbooks/network/list_switch_interfaces.yml",
        "inventory_id": inventory_id,
        "repository_id": repository_id,
        "key_id": key_id,
        "survey_vars": json.dumps(survey_variables)
    }
    
    print("🔧 Creating interface listing template...")
    
    result = client.create_template(
        project_id=project_id,
        name=template_data["name"],
        playbook=template_data["playbook"],
        inventory_id=template_data["inventory_id"],
        key_id=template_data["key_id"],
        repository_id=template_data["repository_id"],
        arguments=template_data.get("arguments", [])
    )
    
    if result:
        print("✅ Successfully created interface listing template!")
        print(f"📋 Template ID: {result.get('id', 'Unknown')}")
        print(f"📝 Template Name: {result.get('name', 'Unknown')}")
        
        # Now update it with survey variables
        template_id = result.get('id')
        if template_id:
            update_result = client.update_template(
                project_id, 
                template_id, 
                survey_vars=json.dumps(survey_variables)
            )
            
            if update_result:
                print("✅ Successfully added survey variables to template!")
            else:
                print("⚠️  Template created but survey variables may need manual configuration")
        
        print("\n🎯 Interface listing template is ready!")
        print("Users can now:")
        print("  1. Select a switch from the dropdown")
        print("  2. See all available interfaces for that switch")
        print("  3. Get port descriptions and VLAN recommendations")
        print("  4. Use this info for VLAN assignment operations")
        
        return True
    else:
        print("❌ Failed to create interface listing template")
        return False

def main():
    """Main function"""
    print("🔧 Creating Semaphore template for interface listing...")
    
    success = create_interface_listing_template()
    
    if success:
        print("\n🎉 Operation completed successfully!")
        print("\n📋 Next steps:")
        print("  1. Go to Semaphore UI → Templates")
        print("  2. Find 'List Switch Interfaces' template")
        print("  3. Test it by selecting different switches")
        print("  4. Use the interface info for VLAN assignments")
        sys.exit(0)
    else:
        print("\n❌ Operation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
