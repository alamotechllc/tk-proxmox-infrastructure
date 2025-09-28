#!/usr/bin/env python3
"""
Semaphore GitHub Integration Verification Script

This script verifies that Semaphore is properly configured to access
the GitHub repository using SSH keys.

Usage:
    python3 verify_semaphore_github_integration.py

Requirements:
    - Semaphore API access
    - Python requests library
    - Valid Semaphore credentials
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
SEMAPHORE_URL = 'http://172.23.5.22:3000'
API_URL = f'{SEMAPHORE_URL}/api'
PROJECT_ID = 4
REPOSITORY_ID = 1
GITHUB_REPO_URL = 'https://github.com/alamotechllc/tk-proxmox-infrastructure.git'

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    """Print script header"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("  SEMAPHORE GITHUB INTEGRATION VERIFICATION")
    print("=" * 60)
    print(f"{Colors.END}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Semaphore URL: {SEMAPHORE_URL}")
    print(f"GitHub Repository: {GITHUB_REPO_URL}")
    print()

def authenticate():
    """Authenticate with Semaphore API"""
    print(f"{Colors.YELLOW}🔐 Authenticating with Semaphore...{Colors.END}")
    
    session = requests.Session()
    auth_data = {'auth': 'admin', 'password': '8fewWER8382'}
    
    try:
        response = session.post(f'{API_URL}/auth/login', json=auth_data)
        if response.status_code == 200:
            print(f"{Colors.GREEN}✅ Authentication successful{Colors.END}")
            return session
        else:
            print(f"{Colors.RED}❌ Authentication failed: {response.status_code}{Colors.END}")
            return None
    except Exception as e:
        print(f"{Colors.RED}❌ Authentication error: {e}{Colors.END}")
        return None

def check_repository_config(session):
    """Check repository configuration"""
    print(f"\n{Colors.YELLOW}📋 Checking repository configuration...{Colors.END}")
    
    try:
        response = session.get(f'{API_URL}/project/{PROJECT_ID}/repositories/{REPOSITORY_ID}')
        if response.status_code == 200:
            repo = response.json()
            
            print(f"{Colors.GREEN}✅ Repository found:{Colors.END}")
            print(f"   Name: {repo['name']}")
            print(f"   Git URL: {repo['git_url']}")
            print(f"   Branch: {repo['git_branch']}")
            print(f"   SSH Key ID: {repo.get('ssh_key_id', 'None')}")
            
            # Check if using GitHub repository
            if 'github.com' in repo['git_url']:
                print(f"{Colors.GREEN}✅ GitHub repository configured{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}❌ Not using GitHub repository{Colors.END}")
                return False
        else:
            print(f"{Colors.RED}❌ Repository check failed: {response.status_code}{Colors.END}")
            return False
            
    except Exception as e:
        print(f"{Colors.RED}❌ Repository check error: {e}{Colors.END}")
        return False

def check_ssh_keys(session):
    """Check available SSH keys"""
    print(f"\n{Colors.YELLOW}🔑 Checking SSH keys...{Colors.END}")
    
    try:
        response = session.get(f'{API_URL}/project/{PROJECT_ID}/keys')
        if response.status_code == 200:
            keys = response.json()
            
            print(f"{Colors.GREEN}✅ SSH Keys found: {len(keys)}{Colors.END}")
            github_keys = []
            
            for key in keys:
                print(f"   ID {key['id']}: {key['name']} ({key['type']})")
                if 'github' in key['name'].lower() or 'repository' in key['name'].lower():
                    github_keys.append(key)
            
            if github_keys:
                print(f"{Colors.GREEN}✅ GitHub-related SSH keys found: {len(github_keys)}{Colors.END}")
                return True
            else:
                print(f"{Colors.YELLOW}⚠️  No GitHub-specific SSH keys found{Colors.END}")
                return False
        else:
            print(f"{Colors.RED}❌ SSH keys check failed: {response.status_code}{Colors.END}")
            return False
            
    except Exception as e:
        print(f"{Colors.RED}❌ SSH keys check error: {e}{Colors.END}")
        return False

def check_templates(session):
    """Check available templates"""
    print(f"\n{Colors.YELLOW}📄 Checking templates...{Colors.END}")
    
    try:
        response = session.get(f'{API_URL}/project/{PROJECT_ID}/templates')
        if response.status_code == 200:
            templates = response.json()
            
            print(f"{Colors.GREEN}✅ Templates found: {len(templates)}{Colors.END}")
            
            # Look for our specific templates
            vlan_template = None
            interface_template = None
            
            for template in templates:
                name = template['name'].lower()
                if 'vlan' in name and 'assignment' in name:
                    vlan_template = template
                elif 'interface' in name and 'list' in name:
                    interface_template = template
                
                print(f"   ID {template['id']}: {template['name']}")
            
            if vlan_template and interface_template:
                print(f"{Colors.GREEN}✅ Required templates found:{Colors.END}")
                print(f"   VLAN Assignment: ID {vlan_template['id']}")
                print(f"   Interface Listing: ID {interface_template['id']}")
                return True
            else:
                print(f"{Colors.YELLOW}⚠️  Some required templates not found{Colors.END}")
                return False
        else:
            print(f"{Colors.RED}❌ Templates check failed: {response.status_code}{Colors.END}")
            return False
            
    except Exception as e:
        print(f"{Colors.RED}❌ Templates check error: {e}{Colors.END}")
        return False

def test_template_execution(session):
    """Test template execution (dry run)"""
    print(f"\n{Colors.YELLOW}🧪 Testing template execution...{Colors.END}")
    
    try:
        # Try to run the interface listing template
        template_data = {
            'template_id': 22,  # Interface listing template
            'dry_run': True,
            'extra_vars': {
                'switch_name': 'tks-sw-arista-core-1'
            }
        }
        
        response = session.post(f'{API_URL}/project/{PROJECT_ID}/tasks', json=template_data)
        if response.status_code == 200:
            task = response.json()
            print(f"{Colors.GREEN}✅ Template execution test successful{Colors.END}")
            print(f"   Task ID: {task.get('id', 'Unknown')}")
            return True
        else:
            print(f"{Colors.RED}❌ Template execution test failed: {response.status_code}{Colors.END}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"{Colors.RED}❌ Template execution test error: {e}{Colors.END}")
        return False

def print_summary(results):
    """Print verification summary"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("  VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"{Colors.END}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print()
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if result else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"{test_name}: {status}")
    
    print()
    if passed_tests == total_tests:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! GitHub integration is working correctly.{Colors.END}")
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  Some tests failed. Check the setup and try again.{Colors.END}")
    
    print(f"\n{Colors.BLUE}Next steps:{Colors.END}")
    if passed_tests == total_tests:
        print("   • Templates are ready for use")
        print("   • GitHub integration is working")
        print("   • You can now run VLAN assignment and interface listing tasks")
    else:
        print("   • Complete SSH key setup")
        print("   • Verify GitHub deploy key configuration")
        print("   • Check Semaphore repository settings")
        print("   • Re-run this verification script")

def main():
    """Main verification function"""
    print_header()
    
    # Authenticate
    session = authenticate()
    if not session:
        print(f"{Colors.RED}❌ Cannot proceed without authentication{Colors.END}")
        sys.exit(1)
    
    # Run verification tests
    results = {}
    
    results['Repository Configuration'] = check_repository_config(session)
    results['SSH Keys'] = check_ssh_keys(session)
    results['Templates'] = check_templates(session)
    results['Template Execution'] = test_template_execution(session)
    
    # Print summary
    print_summary(results)
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
