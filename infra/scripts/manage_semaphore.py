#!/usr/bin/env python3
"""
Semaphore Management Script
High-level management operations for Semaphore integration
"""

import json
import sys
import os
from pathlib import Path
from semaphore_api_client import SemaphoreAPIClient

class SemaphoreManager:
    """High-level Semaphore management operations"""
    
    def __init__(self, config_file: str = None):
        """Initialize Semaphore manager with configuration"""
        if config_file is None:
            config_file = Path(__file__).parent.parent / "config" / "semaphore_config.json"
        
        self.config_file = Path(config_file)
        self.load_config()
        self.client = SemaphoreAPIClient(
            self.config['semaphore']['base_url'],
            self.config['semaphore']['username'],
            self.config['semaphore']['password']
        )
    
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {self.config_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in configuration file: {e}")
            sys.exit(1)
    
    def authenticate(self):
        """Authenticate with Semaphore"""
        print("🔐 Authenticating with Semaphore...")
        if self.client.authenticate():
            print("✅ Authentication successful!")
            return True
        else:
            print("❌ Authentication failed!")
            return False
    
    def setup_project(self, project_name: str = None):
        """Set up project with all required resources"""
        if not self.authenticate():
            return False
        
        # Get or create project
        if project_name is None:
            project_name = "Network Infrastructure"
        
        project = self.client.find_project_by_name(project_name)
        if not project:
            print(f"📋 Creating project: {project_name}")
            project = self.client.create_project(
                project_name, 
                "Network device automation and management"
            )
            if not project:
                print("❌ Failed to create project")
                return False
        else:
            print(f"📋 Using existing project: {project_name}")
        
        project_id = project['id']
        print(f"   Project ID: {project_id}")
        
        # Create secrets
        print("\n🔐 Setting up secrets...")
        secrets_config = self.config.get('secrets', {})
        for secret_key, secret_config in secrets_config.items():
            existing_secret = self.client.find_secret_by_name(project_id, secret_config['name'])
            if not existing_secret:
                print(f"   Creating secret: {secret_config['name']}")
                result = self.client.create_secret(
                    project_id,
                    secret_config['name'],
                    secret_config['value'],
                    secret_config.get('description', '')
                )
                if result:
                    print(f"     ✅ Created (ID: {result.get('id')})")
                else:
                    print(f"     ❌ Failed to create")
            else:
                print(f"   ✅ Secret exists: {secret_config['name']}")
        
        # Create inventory
        print("\n📦 Setting up inventory...")
        inventory_config = self.config.get('inventories', {}).get('core_network', {})
        if inventory_config:
            existing_inventory = self.client.find_inventory_by_name(project_id, inventory_config['name'])
            if not existing_inventory:
                print(f"   Creating inventory: {inventory_config['name']}")
                inventory_content = json.dumps(inventory_config['content'], indent=2)
                result = self.client.create_inventory(
                    project_id,
                    inventory_config['name'],
                    inventory_content
                )
                if result:
                    print(f"     ✅ Created (ID: {result.get('id')})")
                else:
                    print(f"     ❌ Failed to create")
            else:
                print(f"   ✅ Inventory exists: {inventory_config['name']}")
        
        # Create SSH key (placeholder)
        print("\n🔑 Setting up SSH key...")
        ssh_keys = self.client.get_ssh_keys(project_id)
        if not ssh_keys:
            print("   Creating placeholder SSH key...")
            # Note: In production, you'd want to use a real SSH key
            placeholder_key = "-----BEGIN OPENSSH PRIVATE KEY-----\nplaceholder\n-----END OPENSSH PRIVATE KEY-----"
            result = self.client.create_ssh_key(
                project_id,
                "Placeholder SSH Key",
                placeholder_key
            )
            if result:
                print(f"     ✅ Created (ID: {result.get('id')})")
            else:
                print(f"     ❌ Failed to create")
        else:
            print(f"   ✅ SSH key exists: {ssh_keys[0].get('name')}")
        
        print(f"\n🎉 Project setup complete!")
        print(f"   Project ID: {project_id}")
        print(f"   Access URL: {self.config['semaphore']['base_url']}")
        
        return project_id
    
    def create_template(self, project_id: int, template_config: dict):
        """Create template from configuration"""
        print(f"\n📋 Creating template: {template_config['name']}")
        
        # Find required resources
        inventory = self.client.find_inventory_by_name(project_id, "Core Network Devices")
        if not inventory:
            print("❌ Core Network Devices inventory not found")
            return False
        
        ssh_keys = self.client.get_ssh_keys(project_id)
        if not ssh_keys:
            print("❌ No SSH keys found")
            return False
        
        # Create template
        result = self.client.create_template(
            project_id,
            template_config['name'],
            template_config['playbook'],
            inventory['id'],
            ssh_keys[0]['id'],
            arguments=template_config.get('arguments', [])
        )
        
        if result:
            print(f"   ✅ Created (ID: {result.get('id')})")
            return result
        else:
            print(f"   ❌ Failed to create")
            return False
    
    def setup_network_template(self, project_id: int):
        """Set up the network operations template"""
        template_config = self.config.get('templates', {}).get('network_operations', {})
        if template_config:
            return self.create_template(project_id, template_config)
        else:
            print("❌ Network operations template configuration not found")
            return False
    
    def run_health_check(self, project_id: int):
        """Run health check on all devices"""
        print("\n🏥 Running health check...")
        
        # Find the network operations template
        templates = self.client.get_templates(project_id)
        network_template = None
        for template in templates:
            if 'network' in template.get('name', '').lower() and 'operations' in template.get('name', '').lower():
                network_template = template
                break
        
        if not network_template:
            print("❌ Network operations template not found")
            return False
        
        # Run template with health_check operation
        result = self.client.run_template(
            project_id,
            network_template['id'],
            extra_vars={
                'operation': 'health_check',
                'target_device': 'all'
            }
        )
        
        if result:
            print(f"   ✅ Task started (ID: {result.get('task_id', 'Unknown')})")
            return result
        else:
            print(f"   ❌ Failed to start task")
            return False
    
    def get_status(self, project_id: int = None):
        """Get comprehensive status"""
        if not self.authenticate():
            return False
        
        if project_id is None:
            # Get first project or create one
            projects = self.client.get_projects()
            if projects:
                project_id = projects[0]['id']
            else:
                print("❌ No projects found")
                return False
        
        print(f"\n📊 Semaphore Status:")
        print(f"   Base URL: {self.config['semaphore']['base_url']}")
        print(f"   Authenticated: {self.client.authenticated}")
        
        # Get project status
        status = self.client.get_project_status(project_id)
        if "error" in status:
            print(f"❌ {status['error']}")
            return False
        
        project = status.get('project', {})
        print(f"\n📋 Project: {project.get('name')}")
        print(f"   ID: {project.get('id')}")
        print(f"   Description: {project.get('description', 'No description')}")
        
        # Count resources
        repositories = len(status.get('repositories', []))
        inventories = len(status.get('inventories', []))
        keys = len(status.get('keys', []))
        secrets = len(status.get('secrets', []))
        templates = len(status.get('templates', []))
        
        print(f"\n📈 Resource Counts:")
        print(f"   Repositories: {repositories}")
        print(f"   Inventories: {inventories}")
        print(f"   SSH Keys: {keys}")
        print(f"   Secrets: {secrets}")
        print(f"   Templates: {templates}")
        
        return True

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python manage_semaphore.py <command>")
        print("Commands:")
        print("  setup           - Set up project with all resources")
        print("  status          - Show current status")
        print("  health-check    - Run health check on all devices")
        print("  setup-template  - Set up network operations template")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    # Initialize manager
    manager = SemaphoreManager()
    
    if command == "setup":
        project_id = manager.setup_project()
        if project_id:
            manager.setup_network_template(project_id)
    
    elif command == "status":
        manager.get_status()
    
    elif command == "health-check":
        projects = manager.client.get_projects()
        if projects:
            project_id = projects[0]['id']
            manager.run_health_check(project_id)
        else:
            print("❌ No projects found")
    
    elif command == "setup-template":
        projects = manager.client.get_projects()
        if projects:
            project_id = projects[0]['id']
            manager.setup_network_template(project_id)
        else:
            print("❌ No projects found")
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
