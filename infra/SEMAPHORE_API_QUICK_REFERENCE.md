# Semaphore API Quick Reference

Based on TK-Proxmox project implementation experience.

## Base Configuration
- **Base URL**: `http://172.23.5.22:3000/api`
- **Project ID**: `4`
- **Repository ID**: `1`
- **Inventory ID**: `7`
- **Environment ID**: `5`

## Authentication
```python
session = requests.Session()
auth_data = {'auth': 'admin', 'password': 'your_password'}
response = session.post(f'{api_url}/auth/login', json=auth_data)
```

## Template Operations

### Create Template with Survey Variables
```python
template_data = {
    'name': 'Template Name',
    'playbook': 'playbooks/path/to/playbook.yml',
    'inventory_id': 7,
    'repository_id': 1,
    'environment_id': 5,
    'app': 'ansible',
    'arguments': '[]',
    'survey_vars': [
        {
            'name': 'switch_name',
            'title': 'Switch Name',
            'required': True,
            'type': 'enum',
            'description': 'Select the switch',
            'values': [
                {'name': 'Arista Core', 'value': 'tks-sw-arista-core-1'},
                {'name': 'Cisco Nexus', 'value': 'tks-sw-cis-nexus-1'}
            ],
            'default_value': 'tks-sw-arista-core-1'
        }
    ]
}

response = session.post(f'{api_url}/project/4/templates', json=template_data)
```

### Run Task
```python
task_data = {
    'template_id': 22,
    'debug': False,
    'dry_run': False,
    'diff': False,
    'playbook': 'playbooks/network/list_switch_interfaces.yml',
    'environment_id': 5,
    'inventory_id': 7,
    'extra_vars': json.dumps({'switch_name': 'tks-sw-arista-core-1'})
}

response = session.post(f'{api_url}/project/4/tasks', json=task_data)
```

## Common Issues & Solutions

### "Invalid app id" Error
**Solution**: Include `"app": "ansible"` in template requests

### "template id in URL and in body must be the same"
**Solution**: Include `"id": template_id` in request body

### Playbook Not Found
**Solution**: Create directory structure `/tmp/semaphore/project_4/repository_1_template_X/playbooks/`

### Survey Variables Not Working
**Solution**: Use `survey_vars` field (not `survey`) with correct structure

## Working Templates

### Template 14: VLAN Assignment
- **Playbook**: `switch_specific_vlan_assignment.yml`
- **Variables**: switch_name, vlan_id, vlan_desc, port_interface

### Template 22: Interface Listing
- **Playbook**: `list_switch_interfaces.yml`
- **Variables**: switch_name (3 device options)

## Device Names
- `tks-sw-arista-core-1` - Arista Core Switch
- `tks-sw-cis-nexus-1` - Cisco Nexus Switch
- `tks-sw-access-1` - Access Layer Switch

---
*Last Updated: September 25, 2025*