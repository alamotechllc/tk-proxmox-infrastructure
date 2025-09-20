#!/usr/bin/env python3
"""
Test Proxmox VM power management functionality
"""
import sys
from test_common import setup_test_environment, get_test_tools, print_test_header, print_test_result

def test_vm_power_operations():
    """Test VM power management operations"""
    
    try:
        # Set up test environment
        setup_test_environment()
        tools = get_test_tools()
        
        api = tools['api']
        nodes = api.nodes.get()
        
        # Safely get the first node to avoid index out of range error
        if not nodes or len(nodes) == 0:
            print("❌ No Proxmox nodes found")
            return False
            
        node_name = nodes[0]['node']
        
        print(f"Test node: {node_name}")
        
        # Get all VMs
        vms = api.nodes(node_name).qemu.get()
        print(f"Found {len(vms)} virtual machines:")
        
        vm_101_found = False
        for vm in vms:
            vmid = vm['vmid']
            name = vm['name']
            status = vm['status']
            print(f"  - VM {vmid}: {name} ({status})")
            
            if vmid == 101:
                vm_101_found = True
                print(f"\nFound VPN-Server (ID: 101), current status: {status}")
                
                # Test available status operations
                vm_api = api.nodes(node_name).qemu(vmid)
                status_api = vm_api.status
                
                print("Test available status operations:")
                
                # Try accessing different status endpoints
                try:
                    # Check if start endpoint exists
                    if hasattr(status_api, 'start'):
                        print("  ✅ Supports start operation")
                    else:
                        print("  ❌ Does not support start operation")
                        
                    if hasattr(status_api, 'stop'):
                        print("  ✅ Supports stop operation")
                    else:
                        print("  ❌ Does not support stop operation")
                        
                    if hasattr(status_api, 'reset'):
                        print("  ✅ Supports reset operation")
                    else:
                        print("  ❌ Does not support reset operation")
                        
                    if hasattr(status_api, 'shutdown'):
                        print("  ✅ Supports shutdown operation")
                    else:
                        print("  ❌ Does not support shutdown operation")
                        
                    # If VM is stopped, try to start
                    if status == 'stopped':
                        print(f"\nVM {vmid} is currently stopped, can try to start")
                        print("Start command would be: api.nodes(node).qemu(101).status.start.post()")
                        
                    elif status == 'running':
                        print(f"\nVM {vmid} is currently running")
                        
                except Exception as e:
                    print(f"  Error while testing operations: {e}")
        
        if not vm_101_found:
            print("\n❌ VM 101 (VPN-Server) not found")
            
    except Exception as e:
        print(f"Test failed: {e}")
        return False
        
    return True

if __name__ == "__main__":
    print_test_header("Test Proxmox VM power management functionality")
    
    success = test_vm_power_operations()
    print_test_result(success) 