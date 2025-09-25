#!/usr/bin/env python3
"""
Semaphore CLI Tool
Command-line interface for Semaphore API operations
"""

import sys
import json
from semaphore_api_client import SemaphoreAPIClient

class SemaphoreCLI:
    """Command-line interface for Semaphore API"""
    
    def __init__(self, base_url: str, username: str, password: str):
        self.client = SemaphoreAPIClient(base_url, username, password)
        self.authenticated = False
    
    def authenticate(self):
        """Authenticate with Semaphore"""
        print(f"🔐 Authenticating with Semaphore at {self.client.base_url}...")
        if self.client.authenticate():
            self.authenticated = True
            print("✅ Authentication successful!")
            return True
        else:
            print("❌ Authentication failed!")
            return False
    
    def list_projects(self):
        """List all projects"""
        print("\n📋 Projects:")
        projects = self.client.get_projects()
        if projects:
            for project in projects:
                print(f"  • {project.get('name')} (ID: {project.get('id')})")
                print(f"    Description: {project.get('description', 'No description')}")
        else:
            print("  No projects found")
    
    def create_project(self, name: str, description: str = ""):
        """Create a new project"""
        print(f"\n➕ Creating project: {name}")
        result = self.client.create_project(name, description)
        if result:
            print(f"✅ Project created successfully!")
            print(f"   ID: {result.get('id')}")
            print(f"   Name: {result.get('name')}")
        else:
            print("❌ Failed to create project")
    
    def list_secrets(self, project_id: int):
        """List secrets for a project"""
        print(f"\n🔐 Secrets for Project {project_id}:")
        secrets = self.client.get_secrets(project_id)
        if secrets:
            for secret in secrets:
                print(f"  • {secret.get('name')} (ID: {secret.get('id')})")
                print(f"    Description: {secret.get('description', 'No description')}")
        else:
            print("  No secrets found")
    
    def create_secret(self, project_id: int, name: str, value: str, description: str = ""):
        """Create a new secret"""
        print(f"\n🔐 Creating secret: {name}")
        result = self.client.create_secret(project_id, name, value, description)
        if result:
            print(f"✅ Secret created successfully!")
            print(f"   ID: {result.get('id')}")
            print(f"   Name: {result.get('name')}")
        else:
            print("❌ Failed to create secret")
    
    def list_inventories(self, project_id: int):
        """List inventories for a project"""
        print(f"\n📦 Inventories for Project {project_id}:")
        inventories = self.client.get_inventories(project_id)
        if inventories:
            for inventory in inventories:
                print(f"  • {inventory.get('name')} (ID: {inventory.get('id')})")
                print(f"    Type: {inventory.get('type', 'static')}")
        else:
            print("  No inventories found")
    
    def list_templates(self, project_id: int):
        """List templates for a project"""
        print(f"\n📋 Templates for Project {project_id}:")
        templates = self.client.get_templates(project_id)
        if templates:
            for template in templates:
                print(f"  • {template.get('name')} (ID: {template.get('id')})")
                print(f"    Playbook: {template.get('playbook', 'N/A')}")
        else:
            print("  No templates found")
    
    def get_project_status(self, project_id: int):
        """Get comprehensive project status"""
        print(f"\n📊 Project Status for ID {project_id}:")
        status = self.client.get_project_status(project_id)
        
        if "error" in status:
            print(f"❌ {status['error']}")
            return
        
        project = status.get('project', {})
        print(f"📋 Project: {project.get('name')}")
        print(f"   Description: {project.get('description', 'No description')}")
        
        repositories = status.get('repositories', [])
        print(f"\n📁 Repositories: {len(repositories)}")
        for repo in repositories:
            print(f"  • {repo.get('name')} - {repo.get('git_url', 'No URL')}")
        
        inventories = status.get('inventories', [])
        print(f"\n📦 Inventories: {len(inventories)}")
        for inv in inventories:
            print(f"  • {inv.get('name')} ({inv.get('type', 'static')})")
        
        keys = status.get('keys', [])
        print(f"\n🔑 SSH Keys: {len(keys)}")
        for key in keys:
            print(f"  • {key.get('name')}")
        
        secrets = status.get('secrets', [])
        print(f"\n🔐 Secrets: {len(secrets)}")
        for secret in secrets:
            print(f"  • {secret.get('name')}")
        
        templates = status.get('templates', [])
        print(f"\n📋 Templates: {len(templates)}")
        for template in templates:
            print(f"  • {template.get('name')} - {template.get('playbook', 'No playbook')}")
    
    def interactive_mode(self):
        """Interactive mode for CLI"""
        print("\n🎯 Semaphore CLI Interactive Mode")
        print("Type 'help' for available commands, 'quit' to exit")
        
        while True:
            try:
                command = input("\nsemaphore> ").strip().lower()
                
                if command == 'quit' or command == 'exit':
                    print("👋 Goodbye!")
                    break
                elif command == 'help':
                    self.show_help()
                elif command == 'projects':
                    self.list_projects()
                elif command.startswith('create-project '):
                    parts = command.split(' ', 2)
                    if len(parts) >= 2:
                        name = parts[1]
                        description = parts[2] if len(parts) > 2 else ""
                        self.create_project(name, description)
                    else:
                        print("Usage: create-project <name> [description]")
                elif command.startswith('secrets '):
                    try:
                        project_id = int(command.split()[1])
                        self.list_secrets(project_id)
                    except (IndexError, ValueError):
                        print("Usage: secrets <project_id>")
                elif command.startswith('create-secret '):
                    parts = command.split(' ', 3)
                    if len(parts) >= 4:
                        try:
                            project_id = int(parts[1])
                            name = parts[2]
                            value = parts[3]
                            self.create_secret(project_id, name, value)
                        except ValueError:
                            print("Usage: create-secret <project_id> <name> <value>")
                    else:
                        print("Usage: create-secret <project_id> <name> <value>")
                elif command.startswith('status '):
                    try:
                        project_id = int(command.split()[1])
                        self.get_project_status(project_id)
                    except (IndexError, ValueError):
                        print("Usage: status <project_id>")
                elif command.startswith('inventories '):
                    try:
                        project_id = int(command.split()[1])
                        self.list_inventories(project_id)
                    except (IndexError, ValueError):
                        print("Usage: inventories <project_id>")
                elif command.startswith('templates '):
                    try:
                        project_id = int(command.split()[1])
                        self.list_templates(project_id)
                    except (IndexError, ValueError):
                        print("Usage: templates <project_id>")
                else:
                    print(f"Unknown command: {command}")
                    print("Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def show_help(self):
        """Show help information"""
        print("""
🎯 Available Commands:

📋 Project Management:
  projects                    - List all projects
  create-project <name> [desc] - Create new project
  status <project_id>         - Show project status

🔐 Secret Management:
  secrets <project_id>        - List secrets for project
  create-secret <pid> <name> <value> - Create new secret

📦 Resource Management:
  inventories <project_id>    - List inventories
  templates <project_id>      - List templates

🛠️ Utility:
  help                       - Show this help
  quit/exit                  - Exit CLI

📝 Examples:
  projects
  create-project "Network Automation" "Network device management"
  status 1
  secrets 1
  create-secret 1 "Network Credentials" "admin:password123"
        """)

def main():
    """Main CLI entry point"""
    if len(sys.argv) < 4:
        print("Usage: python semaphore_cli.py <base_url> <username> <password> [interactive]")
        print("Example: python semaphore_cli.py http://172.23.5.22:3000 admin password123")
        print("Add 'interactive' for interactive mode")
        sys.exit(1)
    
    base_url = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    interactive = len(sys.argv) > 4 and sys.argv[4].lower() == 'interactive'
    
    # Initialize CLI
    cli = SemaphoreCLI(base_url, username, password)
    
    # Authenticate
    if not cli.authenticate():
        sys.exit(1)
    
    if interactive:
        cli.interactive_mode()
    else:
        # Show basic status
        cli.list_projects()

if __name__ == "__main__":
    main()
