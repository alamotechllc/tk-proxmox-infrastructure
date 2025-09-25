#!/usr/bin/env python3
"""
Semaphore API Client
Comprehensive Python client for Semaphore API integration
"""

import requests
import json
import sys
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SemaphoreAPIClient:
    """Comprehensive Semaphore API client"""
    
    def __init__(self, base_url: str, username: str, password: str):
        """
        Initialize Semaphore API client
        
        Args:
            base_url: Semaphore base URL (e.g., http://172.23.5.22:3000)
            username: Semaphore username
            password: Semaphore password
        """
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api"
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.authenticated = False
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def authenticate(self) -> bool:
        """Authenticate with Semaphore API"""
        try:
            auth_url = f"{self.api_url}/auth/login"
            auth_data = {
                'auth': self.username,
                'password': self.password
            }
            
            logger.debug(f"Authenticating with URL: {auth_url}")
            response = self.session.post(auth_url, json=auth_data)
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response cookies: {dict(response.cookies)}")
            response.raise_for_status()
            
            # Extract session cookie - Semaphore returns 204 on successful auth
            if response.status_code == 204:
                # Cookie should be automatically handled by the session
                self.authenticated = True
                logger.info("Successfully authenticated with Semaphore API")
                return True
            else:
                logger.error(f"Authentication failed: Status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make authenticated API request"""
        if not self.authenticated:
            if not self.authenticate():
                return None
        
        url = f"{self.api_url}{endpoint}" if endpoint.startswith('/') else f"{self.api_url}/{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            # Handle empty responses
            if response.status_code == 204 or not response.content:
                return {"success": True, "status_code": response.status_code}
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {method} {endpoint} - {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response content: {e.response.text}")
            return None
    
    # Project Management
    def get_projects(self) -> List[Dict]:
        """Get all projects"""
        result = self._make_request('GET', '/projects')
        return result if result else []
    
    def get_project(self, project_id: int) -> Optional[Dict]:
        """Get specific project"""
        return self._make_request('GET', f'/project/{project_id}')
    
    def create_project(self, name: str, description: str = "") -> Optional[Dict]:
        """Create new project"""
        data = {
            'name': name,
            'description': description
        }
        return self._make_request('POST', '/projects', data=data)
    
    def update_project(self, project_id: int, name: str = None, description: str = None) -> Optional[Dict]:
        """Update project"""
        data = {}
        if name:
            data['name'] = name
        if description:
            data['description'] = description
        
        return self._make_request('PUT', f'/project/{project_id}', data=data)
    
    def delete_project(self, project_id: int) -> bool:
        """Delete project"""
        result = self._make_request('DELETE', f'/project/{project_id}')
        return result is not None and result.get('success', False)
    
    # Repository Management
    def get_repositories(self, project_id: int) -> List[Dict]:
        """Get all repositories for a project"""
        result = self._make_request('GET', f'/project/{project_id}/repositories')
        return result if result else []
    
    def create_repository(self, project_id: int, name: str, git_url: str, ssh_key_id: int = None) -> Optional[Dict]:
        """Create new repository"""
        data = {
            'name': name,
            'git_url': git_url,
            'ssh_key_id': ssh_key_id
        }
        return self._make_request('POST', f'/project/{project_id}/repositories', data=data)
    
    def update_repository(self, project_id: int, repo_id: int, name: str = None, git_url: str = None) -> Optional[Dict]:
        """Update repository"""
        data = {}
        if name:
            data['name'] = name
        if git_url:
            data['git_url'] = git_url
        
        return self._make_request('PUT', f'/project/{project_id}/repositories/{repo_id}', data=data)
    
    def delete_repository(self, project_id: int, repo_id: int) -> bool:
        """Delete repository"""
        result = self._make_request('DELETE', f'/project/{project_id}/repositories/{repo_id}')
        return result is not None and result.get('success', False)
    
    # SSH Key Management
    def get_ssh_keys(self, project_id: int) -> List[Dict]:
        """Get all SSH keys for a project"""
        result = self._make_request('GET', f'/project/{project_id}/keys')
        return result if result else []
    
    def create_ssh_key(self, project_id: int, name: str, private_key: str, public_key: str = None) -> Optional[Dict]:
        """Create new SSH key"""
        data = {
            'name': name,
            'private_key': private_key,
            'public_key': public_key
        }
        return self._make_request('POST', f'/project/{project_id}/keys', data=data)
    
    def update_ssh_key(self, project_id: int, key_id: int, name: str = None, private_key: str = None) -> Optional[Dict]:
        """Update SSH key"""
        data = {}
        if name:
            data['name'] = name
        if private_key:
            data['private_key'] = private_key
        
        return self._make_request('PUT', f'/project/{project_id}/keys/{key_id}', data=data)
    
    def delete_ssh_key(self, project_id: int, key_id: int) -> bool:
        """Delete SSH key"""
        result = self._make_request('DELETE', f'/project/{project_id}/keys/{key_id}')
        return result is not None and result.get('success', False)
    
    # Secret Management
    def get_secrets(self, project_id: int) -> List[Dict]:
        """Get all secrets for a project"""
        result = self._make_request('GET', f'/project/{project_id}/secrets')
        return result if result else []
    
    def create_secret(self, project_id: int, name: str, value: str, description: str = "") -> Optional[Dict]:
        """Create new secret"""
        data = {
            'name': name,
            'value': value,
            'description': description
        }
        return self._make_request('POST', f'/project/{project_id}/secrets', data=data)
    
    def update_secret(self, project_id: int, secret_id: int, name: str = None, value: str = None, description: str = None) -> Optional[Dict]:
        """Update secret"""
        data = {}
        if name:
            data['name'] = name
        if value:
            data['value'] = value
        if description:
            data['description'] = description
        
        return self._make_request('PUT', f'/project/{project_id}/secrets/{secret_id}', data=data)
    
    def delete_secret(self, project_id: int, secret_id: int) -> bool:
        """Delete secret"""
        result = self._make_request('DELETE', f'/project/{project_id}/secrets/{secret_id}')
        return result is not None and result.get('success', False)
    
    # Template Management
    def get_templates(self, project_id: int) -> List[Dict]:
        """Get all templates for a project"""
        result = self._make_request('GET', f'/project/{project_id}/templates')
        return result if result else []
    
    def create_template(self, project_id: int, name: str, playbook: str, inventory_id: int, 
                       key_id: int, repository_id: int = None, arguments: List[Dict] = None) -> Optional[Dict]:
        """Create new template"""
        data = {
            'name': name,
            'playbook': playbook,
            'inventory_id': inventory_id,
            'key_id': key_id,
            'repository_id': repository_id,
            'arguments': arguments or []
        }
        return self._make_request('POST', f'/project/{project_id}/templates', data=data)
    
    def update_template(self, project_id: int, template_id: int, **kwargs) -> Optional[Dict]:
        """Update template"""
        return self._make_request('PUT', f'/project/{project_id}/templates/{template_id}', data=kwargs)
    
    def delete_template(self, project_id: int, template_id: int) -> bool:
        """Delete template"""
        result = self._make_request('DELETE', f'/project/{project_id}/templates/{template_id}')
        return result is not None and result.get('success', False)
    
    # Inventory Management
    def get_inventories(self, project_id: int) -> List[Dict]:
        """Get all inventories for a project"""
        result = self._make_request('GET', f'/project/{project_id}/inventories')
        return result if result else []
    
    def create_inventory(self, project_id: int, name: str, inventory: str, type: str = "static") -> Optional[Dict]:
        """Create new inventory"""
        data = {
            'name': name,
            'inventory': inventory,
            'type': type
        }
        return self._make_request('POST', f'/project/{project_id}/inventories', data=data)
    
    def update_inventory(self, project_id: int, inventory_id: int, name: str = None, inventory: str = None) -> Optional[Dict]:
        """Update inventory"""
        data = {}
        if name:
            data['name'] = name
        if inventory:
            data['inventory'] = inventory
        
        return self._make_request('PUT', f'/project/{project_id}/inventories/{inventory_id}', data=data)
    
    def delete_inventory(self, project_id: int, inventory_id: int) -> bool:
        """Delete inventory"""
        result = self._make_request('DELETE', f'/project/{project_id}/inventories/{inventory_id}')
        return result is not None and result.get('success', False)
    
    # Task Management
    def get_tasks(self, project_id: int, template_id: int = None) -> List[Dict]:
        """Get all tasks for a project or template"""
        endpoint = f'/project/{project_id}/tasks'
        if template_id:
            endpoint += f'?template_id={template_id}'
        
        result = self._make_request('GET', endpoint)
        return result if result else []
    
    def get_task(self, project_id: int, task_id: int) -> Optional[Dict]:
        """Get specific task"""
        return self._make_request('GET', f'/project/{project_id}/tasks/{task_id}')
    
    def run_template(self, project_id: int, template_id: int, debug: bool = False, dry_run: bool = False, 
                    extra_vars: Dict = None) -> Optional[Dict]:
        """Run a template"""
        data = {
            'debug': debug,
            'dry_run': dry_run,
            'extra_vars': extra_vars or {}
        }
        return self._make_request('POST', f'/project/{project_id}/templates/{template_id}/run', data=data)
    
    # Utility Methods
    def find_project_by_name(self, name: str) -> Optional[Dict]:
        """Find project by name"""
        projects = self.get_projects()
        for project in projects:
            if project.get('name') == name:
                return project
        return None
    
    def find_inventory_by_name(self, project_id: int, name: str) -> Optional[Dict]:
        """Find inventory by name"""
        inventories = self.get_inventories(project_id)
        for inventory in inventories:
            if inventory.get('name') == name:
                return inventory
        return None
    
    def find_key_by_name(self, project_id: int, name: str) -> Optional[Dict]:
        """Find SSH key by name"""
        keys = self.get_ssh_keys(project_id)
        for key in keys:
            if key.get('name') == name:
                return key
        return None
    
    def find_secret_by_name(self, project_id: int, name: str) -> Optional[Dict]:
        """Find secret by name"""
        secrets = self.get_secrets(project_id)
        for secret in secrets:
            if secret.get('name') == name:
                return secret
        return None
    
    def get_project_status(self, project_id: int) -> Dict:
        """Get comprehensive project status"""
        project = self.get_project(project_id)
        if not project:
            return {"error": "Project not found"}
        
        return {
            "project": project,
            "repositories": self.get_repositories(project_id),
            "inventories": self.get_inventories(project_id),
            "keys": self.get_ssh_keys(project_id),
            "secrets": self.get_secrets(project_id),
            "templates": self.get_templates(project_id)
        }

def main():
    """Example usage of Semaphore API client"""
    if len(sys.argv) < 4:
        print("Usage: python semaphore_api_client.py <base_url> <username> <password> [command]")
        print("Commands: status, projects, secrets, templates")
        sys.exit(1)
    
    base_url = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    command = sys.argv[4] if len(sys.argv) > 4 else "status"
    
    # Initialize client
    client = SemaphoreAPIClient(base_url, username, password)
    
    if not client.authenticate():
        print("Failed to authenticate with Semaphore")
        sys.exit(1)
    
    if command == "status":
        print("Semaphore API Status:")
        print(f"Base URL: {client.base_url}")
        print(f"Authenticated: {client.authenticated}")
        
    elif command == "projects":
        print("Projects:")
        projects = client.get_projects()
        for project in projects:
            print(f"  - {project.get('name')} (ID: {project.get('id')})")
            
    elif command == "secrets":
        project_id = input("Enter project ID: ")
        if project_id.isdigit():
            secrets = client.get_secrets(int(project_id))
            print(f"Secrets for project {project_id}:")
            for secret in secrets:
                print(f"  - {secret.get('name')} (ID: {secret.get('id')})")
                
    elif command == "templates":
        project_id = input("Enter project ID: ")
        if project_id.isdigit():
            templates = client.get_templates(int(project_id))
            print(f"Templates for project {project_id}:")
            for template in templates:
                print(f"  - {template.get('name')} (ID: {template.get('id')})")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
