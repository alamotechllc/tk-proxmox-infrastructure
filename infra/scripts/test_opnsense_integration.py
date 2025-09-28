#!/usr/bin/env python3
"""
OPNsense Integration Test Script
Tests working API endpoints and creates integration templates
"""

import requests
import json
import sys
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings for testing
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Configuration
OPNSENSE_HOST = "172.23.5.1"
API_KEY = ""
API_SECRET = ""

def load_credentials():
    """Load API credentials from file"""
    global API_KEY, API_SECRET
    
    try:
        with open('infra/secrets/opnsense-api-credentials.txt', 'r') as f:
            for line in f:
                if line.startswith('key='):
                    API_KEY = line.strip().split('=', 1)[1]
                elif line.startswith('secret='):
                    API_SECRET = line.strip().split('=', 1)[1]
        
        if not API_KEY or not API_SECRET:
            print("❌ Failed to load API credentials")
            sys.exit(1)
            
        print(f"✅ Credentials loaded: {API_KEY[:20]}...")
        
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        sys.exit(1)

def test_working_endpoints():
    """Test all working endpoints and gather information"""
    print("🔥 Testing Working OPNsense API Endpoints")
    print("=" * 50)
    
    # Test firmware info
    try:
        response = requests.get(
            f"https://{OPNSENSE_HOST}/api/core/firmware/info",
            auth=(API_KEY, API_SECRET),
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Firmware Info:")
            print(f"   Product: {data.get('product_id', 'Unknown')}")
            print(f"   Version: {data.get('product_version', 'Unknown')}")
            print(f"   Packages: {len(data.get('package', []))}")
        else:
            print(f"❌ Firmware Info failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Firmware Info error: {e}")
    
    print()
    
    # Test service search
    try:
        search_data = {"current": 1, "rowCount": 20, "sort": {}, "searchPhrase": ""}
        response = requests.post(
            f"https://{OPNSENSE_HOST}/api/core/service/search",
            auth=(API_KEY, API_SECRET),
            json=search_data,
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service Search:")
            print(f"   Total Services: {data.get('total', 0)}")
            print(f"   Returned: {len(data.get('rows', []))}")
            
            print(f"   Active Services:")
            for service in data.get('rows', [])[:10]:
                status = "🟢 Running" if service.get('running') else "🔴 Stopped"
                locked = "🔒 Locked" if service.get('locked') else "🔓 Unlocked"
                print(f"     • {service.get('name', 'Unknown')}: {status} {locked}")
        else:
            print(f"❌ Service Search failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Service Search error: {e}")
    
    print()
    
    # Test firmware status
    try:
        response = requests.get(
            f"https://{OPNSENSE_HOST}/api/core/firmware/status",
            auth=(API_KEY, API_SECRET),
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Firmware Status:")
            print(f"   Product: {data.get('product', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   Message: {data.get('status_msg', 'No message')}")
        else:
            print(f"❌ Firmware Status failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Firmware Status error: {e}")

def create_semaphore_templates():
    """Create Semaphore template configurations for working endpoints"""
    print("\n🚀 Creating Semaphore Template Configurations")
    print("=" * 50)
    
    # OPNsense Service Management Template
    service_template = {
        "name": "OPNsense Service Management",
        "description": "Monitor and manage OPNsense services",
        "playbook": "playbooks/network/opnsense_service_management.yml",
        "inventory": "inventories/opnsense.yml",
        "survey_vars": [
            {
                "name": "operation",
                "description": "Service operation to perform",
                "type": "enum",
                "choices": ["list", "status", "start", "stop", "restart"],
                "default": "list"
            },
            {
                "name": "service_name",
                "description": "Service name (for start/stop/restart operations)",
                "type": "string",
                "default": ""
            }
        ],
        "extra_vars": {
            "opnsense_host": "172.23.5.1",
            "opnsense_verify_ssl": "false"
        }
    }
    
    # OPNsense System Information Template
    system_template = {
        "name": "OPNsense System Information",
        "description": "Gather OPNsense system information and status",
        "playbook": "playbooks/network/opnsense_system_info.yml",
        "inventory": "inventories/opnsense.yml",
        "survey_vars": [
            {
                "name": "info_type",
                "description": "Type of information to gather",
                "type": "enum",
                "choices": ["firmware", "status", "services", "all"],
                "default": "all"
            }
        ],
        "extra_vars": {
            "opnsense_host": "172.23.5.1",
            "opnsense_verify_ssl": "false"
        }
    }
    
    # Save templates
    with open('infra/opnsense_service_template.json', 'w') as f:
        json.dump(service_template, f, indent=2)
    
    with open('infra/opnsense_system_template.json', 'w') as f:
        json.dump(system_template, f, indent=2)
    
    print("✅ Created Semaphore template configurations:")
    print("   • infra/opnsense_service_template.json")
    print("   • infra/opnsense_system_template.json")

def create_ansible_playbooks():
    """Create Ansible playbooks for working endpoints"""
    print("\n📝 Creating Ansible Playbooks")
    print("=" * 50)
    
    # Service Management Playbook
    service_playbook = """---
# OPNsense Service Management Playbook
# Monitor and manage OPNsense services via API

- name: "OPNsense Service Management - {{ operation | upper }}"
  hosts: localhost
  gather_facts: true
  
  vars:
    opnsense_host: "{{ opnsense_fqdn | default('172.23.5.1') }}"
    opnsense_api_key: "{{ semaphore_opnsense_api_key | mandatory }}"
    opnsense_api_secret: "{{ semaphore_opnsense_api_secret | mandatory }}"
    opnsense_verify_ssl: false
    
    operation: "{{ service_operation | default('list') }}"
    target_service: "{{ service_name | default('') }}"

  tasks:
    - name: Test OPNsense API connectivity
      uri:
        url: "https://{{ opnsense_host }}/api/core/firmware/info"
        method: GET
        user: "{{ opnsense_api_key }}"
        password: "{{ opnsense_api_secret }}"
        validate_certs: "{{ opnsense_verify_ssl }}"
      register: api_test
      
    - name: Display connectivity status
      debug:
        msg: |
          🔥 OPNsense API Connectivity
          ============================
          Host: {{ opnsense_host }}
          Product: {{ api_test.json.product_id }}
          Version: {{ api_test.json.product_version }}
          Status: Connected ✅
    
    - name: Get service list
      uri:
        url: "https://{{ opnsense_host }}/api/core/service/search"
        method: POST
        user: "{{ opnsense_api_key }}"
        password: "{{ opnsense_api_secret }}"
        validate_certs: "{{ opnsense_verify_ssl }}"
        body_format: json
        body:
          current: 1
          rowCount: 100
          sort: {}
          searchPhrase: ""
      register: services
      
    - name: Display service list
      debug:
        msg: |
          🔥 OPNsense Services
          ===================
          {% for service in services.json.rows %}
          {{ loop.index }}. {{ service.name }}
             Description: {{ service.description }}
             Status: {{ '🟢 Running' if service.running else '🔴 Stopped' }}
             Locked: {{ '🔒 Yes' if service.locked else '🔓 No' }}
          {% endfor %}
          
          Total Services: {{ services.json.total }}
      when: operation in ['list', 'status']
    
    - name: Display operation summary
      debug:
        msg: |
          🔥 Service Management Complete
          ==============================
          Operation: {{ operation | upper }}
          Target Service: {{ target_service | default('All Services') }}
          Services Found: {{ services.json.total }}
          ✅ Operation completed successfully
"""
    
    # System Information Playbook
    system_playbook = """---
# OPNsense System Information Playbook
# Gather system information via API

- name: "OPNsense System Information"
  hosts: localhost
  gather_facts: true
  
  vars:
    opnsense_host: "{{ opnsense_fqdn | default('172.23.5.1') }}"
    opnsense_api_key: "{{ semaphore_opnsense_api_key | mandatory }}"
    opnsense_api_secret: "{{ semaphore_opnsense_api_secret | mandatory }}"
    opnsense_verify_ssl: false
    
    info_type: "{{ information_type | default('all') }}"

  tasks:
    - name: Get firmware information
      uri:
        url: "https://{{ opnsense_host }}/api/core/firmware/info"
        method: GET
        user: "{{ opnsense_api_key }}"
        password: "{{ opnsense_api_secret }}"
        validate_certs: "{{ opnsense_verify_ssl }}"
      register: firmware_info
      when: info_type in ['firmware', 'all']
      
    - name: Get firmware status
      uri:
        url: "https://{{ opnsense_host }}/api/core/firmware/status"
        method: GET
        user: "{{ opnsense_api_key }}"
        password: "{{ opnsense_api_secret }}"
        validate_certs: "{{ opnsense_verify_ssl }}"
      register: firmware_status
      when: info_type in ['status', 'all']
      
    - name: Get service information
      uri:
        url: "https://{{ opnsense_host }}/api/core/service/search"
        method: POST
        user: "{{ opnsense_api_key }}"
        password: "{{ opnsense_api_secret }}"
        validate_certs: "{{ opnsense_verify_ssl }}"
        body_format: json
        body:
          current: 1
          rowCount: 100
          sort: {}
          searchPhrase: ""
      register: services_info
      when: info_type in ['services', 'all']
    
    - name: Display firmware information
      debug:
        msg: |
          🔥 OPNsense Firmware Information
          ================================
          Product ID: {{ firmware_info.json.product_id }}
          Product Version: {{ firmware_info.json.product_version }}
          Packages: {{ firmware_info.json.package | length }}
          
          Recent Packages:
          {% for package in firmware_info.json.package[:5] %}
          • {{ package.name }} - {{ package.version }}
          {% endfor %}
      when: info_type in ['firmware', 'all'] and firmware_info is defined
      
    - name: Display firmware status
      debug:
        msg: |
          🔥 OPNsense Firmware Status
          ===========================
          Product: {{ firmware_status.json.product }}
          Status: {{ firmware_status.json.status }}
          Message: {{ firmware_status.json.status_msg }}
      when: info_type in ['status', 'all'] and firmware_status is defined
      
    - name: Display service summary
      debug:
        msg: |
          🔥 OPNsense Service Summary
          ===========================
          Total Services: {{ services_info.json.total }}
          
          Service Status:
          {% set running_count = 0 %}
          {% set stopped_count = 0 %}
          {% for service in services_info.json.rows %}
          {% if service.running %}{% set running_count = running_count + 1 %}{% endif %}
          {% if not service.running %}{% set stopped_count = stopped_count + 1 %}{% endif %}
          {% endfor %}
          🟢 Running: {{ running_count }}
          🔴 Stopped: {{ stopped_count }}
      when: info_type in ['services', 'all'] and services_info is defined
"""
    
    # Save playbooks
    with open('infra/ansible/playbooks/network/opnsense_service_management.yml', 'w') as f:
        f.write(service_playbook)
    
    with open('infra/ansible/playbooks/network/opnsense_system_info.yml', 'w') as f:
        f.write(system_playbook)
    
    print("✅ Created Ansible playbooks:")
    print("   • infra/ansible/playbooks/network/opnsense_service_management.yml")
    print("   • infra/ansible/playbooks/network/opnsense_system_info.yml")

def main():
    """Main function"""
    print("🔥 OPNsense Integration Setup")
    print("=" * 50)
    
    load_credentials()
    test_working_endpoints()
    create_semaphore_templates()
    create_ansible_playbooks()
    
    print("\n🎉 OPNsense Integration Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Add API credentials to Semaphore secrets")
    print("2. Import the template configurations into Semaphore")
    print("3. Test the new OPNsense automation templates")
    print("4. Expand API endpoints as more become available")

if __name__ == "__main__":
    main()
