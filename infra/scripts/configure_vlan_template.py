#!/usr/bin/env python3
"""
Configure Semaphore Template for VLAN Assignment
Uses Semaphore API to add survey variables to the template
"""

import sys
import os
import json
import requests
from pathlib import Path

# Add the scripts directory to the path to import semaphore_api_client
sys.path.append(str(Path(__file__).parent))

from semaphore_api_client import SemaphoreAPIClient

def configure_vlan_template():
    """Configure the VLAN assignment template with survey variables"""
    
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
    
    # Get current templates
    templates = client.get_templates(project_id)
    print(f"📋 Found {len(templates)} templates")
    
    # Find the VLAN assignment template
    vlan_template = None
    for template in templates:
        if "vlan" in template.get('name', '').lower():
            vlan_template = template
            break
    
    if not vlan_template:
        print("❌ VLAN assignment template not found")
        print("Available templates:")
        for template in templates:
            print(f"  - {template.get('name')} (ID: {template.get('id')})")
        return False
    
    template_id = vlan_template['id']
    print(f"🎯 Found VLAN template: {vlan_template['name']} (ID: {template_id})")
    
    # Define survey variables
    survey_variables = [
        {
            "name": "switch_name",
            "type": "multiple_choice",
            "description": "Target switch to configure",
            "required": True,
            "default": "arista_core",
            "choices": [
                {"value": "arista_core", "label": "Arista Core Switch (tks-sw-arista-core-1)"},
                {"value": "cisco_nexus", "label": "Cisco Nexus Switch (tks-sw-cis-nexus-1)"},
                {"value": "access_switch", "label": "Access Layer Switch (8-port)"}
            ]
        },
        {
            "name": "port_interface", 
            "type": "string",
            "description": "Port interface to configure (e.g., Ethernet1/10)",
            "required": True,
            "default": "Ethernet1/10"
        },
        {
            "name": "vlan_id",
            "type": "multiple_choice", 
            "description": "VLAN ID to assign",
            "required": True,
            "default": "3",
            "choices": [
                {"value": "2", "label": "SERVERS (172.23.2.0/24)"},
                {"value": "3", "label": "WORKSTATIONS (172.23.3.0/24)"},
                {"value": "4", "label": "GUEST (172.23.4.0/24)"},
                {"value": "5", "label": "IOT (172.23.5.0/24)"},
                {"value": "6", "label": "GAMING (172.23.6.0/24)"},
                {"value": "7", "label": "MANAGEMENT (172.23.7.0/24)"}
            ]
        },
        {
            "name": "port_desc",
            "type": "string",
            "description": "Port description",
            "required": False,
            "default": "Ansible managed port"
        }
    ]
    
    # Update template with survey variables
    print("🔧 Updating template with survey variables...")
    
    update_data = {
        "survey_vars": json.dumps(survey_variables)
    }
    
    result = client.update_template(project_id, template_id, **update_data)
    
    if result:
        print("✅ Successfully updated template with survey variables!")
        print("\n📋 Survey variables added:")
        for var in survey_variables:
            print(f"  - {var['name']}: {var['type']} ({'Required' if var.get('required') else 'Optional'})")
        
        print("\n🎯 Template is now ready for use!")
        print("Users will see a form with dropdowns for switch selection and VLAN assignment.")
        return True
    else:
        print("❌ Failed to update template")
        return False

def test_template_execution():
    """Test the template execution with sample data"""
    
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
        print("❌ Failed to authenticate for testing")
        return False
    
    project_id = config['projects']['network_infrastructure']['id']
    
    # Find the VLAN template
    templates = client.get_templates(project_id)
    vlan_template = None
    for template in templates:
        if "vlan" in template.get('name', '').lower():
            vlan_template = template
            break
    
    if not vlan_template:
        print("❌ VLAN template not found for testing")
        return False
    
    template_id = vlan_template['id']
    
    # Test with sample data
    print("🧪 Testing template execution with sample data...")
    
    test_vars = {
        "switch_name": "arista_core",
        "port_interface": "Ethernet1/10", 
        "vlan_id": "3",
        "port_desc": "Test Port Assignment"
    }
    
    print(f"📝 Test variables: {test_vars}")
    
    # Run template in dry-run mode
    result = client.run_template(
        project_id=project_id,
        template_id=template_id,
        debug=False,
        dry_run=True,
        extra_vars=test_vars
    )
    
    if result:
        print("✅ Template test execution successful!")
        print(f"📊 Result: {result}")
        return True
    else:
        print("❌ Template test execution failed")
        return False

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("🧪 Testing template execution...")
        success = test_template_execution()
    else:
        print("🔧 Configuring Semaphore template...")
        success = configure_vlan_template()
    
    if success:
        print("\n🎉 Operation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Operation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
