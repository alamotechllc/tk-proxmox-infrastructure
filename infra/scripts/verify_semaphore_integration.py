#!/usr/bin/env python3
"""
Verify Semaphore API Integration
Confirms that API-created resources are visible in Semaphore UI
"""

from semaphore_token_client import SemaphoreTokenClient
import json

def verify_integration():
    """Verify that API integration is working correctly"""
    
    print("🔍 === SEMAPHORE API INTEGRATION VERIFICATION ===")
    print()
    
    # Initialize client
    client = SemaphoreTokenClient('http://172.23.5.22:3000', api_token='ywg7silgm3-fxumm06rjdztw8th9dundrwe7fc73e2y=')
    
    # Test authentication
    print("🔐 Authentication Test:")
    if client.authenticated:
        print("   ✅ API token authentication successful")
    else:
        print("   ❌ Authentication failed")
        return False
    
    # Get projects
    print("\n📋 Projects:")
    projects = client.get_projects()
    print(f"   Found {len(projects)} projects:")
    for project in projects:
        print(f"   • {project['name']} (ID: {project['id']})")
    
    # Focus on Network Infrastructure project
    network_project = None
    for project in projects:
        if project['name'] == 'Network Infrastructure':
            network_project = project
            break
    
    if not network_project:
        print("   ❌ Network Infrastructure project not found")
        return False
    
    project_id = network_project['id']
    print(f"\n🎯 Network Infrastructure Project (ID: {project_id}):")
    
    # Check repositories
    print("\n📁 Repositories:")
    repositories = client.get_repositories(project_id)
    print(f"   Found {len(repositories)} repositories:")
    for repo in repositories:
        print(f"   • {repo['name']} (ID: {repo['id']})")
        print(f"     URL: {repo.get('git_url', 'N/A')}")
        print(f"     SSH Key: {repo.get('ssh_key_id', 'N/A')}")
    
    # Check inventories
    print("\n📦 Inventories:")
    inventories = client.get_inventories(project_id)
    print(f"   Found {len(inventories)} inventories:")
    for inv in inventories:
        print(f"   • {inv['name']} (ID: {inv['id']})")
        print(f"     Type: {inv.get('type', 'N/A')}")
    
    # Check SSH keys
    print("\n🔑 SSH Keys:")
    keys = client.get_ssh_keys(project_id)
    print(f"   Found {len(keys)} SSH keys:")
    for key in keys:
        print(f"   • {key['name']} (ID: {key['id']})")
    
    # Check templates
    print("\n📋 Templates:")
    templates = client.get_templates(project_id)
    print(f"   Found {len(templates)} templates:")
    for template in templates:
        print(f"   • {template['name']} (ID: {template['id']})")
        print(f"     Playbook: {template.get('playbook', 'N/A')}")
        print(f"     Inventory: {template.get('inventory_id', 'N/A')}")
        print(f"     Repository: {template.get('repository_id', 'N/A')}")
    
    # Summary
    print(f"\n✅ === INTEGRATION VERIFICATION COMPLETE ===")
    print(f"   🔐 Authentication: {'✅ Working' if client.authenticated else '❌ Failed'}")
    print(f"   📋 Projects: {len(projects)} found")
    print(f"   📁 Repositories: {len(repositories)} found")
    print(f"   📦 Inventories: {len(inventories)} found")
    print(f"   🔑 SSH Keys: {len(keys)} found")
    print(f"   📋 Templates: {len(templates)} found")
    
    print(f"\n🌐 Access Semaphore UI at: http://172.23.5.22:3000")
    print(f"   Login: admin / 8fewWER8382")
    print(f"   All API-created resources should be visible in the web interface!")
    
    return True

if __name__ == "__main__":
    verify_integration()
