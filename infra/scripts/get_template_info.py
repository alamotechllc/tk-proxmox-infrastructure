#!/usr/bin/env python3
"""
Get Semaphore template information
"""

import sys
import json
import requests
from pathlib import Path

# Add the scripts directory to the path to import semaphore_api_client
sys.path.append(str(Path(__file__).parent))

from semaphore_api_client import SemaphoreAPIClient

def main():
    """Get template information"""
    
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
    
    # Print current template details
    print("\n📋 Current template details:")
    print(json.dumps(vlan_template, indent=2))
    
    return True

if __name__ == "__main__":
    main()
