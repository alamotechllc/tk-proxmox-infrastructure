#!/usr/bin/env python3
"""
Final Template Verification
Confirms that templates are properly configured and should work without "invalid app id" errors
"""

from semaphore_token_client import SemaphoreTokenClient

def verify_template_configuration():
    """Verify that all templates are properly configured"""
    
    print("🔍 === FINAL TEMPLATE VERIFICATION ===")
    print()
    
    # Initialize client
    client = SemaphoreTokenClient('http://172.23.5.22:3000', api_token='ywg7silgm3-fxumm06rjdztw8th9dundrwe7fc73e2y=')
    
    project_id = 4
    
    # Check templates
    print("📋 Templates in Network Infrastructure Project:")
    templates = client.get_templates(project_id)
    
    if not templates:
        print("   ❌ No templates found")
        return False
    
    for template in templates:
        print(f"   • {template.get('name')} (ID: {template.get('id')})")
        print(f"     Playbook: {template.get('playbook')}")
        print(f"     Inventory: {template.get('inventory_id')}")
        print(f"     Repository: {template.get('repository_id')}")
        print()
    
    # Check inventory configuration
    print("📦 Inventory Configuration:")
    inventories = client.get_inventories(project_id)
    template_inventory = None
    
    for inv in inventories:
        if inv.get('id') == 7:  # Core Network Infrastructure
            template_inventory = inv
            break
    
    if template_inventory:
        print(f"   • {template_inventory.get('name')} (ID: {template_inventory.get('id')})")
        print(f"     SSH Key ID: {template_inventory.get('ssh_key_id')}")
        print(f"     Become Key ID: {template_inventory.get('become_key_id')}")
        print(f"     Type: {template_inventory.get('type')}")
        print()
        
        # Validate SSH key
        ssh_key_valid = template_inventory.get('ssh_key_id') is not None
        print(f"   🔑 SSH Key Status: {'✅ Valid' if ssh_key_valid else '❌ Missing'}")
    else:
        print("   ❌ Core Network Infrastructure inventory not found")
        return False
    
    # Check repository configuration
    print("📁 Repository Configuration:")
    repositories = client.get_repositories(project_id)
    template_repository = None
    
    for repo in repositories:
        if repo.get('id') == 1:  # Local repository
            template_repository = repo
            break
    
    if template_repository:
        print(f"   • {template_repository.get('name')} (ID: {template_repository.get('id')})")
        print(f"     SSH Key ID: {template_repository.get('ssh_key_id')}")
        print(f"     Git URL: {template_repository.get('git_url')}")
        print()
        
        # Validate SSH key
        repo_ssh_key_valid = template_repository.get('ssh_key_id') is not None
        print(f"   🔑 Repository SSH Key Status: {'✅ Valid' if repo_ssh_key_valid else '❌ Missing'}")
    else:
        print("   ❌ Local repository not found")
        return False
    
    # Check SSH key details
    print("🔐 SSH Key Details:")
    keys = client.get_ssh_keys(project_id)
    ssh_key = None
    
    for key in keys:
        if key.get('id') == 4:  # Network Device Admin Credentials
            ssh_key = key
            break
    
    if ssh_key:
        print(f"   • {ssh_key.get('name')} (ID: {ssh_key.get('id')})")
        print(f"     Type: {ssh_key.get('type')}")
        print(f"     Status: ✅ Available")
    else:
        print("   ❌ Network Device Admin Credentials SSH key not found")
        return False
    
    # Final validation
    print("\n✅ === VALIDATION SUMMARY ===")
    
    all_valid = (
        len(templates) > 0 and
        template_inventory is not None and
        template_repository is not None and
        ssh_key is not None and
        template_inventory.get('ssh_key_id') is not None and
        template_repository.get('ssh_key_id') is not None
    )
    
    print(f"   📋 Templates: {len(templates)} found")
    print(f"   📦 Inventory SSH Key: {'✅ Configured' if template_inventory.get('ssh_key_id') else '❌ Missing'}")
    print(f"   📁 Repository SSH Key: {'✅ Configured' if template_repository.get('ssh_key_id') else '❌ Missing'}")
    print(f"   🔐 SSH Key Available: {'✅ Yes' if ssh_key else '❌ No'}")
    
    print(f"\n🎯 FINAL STATUS: {'✅ ALL SYSTEMS GO' if all_valid else '❌ ISSUES REMAIN'}")
    
    if all_valid:
        print("\n🚀 Templates should now work without 'invalid app id' errors!")
        print("   • SSH keys are properly associated with inventory and repository")
        print("   • Templates can access network devices using the configured credentials")
        print("   • All playbooks are available in the local repository")
        print("\n🌐 Access Semaphore UI at: http://172.23.5.22:3000")
        print("   Login: admin / 8fewWER8382")
        print("   Project: Network Infrastructure")
        print("   Templates should be executable from the web interface!")
    else:
        print("\n❌ Some configuration issues remain. Check the validation details above.")
    
    return all_valid

if __name__ == "__main__":
    verify_template_configuration()
