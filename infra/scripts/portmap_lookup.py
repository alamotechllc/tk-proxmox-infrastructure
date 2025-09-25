#!/usr/bin/env python3
"""
TK Network Port Mapping Lookup Tool
Quick reference for network port assignments and device locations
"""

import argparse
import json
from typing import Dict, List, Optional

# Network topology data based on diagram
NETWORK_TOPOLOGY = {
    "devices": {
        "tks-fw-opnsense-1": {
            "ip": "172.23.7.1",
            "type": "firewall",
            "model": "OPNsense HA Firewall",
            "interfaces": {
                "WAN": {"vlan": None, "network": "Internet", "description": "ISP connection"},
                "LAN": {"vlan": 7, "network": "172.23.7.0/24", "description": "Management network"},
                "OPT1": {"vlan": 2, "network": "172.23.2.0/24", "description": "Server infrastructure"},
                "OPT2": {"vlan": 3, "network": "172.23.3.0/24", "description": "User workstations"},
                "OPT3": {"vlan": 4, "network": "172.23.4.0/24", "description": "Guest network"},
                "OPT4": {"vlan": 5, "network": "172.23.5.0/24", "description": "IoT devices"},
                "OPT5": {"vlan": 6, "network": "172.23.6.0/24", "description": "Gaming & entertainment"}
            }
        },
        "tks-sw-arista-core-1": {
            "ip": "172.23.7.10",
            "type": "core_switch",
            "model": "DCS-7050T-64",
            "port_channels": {
                "Po1": {"destination": "Cisco Nexus", "vlans": "2-7", "type": "trunk"},
                "Po2": {"destination": "OPNsense", "vlans": "2-7", "type": "trunk"}
            },
            "protected_ports": ["Ethernet49/1", "Ethernet50/1", "Management1"],
            "high_speed_ports": {
                "40GbE": ["TSKI-Server", "TrueNAS Personal"],
                "10GbE": ["Game Server", "Intel Proxmox", "8x10gbe Node Server"]
            }
        },
        "tks-sw-cis-nexus-1": {
            "ip": "210.141.77.15",
            "type": "access_switch",
            "model": "Cisco Nexus NX-OS 9.3(8)",
            "management": {"vlan": 99, "vrf": "192.6.15.1"},
            "trunk_ports": {
                "Ethernet1/50": {"destination": "Proxmox", "vlans": "2-7"},
                "Ethernet1/52": {"destination": "TrueNAS", "vlans": "2-7"}
            },
            "port_channels": {
                "port-channel1": {"destination": "Arista Po1", "type": "LAG"}
            },
            "access_ports": {
                "Ethernet1/18-46": {"vlan": 6, "description": "Gaming/Entertainment"}
            }
        }
    },
    "vlans": {
        2: {"name": "SERVERS", "network": "172.23.2.0/24", "gateway": "172.23.2.1"},
        3: {"name": "WORKSTATIONS", "network": "172.23.3.0/24", "gateway": "172.23.3.1"},
        4: {"name": "GUEST", "network": "172.23.4.0/24", "gateway": "172.23.4.1"},
        5: {"name": "IOT", "network": "172.23.5.0/24", "gateway": "172.23.5.1"},
        6: {"name": "GAMING", "network": "172.23.6.0/24", "gateway": "172.23.6.1"},
        7: {"name": "MANAGEMENT", "network": "172.23.7.0/24", "gateway": "172.23.7.1"}
    },
    "access_switches": {
        "office-8port": {
            "location": "Office",
            "uplink": "Arista Ethernet1/X",
            "ports": {
                1: {"device": "Desktop Main Backup", "vlan": 3, "ip": "172.23.3.11"},
                2: {"device": "Mac Studio", "vlan": 3, "ip": "172.23.3.10"},
                3: {"device": "Office Comms", "vlan": 3, "ip": "172.23.3.20"},
                4: {"device": "Office AP", "vlan": 5, "ip": "172.23.5.50"},
                5: {"device": "Xbox", "vlan": 6, "ip": "172.23.6.11"},
                6: {"device": "Switch Console", "vlan": 6, "ip": "172.23.6.13"},
                7: {"device": "Available", "vlan": None, "ip": None},
                8: {"device": "Uplink to Arista", "vlan": "Trunk", "ip": None}
            }
        },
        "living-8port": {
            "location": "Living Room",
            "uplink": "Arista Ethernet1/Y",
            "ports": {
                1: {"device": "PlayStation", "vlan": 6, "ip": "172.23.6.10"},
                2: {"device": "Xbox", "vlan": 6, "ip": "172.23.6.11"},
                3: {"device": "Switch Console", "vlan": 6, "ip": "172.23.6.13"},
                4: {"device": "Audio Receiver", "vlan": 6, "ip": "172.23.6.20"},
                5: {"device": "Steam Link", "vlan": 6, "ip": "172.23.6.12"},
                6: {"device": "Available", "vlan": None, "ip": None},
                7: {"device": "Available", "vlan": None, "ip": None},
                8: {"device": "Uplink to Arista", "vlan": "Trunk", "ip": None}
            }
        },
        "poe-10port": {
            "location": "Infrastructure",
            "uplink": "Arista Ethernet1/Z",
            "ports": {
                1: {"device": "Garage Camera", "vlan": 5, "ip": "172.23.5.80", "poe": True},
                2: {"device": "Side Camera", "vlan": 5, "ip": "172.23.5.81", "poe": True},
                3: {"device": "Downstairs AP", "vlan": 5, "ip": "172.23.5.51", "poe": True},
                4: {"device": "Upstairs AP", "vlan": 5, "ip": "172.23.5.52", "poe": True},
                5: {"device": "SmartThings Hub", "vlan": 5, "ip": "172.23.5.70", "poe": True},
                6: {"device": "Smart Panels", "vlan": 5, "ip": "172.23.5.71", "poe": True},
                7: {"device": "PoE Light Switches", "vlan": 5, "ip": "172.23.5.72", "poe": True},
                8: {"device": "Garage Doors", "vlan": 5, "ip": "172.23.5.73", "poe": True},
                9: {"device": "Available", "vlan": 5, "ip": None, "poe": True},
                10: {"device": "Uplink to Arista", "vlan": "Trunk", "ip": None, "poe": False}
            }
        }
    }
}

def lookup_device(device_name: str) -> Optional[Dict]:
    """Find a device by name across all switches"""
    results = []
    
    # Search in access switches
    for switch_name, switch_data in NETWORK_TOPOLOGY["access_switches"].items():
        for port_num, port_data in switch_data["ports"].items():
            if device_name.lower() in port_data["device"].lower():
                results.append({
                    "switch": switch_name,
                    "location": switch_data["location"],
                    "port": port_num,
                    "device": port_data["device"],
                    "vlan": port_data["vlan"],
                    "ip": port_data["ip"],
                    "poe": port_data.get("poe", False)
                })
    
    return results

def lookup_vlan(vlan_id: int) -> Optional[Dict]:
    """Get VLAN information"""
    return NETWORK_TOPOLOGY["vlans"].get(vlan_id)

def lookup_switch(switch_name: str) -> Optional[Dict]:
    """Get switch information"""
    return NETWORK_TOPOLOGY["devices"].get(switch_name)

def show_port_map(switch_name: str = None):
    """Show port mapping for a specific switch or all switches"""
    if switch_name:
        switch_data = NETWORK_TOPOLOGY["access_switches"].get(switch_name)
        if switch_data:
            print(f"📍 {switch_data['location']} Switch ({switch_name}):")
            print(f"   Uplink: {switch_data['uplink']}")
            print("   Port Assignments:")
            
            for port_num, port_data in switch_data["ports"].items():
                device = port_data["device"]
                vlan = port_data["vlan"]
                ip = port_data["ip"] or "N/A"
                poe = " (PoE)" if port_data.get("poe") else ""
                
                print(f"   {port_num:2}: {device:<20} VLAN {vlan} {ip}{poe}")
        else:
            print(f"❌ Switch '{switch_name}' not found")
    else:
        for switch_name in NETWORK_TOPOLOGY["access_switches"]:
            show_port_map(switch_name)
            print()

def show_vlan_summary():
    """Show VLAN assignments and networks"""
    print("📡 VLAN Summary:")
    for vlan_id, vlan_data in NETWORK_TOPOLOGY["vlans"].items():
        print(f"   VLAN {vlan_id}: {vlan_data['name']}")
        print(f"      Network: {vlan_data['network']}")
        print(f"      Gateway: {vlan_data['gateway']}")
        print()

def show_device_summary():
    """Show all network devices"""
    print("🌐 Network Device Summary:")
    for device_name, device_data in NETWORK_TOPOLOGY["devices"].items():
        print(f"   • {device_name}")
        print(f"     IP: {device_data['ip']}")
        print(f"     Type: {device_data['type']}")
        print(f"     Model: {device_data['model']}")
        print()

def main():
    parser = argparse.ArgumentParser(description="TK Network Port Mapping Lookup Tool")
    parser.add_argument('--device', '-d', help='Look up device by name')
    parser.add_argument('--vlan', '-v', type=int, help='Look up VLAN information')
    parser.add_argument('--switch', '-s', help='Show port map for specific switch')
    parser.add_argument('--all-ports', '-p', action='store_true', help='Show all port mappings')
    parser.add_argument('--vlans', action='store_true', help='Show VLAN summary')
    parser.add_argument('--devices', action='store_true', help='Show device summary')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    args = parser.parse_args()
    
    if args.json:
        print(json.dumps(NETWORK_TOPOLOGY, indent=2))
        return
    
    print("🔍 TK Network Port Mapping Lookup")
    print("=" * 40)
    print()
    
    if args.device:
        results = lookup_device(args.device)
        if results:
            print(f"📍 Found '{args.device}' in {len(results)} location(s):")
            for result in results:
                poe_info = " (PoE)" if result["poe"] else ""
                print(f"   • {result['switch']} ({result['location']})")
                print(f"     Port {result['port']}: {result['device']}")
                print(f"     VLAN {result['vlan']}, IP: {result['ip']}{poe_info}")
        else:
            print(f"❌ Device '{args.device}' not found in port mappings")
    
    elif args.vlan:
        vlan_info = lookup_vlan(args.vlan)
        if vlan_info:
            print(f"📡 VLAN {args.vlan} Information:")
            print(f"   Name: {vlan_info['name']}")
            print(f"   Network: {vlan_info['network']}")
            print(f"   Gateway: {vlan_info['gateway']}")
        else:
            print(f"❌ VLAN {args.vlan} not found")
    
    elif args.switch:
        show_port_map(args.switch)
    
    elif args.all_ports:
        show_port_map()
    
    elif args.vlans:
        show_vlan_summary()
    
    elif args.devices:
        show_device_summary()
    
    else:
        print("Available commands:")
        print("  --device NAME     Look up device location")
        print("  --vlan ID         Show VLAN information") 
        print("  --switch NAME     Show switch port map")
        print("  --all-ports       Show all port mappings")
        print("  --vlans           Show VLAN summary")
        print("  --devices         Show device summary")
        print("  --json            Output raw data in JSON")
        print()
        print("Examples:")
        print("  python3 portmap_lookup.py --device xbox")
        print("  python3 portmap_lookup.py --vlan 6")
        print("  python3 portmap_lookup.py --switch office-8port")
        print("  python3 portmap_lookup.py --all-ports")

if __name__ == "__main__":
    main()
