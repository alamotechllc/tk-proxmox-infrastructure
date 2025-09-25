#!/usr/bin/env python3
"""
Semaphore API Examples
Practical examples for common Semaphore API operations
Based on TK Network Infrastructure project experience
"""

import json
import sys
from semaphore_token_client import SemaphoreTokenClient

# TK Network Configuration
TK_CONFIG = {
    'semaphore_url': 'http://172.23.5.22:3000',
    'project_id': 4,  # Network Infrastructure project
    'core_inventory_id': 7,  # Core Network Infrastructure (Secure)
    'local_repo_id': 1,  # Local repository
    'default_env_id': 5,  # Default environment
}

def example_1_basic_connectivity(client):
    """Example 1: Test basic API connectivity"""
    print("=== EXAMPLE 1: Basic API Connectivity ===")
    
    if client.authenticate():
        print("✅ Authentication successful")
        
        projects = client.get_projects()
        print(f"📋 Found {len(projects)} projects:")
        for project in projects:
            print(f"   • {project['name']} (ID: {project['id']})")
        
        return True
    else:
        print("❌ Authentication failed")
        return False

def example_2_project_resources(client, project_id):
    """Example 2: Get all resources for a project"""
    print(f"\n=== EXAMPLE 2: Project {project_id} Resources ===")
    
    resources = {
        'inventories': client.get_inventories(project_id),
        'repositories': client.get_repositories(project_id),
        'templates': client.get_templates(project_id),
        'ssh_keys': client.get_ssh_keys(project_id)
    }
    
    for resource_type, resource_list in resources.items():
        print(f"📦 {resource_type.title()}: {len(resource_list)}")
        for resource in resource_list:
            print(f"   • {resource['name']} (ID: {resource['id']})")
    
    return resources

def example_3_inventory_management(client, project_id):
    """Example 3: Inventory management operations"""
    print(f"\n=== EXAMPLE 3: Inventory Management ===")
    
    # Get current inventories
    inventories = client.get_inventories(project_id)
    
    print("📋 Current Inventories:")
    for inv in inventories:
        print(f"   • {inv['name']} (ID: {inv['id']})")
        
        # Show device count
        content = inv.get('inventory', '')
        device_count = content.count('ansible_host:')
        print(f"     Devices: {device_count}")
        
        # Show if it has TK devices
        has_tk_devices = 'tks-' in content
        print(f"     TK Devices: {'✅ Yes' if has_tk_devices else '❌ No'}")

def example_4_template_creation(client, project_id):
    """Example 4: Create a test template"""
    print(f"\n=== EXAMPLE 4: Template Creation ===")
    
    # Template configuration
    template_config = {
        'project_id': project_id,
        'name': 'API Test Template',
        'playbook': 'site.yml',
        'inventory_id': TK_CONFIG['core_inventory_id'],
        'repository_id': TK_CONFIG['local_repo_id'],
        'environment_id': TK_CONFIG['default_env_id'],
        'app': 'ansible',
        'arguments': []
    }
    
    print("🔧 Creating test template...")
    print(f"   Name: {template_config['name']}")
    print(f"   Playbook: {template_config['playbook']}")
    print(f"   Inventory ID: {template_config['inventory_id']}")
    print(f"   Repository ID: {template_config['repository_id']}")
    
    result = client._make_request('POST', f"/project/{project_id}/templates", data=template_config)
    
    if result:
        template_id = result.get('id')
        print(f"✅ Template created successfully (ID: {template_id})")
        
        # Clean up - delete the test template
        delete_result = client._make_request('DELETE', f"/project/{project_id}/templates/{template_id}")
        if delete_result:
            print("🗑️ Test template cleaned up")
        
        return template_id
    else:
        print("❌ Template creation failed")
        return None

def example_5_inventory_update(client, project_id, inventory_id):
    """Example 5: Update inventory with new device"""
    print(f"\n=== EXAMPLE 5: Inventory Update ===")
    
    # Get current inventory
    inventories = client.get_inventories(project_id)
    target_inventory = None
    
    for inv in inventories:
        if inv.get('id') == inventory_id:
            target_inventory = inv
            break
    
    if not target_inventory:
        print(f"❌ Inventory {inventory_id} not found")
        return False
    
    print(f"📦 Updating inventory: {target_inventory['name']}")
    
    # Add a test device (we'll remove it after)
    current_content = target_inventory.get('inventory', '')
    
    test_device = """
        api-test-device:
          ansible_host: 172.23.7.99
          device_type: test
          description: "API Test Device - Will be removed"
"""
    
    # Add test device to inventory
    updated_content = current_content + test_device
    
    # Update via API
    update_data = {
        'id': inventory_id,
        'project_id': project_id,
        'name': target_inventory['name'],
        'inventory': updated_content,
        'type': target_inventory.get('type', 'static'),
        'ssh_key_id': target_inventory.get('ssh_key_id')
    }
    
    result = client._make_request('PUT', f"/project/{project_id}/inventory/{inventory_id}", data=update_data)
    
    if result:
        print("✅ Inventory updated successfully")
        
        # Revert the change
        revert_data = update_data.copy()
        revert_data['inventory'] = current_content
        
        revert_result = client._make_request('PUT', f"/project/{project_id}/inventory/{inventory_id}", data=revert_data)
        if revert_result:
            print("🔄 Changes reverted")
        
        return True
    else:
        print("❌ Inventory update failed")
        return False

def example_6_error_handling(client):
    """Example 6: Proper error handling"""
    print(f"\n=== EXAMPLE 6: Error Handling ===")
    
    # Deliberately try invalid operations to show error handling
    print("🧪 Testing error scenarios...")
    
    # Test 1: Invalid endpoint
    result = client._make_request('GET', '/invalid-endpoint')
    print(f"Invalid endpoint: {'❌ Handled correctly' if result is None else '⚠️ Unexpected result'}")
    
    # Test 2: Invalid project ID
    result = client._make_request('GET', '/project/99999/inventory')
    print(f"Invalid project ID: {'❌ Handled correctly' if result is None else '⚠️ Unexpected result'}")
    
    # Test 3: Missing required fields
    invalid_template = {
        'name': 'Invalid Template'
        # Missing required fields
    }
    result = client._make_request('POST', f"/project/{TK_CONFIG['project_id']}/templates", data=invalid_template)
    print(f"Missing fields: {'❌ Handled correctly' if result is None else '⚠️ Unexpected result'}")

def example_7_bulk_operations(client, project_id):
    """Example 7: Bulk operations"""
    print(f"\n=== EXAMPLE 7: Bulk Operations ===")
    
    # Get all templates and show their status
    templates = client.get_templates(project_id)
    
    print("📋 Template Analysis:")
    for template in templates:
        template_name = template['name']
        playbook = template['playbook']
        inventory_id = template['inventory_id']
        repository_id = template['repository_id']
        
        # Validate template has all required resources
        inventories = client.get_inventories(project_id)
        repositories = client.get_repositories(project_id)
        
        inventory_exists = any(inv['id'] == inventory_id for inv in inventories)
        repository_exists = any(repo['id'] == repository_id for repo in repositories)
        
        status = "✅ Valid" if inventory_exists and repository_exists else "⚠️ Issues"
        print(f"   • {template_name}: {status}")
        
        if not inventory_exists:
            print(f"     ❌ Inventory ID {inventory_id} not found")
        if not repository_exists:
            print(f"     ❌ Repository ID {repository_id} not found")

def main():
    """Run all examples"""
    if len(sys.argv) < 2:
        print("Usage: python3 semaphore_api_examples.py <api_token>")
        print("   or: python3 semaphore_api_examples.py <username> <password>")
        sys.exit(1)
    
    # Initialize client
    if len(sys.argv) == 2:
        # Token authentication
        client = SemaphoreTokenClient(TK_CONFIG['semaphore_url'], api_token=sys.argv[1])
    else:
        # Username/password authentication
        client = SemaphoreTokenClient(TK_CONFIG['semaphore_url'], sys.argv[1], sys.argv[2])
    
    print("🔗 Semaphore API Examples")
    print(f"   URL: {TK_CONFIG['semaphore_url']}")
    print(f"   Project ID: {TK_CONFIG['project_id']}")
    print()
    
    # Run examples
    if not example_1_basic_connectivity(client):
        print("❌ Cannot proceed - authentication failed")
        sys.exit(1)
    
    example_2_project_resources(client, TK_CONFIG['project_id'])
    example_3_inventory_management(client, TK_CONFIG['project_id'])
    example_4_template_creation(client, TK_CONFIG['project_id'])
    example_5_inventory_update(client, TK_CONFIG['project_id'], TK_CONFIG['core_inventory_id'])
    example_6_error_handling(client)
    example_7_bulk_operations(client, TK_CONFIG['project_id'])
    
    print("\n🎯 All examples completed!")
    print("   Check the output above for results and demonstrations")
    print("   Use these patterns in your own API integrations")

if __name__ == "__main__":
    main()
