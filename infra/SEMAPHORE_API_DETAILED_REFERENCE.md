# Semaphore API Detailed Reference

Comprehensive API documentation based on TK-Proxmox infrastructure implementation.

## Authentication & Session Management

### Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "auth": "admin",
  "password": "8fewWER8382"
}
```

**Success Response**: `204 No Content`
**Sets session cookies for subsequent requests**

## Project Configuration

### Our Project Setup
- **Project ID**: 4
- **Repository ID**: 1 (Local file repository)
- **Inventory ID**: 7 (Network switches)
- **Environment ID**: 5 (Default environment)
- **Base URL**: `http://172.23.5.22:3000/api`

## Template Management API

### Create Template
```bash
POST /api/project/4/templates
```

**Required Fields**:
- `name`: Template display name
- `playbook`: Path to playbook file
- `inventory_id`: Inventory to use
- `repository_id`: Repository containing playbook
- `environment_id`: Environment configuration
- `app`: Must be "ansible"
- `arguments`: JSON string (usually "[]")

**Optional Fields**:
- `survey_vars`: Array of survey variable objects

### Survey Variable Structure
```json
{
  "name": "variable_name",
  "title": "Display Title",
  "required": true,
  "type": "enum",
  "description": "User description",
  "values": [
    {"name": "Display Name", "value": "actual_value"}
  ],
  "default_value": "default_value"
}
```

### Update Template
```bash
PUT /api/project/4/templates/{id}
```

**Critical Requirements**:
1. Must include `id` field in body matching URL parameter
2. Must include ALL required fields (same as create)
3. Use `survey_vars` field (not `survey`)

### Delete Template
```bash
DELETE /api/project/4/templates/{id}
```

## Task Management API

### Create Task
```bash
POST /api/project/4/tasks
```

**Request Body**:
```json
{
  "template_id": 22,
  "debug": false,
  "dry_run": false,
  "diff": false,
  "playbook": "playbooks/network/list_switch_interfaces.yml",
  "environment_id": 5,
  "inventory_id": 7,
  "extra_vars": "{\"switch_name\": \"tks-sw-arista-core-1\"}"
}
```

### Get Task Status
```bash
GET /api/project/4/tasks/{task_id}
```

## Repository Management

### Repository Structure
Our local repository configuration:
```json
{
  "id": 1,
  "name": "Local",
  "git_url": "file:///tmp/semaphore",
  "git_branch": "main",
  "ssh_key_id": 4
}
```

### File Path Resolution
Semaphore expects files at:
```
/tmp/semaphore/project_4/repository_1_template_{id}/playbooks/
```

## Common Error Solutions

### Error: "Invalid app id"
**Cause**: Missing `app` field in template requests
**Solution**: Include `"app": "ansible"`

### Error: "template id in URL and in body must be the same"
**Cause**: Missing `id` field in update request body
**Solution**: Include `"id": template_id` in request body

### Error: "playbook could not be found"
**Cause**: Repository path issues or missing files
**Solution**: 
1. Verify repository configuration
2. Create expected directory structure
3. Copy files to correct location

### Error: Survey variables not appearing
**Cause**: Incorrect field name or structure
**Solution**:
1. Use `survey_vars` field (not `survey`)
2. Include correct data structure with `values` array
3. Include all required template fields

## Python Implementation Examples

### Complete Template Creation
```python
import requests
import json

def create_template_with_survey():
    base_url = 'http://172.23.5.22:3000'
    api_url = f'{base_url}/api'
    
    # Authenticate
    session = requests.Session()
    auth_data = {'auth': 'admin', 'password': '8fewWER8382'}
    session.post(f'{api_url}/auth/login', json=auth_data)
    
    # Survey variables
    survey_vars = [
        {
            'name': 'switch_name',
            'title': 'Switch Name',
            'required': True,
            'type': 'enum',
            'description': 'Select the switch to list interfaces for',
            'values': [
                {'name': 'Arista Core Switch', 'value': 'tks-sw-arista-core-1'},
                {'name': 'Cisco Nexus Switch', 'value': 'tks-sw-cis-nexus-1'},
                {'name': 'Access Layer Switch', 'value': 'tks-sw-access-1'}
            ],
            'default_value': 'tks-sw-arista-core-1'
        }
    ]
    
    # Template data
    template_data = {
        'name': 'List Switch Interfaces (with Survey)',
        'playbook': 'playbooks/network/list_switch_interfaces.yml',
        'inventory_id': 7,
        'repository_id': 1,
        'environment_id': 5,
        'app': 'ansible',
        'arguments': '[]',
        'survey_vars': survey_vars
    }
    
    # Create template
    response = session.post(f'{api_url}/project/4/templates', json=template_data)
    return response.json() if response.status_code == 201 else None
```

### Run Task with Parameters
```python
def run_template_task(template_id, extra_vars):
    base_url = 'http://172.23.5.22:3000'
    api_url = f'{base_url}/api'
    
    # Authenticate
    session = requests.Session()
    auth_data = {'auth': 'admin', 'password': '8fewWER8382'}
    session.post(f'{api_url}/auth/login', json=auth_data)
    
    # Task data
    task_data = {
        'template_id': template_id,
        'debug': False,
        'dry_run': False,
        'diff': False,
        'playbook': 'playbooks/network/list_switch_interfaces.yml',
        'environment_id': 5,
        'inventory_id': 7,
        'extra_vars': json.dumps(extra_vars)
    }
    
    # Create task
    response = session.post(f'{api_url}/project/4/tasks', json=task_data)
    return response.json() if response.status_code == 201 else None
```

## Our Working Templates

### Template 14: Switch-Specific VLAN Assignment
- **Status**: ✅ Working
- **Playbook**: `switch_specific_vlan_assignment.yml`
- **Survey Variables**: 4 variables
  - `switch_name` (enum): Device selection
  - `vlan_id` (enum): VLAN ID (2-7)
  - `vlan_desc` (text): Port description
  - `port_interface` (text): Interface name

### Template 22: List Switch Interfaces
- **Status**: ✅ Working with Survey Variables
- **Playbook**: `list_switch_interfaces.yml`
- **Survey Variables**: 1 variable
  - `switch_name` (enum): Device selection with 3 options

## Device Inventory

### Network Device Names
- `tks-sw-arista-core-1`: Arista Core Switch (172.23.7.10)
- `tks-sw-cis-nexus-1`: Cisco Nexus Switch (210.141.77.15)
- `tks-sw-access-1`: Access Layer Switch (172.23.7.20)

### VLAN Assignments
- VLAN 2: SERVERS
- VLAN 3: WORKSTATIONS
- VLAN 4: GUEST
- VLAN 5: IOT
- VLAN 6: GAMING
- VLAN 7: MANAGEMENT

## File System Requirements

### Directory Structure for Local Repository
```
/tmp/semaphore/
├── project_4/
│   ├── repository_1_template_22/
│   │   └── playbooks/
│   │       └── network/
│   │           └── list_switch_interfaces.yml
│   └── inventory_7
```

### Required Files
- Playbook files in correct repository path
- Inventory files in project directory
- Proper file permissions for Semaphore access

## API Response Codes

### Success Codes
- `200`: OK (GET requests)
- `201`: Created (POST requests)
- `204`: No Content (DELETE requests)

### Error Codes
- `400`: Bad Request (validation errors)
- `404`: Not Found (resource doesn't exist)
- `500`: Internal Server Error

## Best Practices

1. **Always include all required fields** when updating templates
2. **Use session-based authentication** for multiple API calls
3. **Verify file paths** before creating templates
4. **Test survey variables** in the UI after creation
5. **Use descriptive names** for templates and variables
6. **Include default values** for required survey variables

## Troubleshooting Checklist

- [ ] Authentication successful (204 response)
- [ ] All required template fields included
- [ ] Survey variables use correct structure
- [ ] File paths exist and are accessible
- [ ] Repository configuration is correct
- [ ] Task creation returns 201 status

---
*Documentation based on TK-Proxmox project implementation*
*Last Updated: September 25, 2025*
