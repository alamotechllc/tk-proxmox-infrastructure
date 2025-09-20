#!/usr/bin/env python3
"""
Common configuration helper for test scripts
"""
import os
import sys
from pathlib import Path

def setup_test_environment():
    """Set up test environment configuration paths"""
    
    # Get current script directory
    current_dir = Path(__file__).parent
    
    # Calculate project root directory
    project_root = current_dir.parent
    
    # Set configuration file path
    config_path = project_root / "proxmox-config" / "config.json"
    
    # Set source code path
    src_path = project_root / "src"
    
    # Ensure paths exist
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file does not exist: {config_path}")
    
    if not src_path.exists():
        raise FileNotFoundError(f"Source code directory does not exist: {src_path}")
    
    # Set environment variables
    os.environ['PROXMOX_MCP_CONFIG'] = str(config_path)
    
    # Add source code path to Python path
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    return str(config_path)

def get_test_tools():
    """Get test tools classes"""
    
    # Ensure environment is set up
    config_path = setup_test_environment()
    
    try:
        from proxmox_mcp.config.loader import load_config
        from proxmox_mcp.core.proxmox import ProxmoxManager
        from proxmox_mcp.tools.vm import VMTools
        
        config = load_config(config_path)
        manager = ProxmoxManager(config.proxmox, config.auth)
        api = manager.get_api()
        
        vm_tools = VMTools(api)
        
        return {
            'config': config,
            'manager': manager,
            'api': api,
            'vm_tools': vm_tools
        }
        
    except Exception as e:
        print(f"❌ Failed to initialize test tools: {e}")
        raise

def print_test_header(title):
    """Print test title"""
    print(f"🔍 {title}")
    print("=" * len(f"🔍 {title}"))

def print_test_result(success, message=""):
    """Print test result"""
    if success:
        print(f"\n✅ Test completed {message}")
    else:
        print(f"\n❌ Test failed {message}")
        sys.exit(1) 