# Semaphore API Reference Guide

## 🎯 Overview

This guide provides comprehensive information for interacting with Ansible Semaphore via its REST API, including authentication methods, endpoint structures, common operations, and troubleshooting based on real-world implementation experience.

## 🔐 Authentication

### Session-Based Authentication (Username/Password)

```python
import requests

# Initialize session
session = requests.Session()
session.headers.update({
    'Content-Type': 'application/json',
    'Accept': 'application/json'
})

# Authenticate
auth_url = f"{base_url}/api/auth/login"
auth_data = {
    'auth': 'admin',
    'password': 'your_password'
}

response = session.post(auth_url, json=auth_data)

# Semaphore returns 204 No Content on successful authentication
if response.status_code == 204:
    print("✅ Authentication successful")
    # Session cookie is automatically handled
else:
    print("❌ Authentication failed")
```

### Token-Based Authentication (API Token)

```python
import requests

# Initialize session with Bearer token
session = requests.Session()
session.headers.update({
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {api_token}'
})

# Test authentication by making a simple request
response = session.get(f"{base_url}/api/projects")
if response.status_code == 200:
    print("✅ Token authentication successful")
else:
    print("❌ Token authentication failed")
```

## 📡 API Endpoint Structure

### Base URL Format
```
http://your-semaphore-host:3000/api
```

### Core Endpoints

| Resource | Endpoint Pattern | Methods |
|----------|------------------|---------|
| Projects | `/projects` | GET, POST |
| Inventories | `/project/{project_id}/inventory` | GET, POST, PUT, DELETE |
| Repositories | `/project/{project_id}/repositories` | GET, POST, PUT, DELETE |
| SSH Keys | `/project/{project_id}/keys` | GET, POST, PUT, DELETE |
| Templates | `/project/{project_id}/templates` | GET, POST, PUT, DELETE |
| Tasks | `/project/{project_id}/tasks` | GET |
| Environments | `/project/{project_id}/environments` | GET, POST, PUT, DELETE |

### ⚠️ Common Endpoint Mistakes

**❌ Incorrect (Plural forms that don't work):**
- `/project/{id}/inventories` → Use `/project/{id}/inventory`
- `/project/{id}/keys` → Actually this one IS correct
- `/project/{id}/secrets` → Use `/project/{id}/keys` for secrets

**✅ Correct Endpoints:**
- `/project/{id}/inventory` (singular)
- `/project/{id}/repositories` (plural)
- `/project/{id}/keys` (plural)
- `/project/{id}/templates` (plural)

## 🔧 Common Operations

### Project Management

```python
# List all projects
def get_projects(session, base_url):
    response = session.get(f"{base_url}/api/projects")
    return response.json() if response.status_code == 200 else None

# Create new project
def create_project(session, base_url, name, alert=False, max_parallel_tasks=1):
    data = {
        'name': name,
        'alert': alert,
        'max_parallel_tasks': max_parallel_tasks
    }
    response = session.post(f"{base_url}/api/projects", json=data)
    return response.json() if response.status_code == 201 else None
```

### Inventory Management

```python
# Get inventories for a project
def get_inventories(session, base_url, project_id):
    response = session.get(f"{base_url}/api/project/{project_id}/inventory")
    return response.json() if response.status_code == 200 else None

# Create inventory
def create_inventory(session, base_url, project_id, name, inventory_content, ssh_key_id=None):
    data = {
        'project_id': project_id,
        'name': name,
        'inventory': inventory_content,
        'type': 'static',
        'ssh_key_id': ssh_key_id
    }
    response = session.post(f"{base_url}/api/project/{project_id}/inventory", json=data)
    return response.json() if response.status_code == 201 else None

# Update inventory
def update_inventory(session, base_url, project_id, inventory_id, name, inventory_content, ssh_key_id=None):
    data = {
        'id': inventory_id,
        'project_id': project_id,
        'name': name,
        'inventory': inventory_content,
        'type': 'static',
        'ssh_key_id': ssh_key_id
    }
    response = session.put(f"{base_url}/api/project/{project_id}/inventory/{inventory_id}", json=data)
    return response.json() if response.status_code == 200 else None
```

### Repository Management

```python
# Get repositories for a project
def get_repositories(session, base_url, project_id):
    response = session.get(f"{base_url}/api/project/{project_id}/repositories")
    return response.json() if response.status_code == 200 else None

# Create repository
def create_repository(session, base_url, project_id, name, git_url, ssh_key_id=None, branch='main'):
    data = {
        'project_id': project_id,
        'name': name,
        'git_url': git_url,
        'ssh_key_id': ssh_key_id,
        'git_branch': branch
    }
    response = session.post(f"{base_url}/api/project/{project_id}/repositories", json=data)
    return response.json() if response.status_code == 201 else None
```

### SSH Key Management

```python
# Get SSH keys for a project
def get_ssh_keys(session, base_url, project_id):
    response = session.get(f"{base_url}/api/project/{project_id}/keys")
    return response.json() if response.status_code == 200 else None

# Create SSH key
def create_ssh_key(session, base_url, project_id, name, private_key):
    data = {
        'project_id': project_id,
        'name': name,
        'type': 'ssh',
        'ssh': private_key
    }
    response = session.post(f"{base_url}/api/project/{project_id}/keys", json=data)
    return response.json() if response.status_code == 201 else None

# Create secret/password
def create_secret(session, base_url, project_id, name, secret_value):
    data = {
        'project_id': project_id,
        'name': name,
        'type': 'password',
        'data': secret_value
    }
    response = session.post(f"{base_url}/api/project/{project_id}/keys", json=data)
    return response.json() if response.status_code == 201 else None
```

### Template Management

```python
# Get templates for a project
def get_templates(session, base_url, project_id):
    response = session.get(f"{base_url}/api/project/{project_id}/templates")
    return response.json() if response.status_code == 200 else None

# Create template
def create_template(session, base_url, project_id, name, playbook, inventory_id, repository_id, environment_id=None):
    data = {
        'project_id': project_id,
        'name': name,
        'playbook': playbook,
        'inventory_id': inventory_id,
        'repository_id': repository_id,
        'environment_id': environment_id,
        'app': 'ansible',
        'arguments': []
    }
    response = session.post(f"{base_url}/api/project/{project_id}/templates", json=data)
    return response.json() if response.status_code == 201 else None
```

## 🛠️ Complete Python Client Example

```python
#!/usr/bin/env python3

import requests
import logging
from typing import Optional, Dict, List

class SemaphoreApiClient:
    """Complete Semaphore API client with error handling"""
    
    def __init__(self, base_url: str, username: str = None, password: str = None, api_token: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api"
        self.username = username
        self.password = password
        self.api_token = api_token
        self.session = requests.Session()
        self.authenticated = False
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def authenticate(self) -> bool:
        """Authenticate with Semaphore API"""
        if self.api_token:
            # Token authentication
            self.session.headers.update({'Authorization': f'Bearer {self.api_token}'})
            try:
                response = self.session.get(f"{self.api_url}/projects")
                response.raise_for_status()
                self.authenticated = True
                return True
            except requests.exceptions.RequestException:
                return False
                
        elif self.username and self.password:
            # Session authentication
            try:
                auth_url = f"{self.api_url}/auth/login"
                auth_data = {'auth': self.username, 'password': self.password}
                response = self.session.post(auth_url, json=auth_data)
                
                if response.status_code == 204:  # Semaphore returns 204 on success
                    self.authenticated = True
                    return True
                return False
            except requests.exceptions.RequestException:
                return False
        return False
    
    def _make_request(self, method: str, endpoint: str, data: dict = None) -> Optional[Dict]:
        """Make authenticated API request with proper error handling"""
        if not self.authenticated:
            if not self.authenticate():
                return None
        
        url = f"{self.api_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                return None
            
            response.raise_for_status()
            
            # Handle 204 No Content responses
            if response.status_code == 204:
                return {"success": True, "status_code": 204}
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {method} {endpoint} - {e}")
            return None

    # Project methods
    def get_projects(self) -> List[Dict]:
        return self._make_request('GET', '/projects') or []
    
    def create_project(self, name: str, alert: bool = False) -> Optional[Dict]:
        data = {'name': name, 'alert': alert, 'max_parallel_tasks': 1}
        return self._make_request('POST', '/projects', data)

    # Inventory methods
    def get_inventories(self, project_id: int) -> List[Dict]:
        return self._make_request('GET', f'/project/{project_id}/inventory') or []
    
    def create_inventory(self, project_id: int, name: str, inventory_content: str, ssh_key_id: int = None) -> Optional[Dict]:
        data = {
            'project_id': project_id,
            'name': name,
            'inventory': inventory_content,
            'type': 'static',
            'ssh_key_id': ssh_key_id
        }
        return self._make_request('POST', f'/project/{project_id}/inventory', data)
    
    def update_inventory(self, project_id: int, inventory_id: int, name: str, inventory_content: str, ssh_key_id: int = None) -> Optional[Dict]:
        data = {
            'id': inventory_id,
            'project_id': project_id,
            'name': name,
            'inventory': inventory_content,
            'type': 'static',
            'ssh_key_id': ssh_key_id
        }
        return self._make_request('PUT', f'/project/{project_id}/inventory/{inventory_id}', data)

    # Repository methods
    def get_repositories(self, project_id: int) -> List[Dict]:
        return self._make_request('GET', f'/project/{project_id}/repositories') or []
    
    def create_repository(self, project_id: int, name: str, git_url: str, ssh_key_id: int = None, branch: str = 'main') -> Optional[Dict]:
        data = {
            'project_id': project_id,
            'name': name,
            'git_url': git_url,
            'ssh_key_id': ssh_key_id,
            'git_branch': branch
        }
        return self._make_request('POST', f'/project/{project_id}/repositories', data)

    # SSH Key methods
    def get_ssh_keys(self, project_id: int) -> List[Dict]:
        return self._make_request('GET', f'/project/{project_id}/keys') or []
    
    def create_ssh_key(self, project_id: int, name: str, private_key: str) -> Optional[Dict]:
        data = {
            'project_id': project_id,
            'name': name,
            'type': 'ssh',
            'ssh': private_key
        }
        return self._make_request('POST', f'/project/{project_id}/keys', data)

    # Template methods
    def get_templates(self, project_id: int) -> List[Dict]:
        return self._make_request('GET', f'/project/{project_id}/templates') or []
    
    def create_template(self, project_id: int, name: str, playbook: str, inventory_id: int, repository_id: int, environment_id: int = None) -> Optional[Dict]:
        data = {
            'project_id': project_id,
            'name': name,
            'playbook': playbook,
            'inventory_id': inventory_id,
            'repository_id': repository_id,
            'environment_id': environment_id,
            'app': 'ansible',
            'arguments': []
        }
        return self._make_request('POST', f'/project/{project_id}/templates', data)

    # Task methods
    def get_tasks(self, project_id: int) -> List[Dict]:
        return self._make_request('GET', f'/project/{project_id}/tasks') or []
```

## 🔍 Endpoint Discovery & Troubleshooting

### Testing API Endpoints

When working with Semaphore API, endpoint structures can vary. Use this systematic approach:

```python
def test_endpoint_patterns(client, project_id, resource_name):
    """Test different endpoint patterns to find the correct one"""
    patterns = [
        f'/project/{project_id}/{resource_name}',
        f'/project/{project_id}/{resource_name}s',
        f'/{resource_name}',
        f'/{resource_name}s'
    ]
    
    working_endpoints = []
    
    for pattern in patterns:
        try:
            response = client.session.get(f"{client.api_url}{pattern}")
            if response.status_code == 200:
                working_endpoints.append((pattern, response.json()))
                print(f"✅ {pattern} - Works")
            else:
                print(f"❌ {pattern} - {response.status_code}")
        except Exception as e:
            print(f"❌ {pattern} - Error: {e}")
    
    return working_endpoints
```

### Common HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | OK | Request successful, data returned |
| 201 | Created | Resource created successfully |
| 204 | No Content | Success (auth, delete) - no response body |
| 400 | Bad Request | Check request data format |
| 401 | Unauthorized | Check authentication |
| 403 | Forbidden | Check permissions |
| 404 | Not Found | Check endpoint URL |
| 500 | Server Error | Check Semaphore logs |

## 📋 Resource Management Patterns

### Creating Resources with Dependencies

Resources in Semaphore have dependencies. Follow this order:

1. **Projects** (no dependencies)
2. **SSH Keys** (requires project)
3. **Repositories** (requires project, optionally SSH key)
4. **Inventories** (requires project, optionally SSH key)
5. **Environments** (requires project)
6. **Templates** (requires project, inventory, repository, optionally environment)

```python
# Example: Complete setup workflow
def setup_project_infrastructure(client, project_name):
    # 1. Create project
    project = client.create_project(project_name)
    project_id = project['id']
    
    # 2. Create SSH key
    ssh_key = client.create_ssh_key(project_id, "Default SSH Key", private_key_content)
    ssh_key_id = ssh_key['id']
    
    # 3. Create repository
    repository = client.create_repository(project_id, "Local", "file:///tmp/semaphore", ssh_key_id)
    repository_id = repository['id']
    
    # 4. Create inventory
    inventory = client.create_inventory(project_id, "Network Infrastructure", inventory_content, ssh_key_id)
    inventory_id = inventory['id']
    
    # 5. Create template
    template = client.create_template(project_id, "Network Operations", "playbooks/network/operations.yml", inventory_id, repository_id)
    
    return {
        'project_id': project_id,
        'ssh_key_id': ssh_key_id,
        'repository_id': repository_id,
        'inventory_id': inventory_id,
        'template_id': template['id']
    }
```

## 🔒 Security Best Practices

### Credential Management

```python
# ✅ Good: Use environment variables
import os
api_token = os.getenv('SEMAPHORE_API_TOKEN')
password = os.getenv('SEMAPHORE_PASSWORD')

# ❌ Bad: Hardcoded credentials
api_token = "abc123..."  # Never do this
```

### Secrets vs SSH Keys

In Semaphore, both secrets and SSH keys are managed through the `/keys` endpoint:

```python
# SSH Key (type: 'ssh')
ssh_key_data = {
    'project_id': project_id,
    'name': 'Network SSH Key',
    'type': 'ssh',
    'ssh': private_key_content
}

# Password Secret (type: 'password')
secret_data = {
    'project_id': project_id,
    'name': 'Network Admin Password',
    'type': 'password',
    'data': password_value
}
```

## 🐛 Common Issues & Solutions

### Issue 1: Authentication Failures

**Problem**: `Authentication failed: No session cookie received`

**Solution**: 
- Ensure you're checking for status code 204 (not 200)
- Verify the session object is reused for subsequent requests

```python
# ✅ Correct
if response.status_code == 204:
    self.authenticated = True

# ❌ Incorrect
if response.status_code == 200:  # Semaphore doesn't return 200 for auth
    self.authenticated = True
```

### Issue 2: Resource Not Visible in UI

**Problem**: Resources created via API don't appear in Semaphore UI

**Solution**: 
- Use correct endpoint patterns (see endpoint table above)
- Ensure all required fields are provided
- Check that resources are linked properly (inventory → SSH key)

### Issue 3: Template Creation Errors

**Problem**: `Invalid app id` or template creation fails

**Solution**:
- Ensure inventory has an associated SSH key
- Use `app: 'ansible'` (not `app: 'Ansible'`)
- Include `arguments: []` field
- Reference existing inventory_id, repository_id, environment_id

```python
# ✅ Correct template structure
template_data = {
    'project_id': project_id,
    'name': 'My Template',
    'playbook': 'playbooks/my_playbook.yml',
    'inventory_id': inventory_id,
    'repository_id': repository_id,
    'environment_id': environment_id,  # Can be None
    'app': 'ansible',  # Must be lowercase
    'arguments': []    # Must be included
}
```

### Issue 4: Inventory Update Failures

**Problem**: `Inventory ID in body and URL must be the same`

**Solution**: Include both `id` and `project_id` in request body

```python
# ✅ Correct update structure
update_data = {
    'id': inventory_id,        # Must match URL
    'project_id': project_id,  # Must match URL
    'name': inventory_name,
    'inventory': inventory_content,
    'type': 'static',
    'ssh_key_id': ssh_key_id
}
```

## 📊 Response Handling

### Successful Responses

```python
def handle_response(response):
    """Proper response handling for Semaphore API"""
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 201:
        return response.json()  # Created
    elif response.status_code == 204:
        return {"success": True}  # No content (delete, auth)
    else:
        logging.error(f"API Error: {response.status_code} - {response.text}")
        return None
```

### Error Response Structure

Semaphore error responses typically have this structure:

```json
{
  "error": "Error message description"
}
```

## 🔄 Batch Operations

### Creating Multiple Resources

```python
def create_multiple_templates(client, project_id, templates_config):
    """Create multiple templates efficiently"""
    created_templates = []
    failed_templates = []
    
    for config in templates_config:
        try:
            template = client.create_template(
                project_id=project_id,
                name=config['name'],
                playbook=config['playbook'],
                inventory_id=config['inventory_id'],
                repository_id=config['repository_id'],
                environment_id=config.get('environment_id')
            )
            
            if template:
                created_templates.append(template)
                print(f"✅ Created: {config['name']} (ID: {template['id']})")
            else:
                failed_templates.append(config['name'])
                print(f"❌ Failed: {config['name']}")
                
        except Exception as e:
            failed_templates.append(config['name'])
            print(f"❌ Error creating {config['name']}: {e}")
    
    return created_templates, failed_templates
```

## 🧪 Testing & Validation

### API Health Check

```python
def test_semaphore_api(base_url, api_token):
    """Complete API health check"""
    client = SemaphoreApiClient(base_url, api_token=api_token)
    
    if not client.authenticate():
        print("❌ Authentication failed")
        return False
    
    # Test basic operations
    projects = client.get_projects()
    if not projects:
        print("❌ Cannot fetch projects")
        return False
    
    project_id = projects[0]['id']
    
    # Test resource access
    inventories = client.get_inventories(project_id)
    repositories = client.get_repositories(project_id)
    templates = client.get_templates(project_id)
    ssh_keys = client.get_ssh_keys(project_id)
    
    print(f"✅ API Health Check Passed")
    print(f"   Projects: {len(projects)}")
    print(f"   Inventories: {len(inventories)}")
    print(f"   Repositories: {len(repositories)}")
    print(f"   Templates: {len(templates)}")
    print(f"   SSH Keys: {len(ssh_keys)}")
    
    return True
```

### Endpoint Discovery Tool

```python
def discover_api_endpoints(client, project_id):
    """Discover available API endpoints"""
    base_endpoints = [
        '/projects',
        '/project',
        f'/project/{project_id}/inventory',
        f'/project/{project_id}/repositories',
        f'/project/{project_id}/keys',
        f'/project/{project_id}/templates',
        f'/project/{project_id}/tasks',
        f'/project/{project_id}/environments'
    ]
    
    working_endpoints = []
    
    for endpoint in base_endpoints:
        try:
            response = client.session.get(f"{client.api_url}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                working_endpoints.append({
                    'endpoint': endpoint,
                    'status': 'Working',
                    'count': len(data) if isinstance(data, list) else 'Object'
                })
            else:
                working_endpoints.append({
                    'endpoint': endpoint,
                    'status': f'Error {response.status_code}',
                    'count': 'N/A'
                })
        except Exception as e:
            working_endpoints.append({
                'endpoint': endpoint,
                'status': f'Exception: {e}',
                'count': 'N/A'
            })
    
    return working_endpoints
```

## 📚 Configuration Examples

### Local Repository Setup

```python
# For local Git repositories (like /tmp/semaphore)
repository_config = {
    'name': 'Local',
    'git_url': 'file:///tmp/semaphore',
    'git_branch': 'main',
    'ssh_key_id': ssh_key_id  # Optional for local repos
}
```

### Network Inventory Template

```yaml
---
# Example network inventory structure
core_network:
  children:
    firewalls:
      hosts:
        tks-fw-opnsense-1:
          ansible_host: 172.23.7.1
          device_type: opnsense
          
    switches:
      hosts:
        tks-sw-arista-core-1:
          ansible_host: 172.23.7.10
          device_type: arista_eos
          ansible_connection: network_cli
          ansible_network_os: eos
```

### Template Extra Variables

```json
{
  "operation": "health_check",
  "target_device": "tks-sw-arista-core-1",
  "semaphore_admin_user": "admin",
  "semaphore_admin_password": "{{ .Secret \"Network Admin Password\" }}",
  "semaphore_enable_password": "{{ .Secret \"Network Enable Password\" }}"
}
```

## 🚨 Troubleshooting Guide

### Debug API Calls

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Add request/response logging
def debug_request(method, url, data=None):
    print(f"🔍 DEBUG: {method} {url}")
    if data:
        print(f"📤 Request Data: {data}")
    
    response = session.request(method, url, json=data)
    
    print(f"📥 Response: {response.status_code}")
    print(f"📥 Content: {response.text[:200]}...")
    
    return response
```

### Common Error Messages

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `Invalid project ID` | Wrong project ID in URL | Verify project exists |
| `Inventory ID in body and URL must be the same` | Missing ID in request body | Add `id` field to data |
| `Invalid app id` | Template not linked to inventory with SSH key | Associate SSH key with inventory |
| `404 Not Found` | Wrong endpoint URL | Check endpoint patterns |
| `400 Bad Request` | Invalid request data | Validate all required fields |

### API Rate Limiting

Semaphore doesn't typically implement rate limiting, but use these practices:

```python
import time

def rate_limited_requests(requests_list, delay=0.1):
    """Execute requests with delay to prevent overload"""
    results = []
    for request_func in requests_list:
        result = request_func()
        results.append(result)
        time.sleep(delay)
    return results
```

## 🔧 Advanced Usage

### Bulk Resource Management

```python
def bulk_update_inventories(client, project_id, updates):
    """Update multiple inventories with IP address changes"""
    for inventory_id, replacements in updates.items():
        # Get current inventory
        inventories = client.get_inventories(project_id)
        current_inv = next((inv for inv in inventories if inv['id'] == inventory_id), None)
        
        if current_inv:
            content = current_inv['inventory']
            
            # Apply replacements
            for old_value, new_value in replacements.items():
                content = content.replace(old_value, new_value)
            
            # Update inventory
            client.update_inventory(project_id, inventory_id, current_inv['name'], content, current_inv.get('ssh_key_id'))
```

### Template Validation

```python
def validate_template_structure(template_data):
    """Validate template data before creation"""
    required_fields = ['project_id', 'name', 'playbook', 'inventory_id', 'repository_id']
    
    for field in required_fields:
        if field not in template_data:
            raise ValueError(f"Missing required field: {field}")
    
    # Ensure app is lowercase
    if 'app' in template_data and template_data['app'] != 'ansible':
        template_data['app'] = 'ansible'
    
    # Ensure arguments is a list
    if 'arguments' not in template_data:
        template_data['arguments'] = []
    
    return template_data
```

## 📖 Integration Examples

### Command Line Interface

```python
#!/usr/bin/env python3
import argparse
from semaphore_api_client import SemaphoreApiClient

def main():
    parser = argparse.ArgumentParser(description="Semaphore CLI")
    parser.add_argument('--url', required=True, help='Semaphore URL')
    parser.add_argument('--token', required=True, help='API Token')
    parser.add_argument('command', choices=['projects', 'inventories', 'templates'])
    parser.add_argument('--project-id', type=int, help='Project ID')
    
    args = parser.parse_args()
    
    client = SemaphoreApiClient(args.url, api_token=args.token)
    
    if not client.authenticate():
        print("❌ Authentication failed")
        return 1
    
    if args.command == 'projects':
        projects = client.get_projects()
        for project in projects:
            print(f"• {project['name']} (ID: {project['id']})")
    
    elif args.command == 'inventories' and args.project_id:
        inventories = client.get_inventories(args.project_id)
        for inventory in inventories:
            print(f"• {inventory['name']} (ID: {inventory['id']})")
    
    elif args.command == 'templates' and args.project_id:
        templates = client.get_templates(args.project_id)
        for template in templates:
            print(f"• {template['name']} (ID: {template['id']})")
    
    return 0

if __name__ == "__main__":
    exit(main())
```

### CI/CD Integration

```yaml
# Example GitHub Actions workflow
name: Update Semaphore Templates
on:
  push:
    paths: ['ansible/playbooks/**']

jobs:
  update-templates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Update Semaphore Templates
        env:
          SEMAPHORE_URL: ${{ secrets.SEMAPHORE_URL }}
          SEMAPHORE_TOKEN: ${{ secrets.SEMAPHORE_TOKEN }}
        run: |
          python3 scripts/update_semaphore_templates.py
```

## 📁 File Structure

For a complete Semaphore API integration project:

```
project/
├── scripts/
│   ├── semaphore_api_client.py      # Main API client
│   ├── semaphore_cli.py             # Command line interface
│   └── update_templates.py          # Automation scripts
├── config/
│   └── semaphore_config.json        # Configuration file
├── inventories/
│   ├── production.yml               # Production inventory
│   └── staging.yml                  # Staging inventory
└── docs/
    └── SEMAPHORE_API_REFERENCE.md   # This guide
```

## 🔗 Additional Resources

- **Semaphore Documentation**: https://docs.semaphoreui.com/
- **Semaphore GitHub**: https://github.com/ansible-semaphore/semaphore
- **API Swagger Documentation**: `http://your-semaphore:3000/swagger/index.html`
- **Ansible Documentation**: https://docs.ansible.com/

## 🤝 Contributing

When extending this API client:

1. **Test thoroughly** in a development environment
2. **Handle errors gracefully** with proper logging
3. **Follow REST conventions** for new endpoints
4. **Document new methods** with examples
5. **Add validation** for input parameters

## 📄 License

This API reference is part of the TK-Proxmox infrastructure automation project.

---

**Last Updated**: Based on Semaphore UI version with extensive real-world testing and implementation experience.
