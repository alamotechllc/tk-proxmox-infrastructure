#!/usr/bin/env python3
"""Test Semaphore authentication"""

import requests
from urllib.parse import urljoin

base_url = "http://172.23.5.22:3000"
api_url = f"{base_url}/api"
auth_url = f"{api_url}/auth/login"

print(f"Base URL: {base_url}")
print(f"API URL: {api_url}")
print(f"Auth URL: {auth_url}")

# Test with session
session = requests.Session()
response = session.post(auth_url, json={"auth": "admin", "password": "8fewWER8382"})

print(f"\nStatus Code: {response.status_code}")
print(f"Response Content: '{response.text}'")
print(f"Response Headers: {dict(response.headers)}")
print(f"Cookies: {dict(response.cookies)}")
print(f"Session Cookies: {dict(session.cookies)}")

# Test API call with session
if response.status_code == 204:
    print("\n✅ Authentication successful!")
    
    # Test getting projects
    projects_url = urljoin(api_url, "projects")
    print(f"Projects URL: {projects_url}")
    
    projects_response = session.get(projects_url)
    print(f"Projects Status: {projects_response.status_code}")
    print(f"Projects Content: {projects_response.text}")
else:
    print("\n❌ Authentication failed!")
