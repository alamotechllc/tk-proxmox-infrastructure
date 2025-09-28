#!/usr/bin/env python3
"""
Test VM startup functionality
"""
import os
import sys

def test_start_vm_101():
    """Test starting VM 101 (VPN-Server)"""
    
    # Set configuration
    os.environ['PROXMOX_MCP_CONFIG'] = 'proxmox-config/config.json'
    
    try:
        from proxmox_mcp.config.loader import load_config
        from proxmox_mcp.core.proxmox import ProxmoxManager
        from proxmox_mcp.tools.vm import VMTools
        
        config = load_config('proxmox-config/config.json')
        manager = ProxmoxManager(config.proxmox, config.auth)
        api = manager.get_api()
        
        vm_tools = VMTools(api)
        
        print("🚀 Test starting VPN-Server (VM 101)")
        print("=" * 50)
        
        # Start VM 101
        result = vm_tools.start_vm(node="pve", vmid="101")
        
        for content in result:
            print(content.text)
            
        return True
        
    except Exception as e:
        print(f"❌ Start failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Test VM startup functionality")
    print("=" * 50)
    
    success = test_start_vm_101()
    
    if success:
        print("\n✅ Test completed")
    else:
        print("\n❌ Test failed")
        sys.exit(1) 