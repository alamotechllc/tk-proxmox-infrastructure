#!/usr/bin/env python3
"""
GitHub-Semaphore Integration Script
Sets up GitHub repository integration with Semaphore for Ansible automation
"""

import json
import sys
import os
from pathlib import Path
from semaphore_token_client import SemaphoreTokenClient

class GitHubSemaphoreIntegration:
    """GitHub-Semaphore integration management"""
    
    def __init__(self, semaphore_url: str, api_token: str, github_repo_url: str = None):
        """
        Initialize GitHub-Semaphore integration
        
        Args:
            semaphore_url: Semaphore base URL
            api_token: Semaphore API token
            github_repo_url: GitHub repository URL (optional)
        """
        self.semaphore_url = semaphore_url
        self.api_token = api_token
        self.github_repo_url = github_repo_url or "https://github.com/your-username/tk-proxmox.git"
        self.client = SemaphoreTokenClient(semaphore_url, api_token=api_token)
        
        # Configuration
        self.project_name = "Network Infrastructure"
        self.repository_name = "TK-Proxmox Repository"
        self.ssh_key_name = "GitHub SSH Key"
        
    def setup_github_integration(self, project_id: int = None):
        """Set up complete GitHub integration for a project"""
        print("🚀 Setting up GitHub-Semaphore Integration...")
        
        # Get or find project
        if project_id is None:
            project = self.client.find_project_by_name(self.project_name)
            if not project:
                print(f"❌ Project '{self.project_name}' not found")
                return False
            project_id = project['id']
        
        print(f"📋 Using project: {self.project_name} (ID: {project_id})")
        
        # Step 1: Create SSH key for GitHub
        print("\n🔑 Setting up SSH key for GitHub...")
        ssh_key = self.client.find_key_by_name(project_id, self.ssh_key_name)
        if not ssh_key:
            print("   Creating SSH key for GitHub access...")
            # Note: In production, you'd use a real SSH key
            ssh_key_data = self._generate_ssh_key_placeholder()
            ssh_key = self.client.create_ssh_key(
                project_id,
                self.ssh_key_name,
                ssh_key_data['private_key'],
                ssh_key_data['public_key']
            )
            if ssh_key:
                print(f"   ✅ SSH key created (ID: {ssh_key['id']})")
            else:
                print("   ❌ Failed to create SSH key")
                return False
        else:
            print(f"   ✅ SSH key exists: {ssh_key['name']} (ID: {ssh_key['id']})")
        
        # Step 2: Create repository
        print("\n📁 Setting up GitHub repository...")
        repository = None
        repositories = self.client.get_repositories(project_id)
        for repo in repositories:
            if repo.get('name') == self.repository_name:
                repository = repo
                break
        
        if not repository:
            print(f"   Creating repository: {self.repository_name}")
            repository = self.client.create_repository(
                project_id,
                self.repository_name,
                self.github_repo_url,
                ssh_key['id']
            )
            if repository:
                print(f"   ✅ Repository created (ID: {repository['id']})")
            else:
                print("   ❌ Failed to create repository")
                return False
        else:
            print(f"   ✅ Repository exists: {repository['name']} (ID: {repository['id']})")
        
        # Step 3: Create/update inventory
        print("\n📦 Setting up inventory...")
        inventory = self.client.find_inventory_by_name(project_id, "Core Network Devices")
        if not inventory:
            print("   Creating network inventory...")
            inventory_data = self._get_network_inventory()
            inventory = self.client.create_inventory(
                project_id,
                "Core Network Devices",
                json.dumps(inventory_data, indent=2)
            )
            if inventory:
                print(f"   ✅ Inventory created (ID: {inventory['id']})")
            else:
                print("   ❌ Failed to create inventory")
                return False
        else:
            print(f"   ✅ Inventory exists: {inventory['name']} (ID: {inventory['id']})")
        
        # Step 4: Create network operations template
        print("\n📋 Setting up network operations template...")
        template_name = "Network Operations Template"
        templates = self.client.get_templates(project_id)
        network_template = None
        for template in templates:
            if template.get('name') == template_name:
                network_template = template
                break
        
        if not network_template:
            print(f"   Creating template: {template_name}")
            template_args = self._get_template_arguments()
            network_template = self.client.create_template(
                project_id,
                template_name,
                "templates/network_operations_template.yml",
                inventory['id'],
                ssh_key['id'],
                repository['id'],
                template_args
            )
            if network_template:
                print(f"   ✅ Template created (ID: {network_template['id']})")
            else:
                print("   ❌ Failed to create template")
                return False
        else:
            print(f"   ✅ Template exists: {network_template['name']} (ID: {network_template['id']})")
        
        # Step 5: Create secrets
        print("\n🔐 Setting up secrets...")
        secrets_config = self._get_secrets_config()
        for secret_name, secret_config in secrets_config.items():
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
                    print(f"     ✅ Created (ID: {result['id']})")
                else:
                    print(f"     ❌ Failed to create")
            else:
                print(f"   ✅ Secret exists: {secret_config['name']}")
        
        print(f"\n🎉 GitHub-Semaphore integration complete!")
        print(f"   Project: {self.project_name} (ID: {project_id})")
        print(f"   Repository: {self.repository_name}")
        print(f"   Template: {template_name}")
        print(f"   Access URL: {self.semaphore_url}")
        
        return True
    
    def test_integration(self, project_id: int = None):
        """Test the GitHub integration by running a health check"""
        print("🧪 Testing GitHub-Semaphore integration...")
        
        # Get project
        if project_id is None:
            project = self.client.find_project_by_name(self.project_name)
            if not project:
                print(f"❌ Project '{self.project_name}' not found")
                return False
            project_id = project['id']
        
        # Find network operations template
        templates = self.client.get_templates(project_id)
        network_template = None
        for template in templates:
            if 'network' in template.get('name', '').lower() and 'operations' in template.get('name', '').lower():
                network_template = template
                break
        
        if not network_template:
            print("❌ Network operations template not found")
            return False
        
        print(f"📋 Found template: {network_template['name']} (ID: {network_template['id']})")
        
        # Run health check
        print("🏥 Running health check...")
        result = self.client.run_template(
            project_id,
            network_template['id'],
            debug=False,
            dry_run=True,  # Safe dry run
            extra_vars={
                'operation': 'health_check',
                'target_device': 'all'
            }
        )
        
        if result:
            print(f"   ✅ Task started (ID: {result.get('task_id', 'Unknown')})")
            return True
        else:
            print(f"   ❌ Failed to start task")
            return False
    
    def _generate_ssh_key_placeholder(self):
        """Generate placeholder SSH key data"""
        return {
            'private_key': '''-----BEGIN OPENSSH PRIVATE KEY-----
# This is a placeholder SSH key
# In production, generate a real SSH key pair:
# ssh-keygen -t ed25519 -C "semaphore-github-integration"
# Add the public key to your GitHub repository settings
-----END OPENSSH PRIVATE KEY-----''',
            'public_key': '''ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... semaphore-github-integration'''
        }
    
    def _get_network_inventory(self):
        """Get network inventory configuration"""
        return {
            "core_network": {
                "hosts": {
                    "arista-core-01": {
                        "ansible_host": "172.23.5.1",
                        "device_type": "arista_eos"
                    },
                    "nexus-agg-01": {
                        "ansible_host": "172.23.5.2", 
                        "device_type": "cisco_nxos"
                    }
                }
            },
            "access_switches": {
                "hosts": {
                    "catalyst-access-01": {
                        "ansible_host": "172.23.5.10",
                        "device_type": "cisco_ios"
                    },
                    "catalyst-access-02": {
                        "ansible_host": "172.23.5.11",
                        "device_type": "cisco_ios"
                    }
                }
            },
            "security": {
                "hosts": {
                    "opnsense-fw-01": {
                        "ansible_host": "172.23.5.3",
                        "device_type": "opnsense"
                    }
                }
            }
        }
    
    def _get_template_arguments(self):
        """Get template arguments configuration"""
        return [
            {
                "name": "operation",
                "description": "Operation type (backup|vlan_assign|port_enable|port_disable|health_check)",
                "type": "string",
                "required": True,
                "default": "health_check"
            },
            {
                "name": "target_device",
                "description": "Target device hostname (or 'all' for all devices)",
                "type": "string",
                "required": False,
                "default": "all"
            },
            {
                "name": "port_interface",
                "description": "Port interface (for port operations)",
                "type": "string",
                "required": False
            },
            {
                "name": "vlan_id",
                "description": "VLAN ID (for VLAN operations)",
                "type": "string",
                "required": False
            },
            {
                "name": "port_description",
                "description": "Port description (for port operations)",
                "type": "string",
                "required": False,
                "default": "Managed by Ansible Template"
            },
            {
                "name": "backup_location",
                "description": "Backup storage location",
                "type": "string",
                "required": False,
                "default": "/opt/network_backups"
            }
        ]
    
    def _get_secrets_config(self):
        """Get secrets configuration"""
        return {
            "network_device_credentials": {
                "name": "Network Device Admin Credentials",
                "description": "Admin username and password for network devices",
                "value": "admin\n8fewWER8382"
            },
            "network_enable_password": {
                "name": "Network Enable Password", 
                "description": "Enable password for Cisco devices",
                "value": "8fewWER8382"
            },
            "opnsense_credentials": {
                "name": "OPNsense Admin Credentials",
                "description": "OPNsense firewall admin credentials",
                "value": "admin\n8fewWER8382"
            },
            "network_backup_credentials": {
                "name": "Network Backup Credentials",
                "description": "Credentials for network backup operations",
                "value": "admin\n8fewWER8382"
            }
        }

def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("Usage: python github_semaphore_integration.py <semaphore_url> <api_token> [github_repo_url] [command]")
        print("Commands:")
        print("  setup           - Set up complete GitHub integration")
        print("  test            - Test the integration")
        print("  status          - Show current status")
        sys.exit(1)
    
    semaphore_url = sys.argv[1]
    api_token = sys.argv[2]
    github_repo_url = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3] in ['setup', 'test', 'status'] else None
    command = sys.argv[-1] if sys.argv[-1] in ['setup', 'test', 'status'] else 'setup'
    
    # Initialize integration
    integration = GitHubSemaphoreIntegration(semaphore_url, api_token, github_repo_url)
    
    if command == "setup":
        success = integration.setup_github_integration()
        if success:
            print("\n✅ GitHub-Semaphore integration setup complete!")
        else:
            print("\n❌ GitHub-Semaphore integration setup failed!")
            sys.exit(1)
    
    elif command == "test":
        success = integration.test_integration()
        if success:
            print("\n✅ Integration test passed!")
        else:
            print("\n❌ Integration test failed!")
            sys.exit(1)
    
    elif command == "status":
        print("📊 GitHub-Semaphore Integration Status:")
        print(f"   Semaphore URL: {semaphore_url}")
        print(f"   GitHub Repo: {integration.github_repo_url}")
        print(f"   Project: {integration.project_name}")
        
        # Test connection
        projects = integration.client.get_projects()
        if projects:
            print(f"   ✅ Connected to Semaphore ({len(projects)} projects)")
        else:
            print(f"   ❌ Failed to connect to Semaphore")
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
