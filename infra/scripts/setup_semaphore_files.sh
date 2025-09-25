#!/bin/bash

# Setup Semaphore Files Script
# Copies playbooks and inventory files to the correct Semaphore directories

set -e

# Configuration
PROJECT_ROOT="/Users/mike.turner/APP_Projects/tk-proxmox"
SEMAPHORE_BASE="/tmp/semaphore/project_4"
PROJECT_ID="4"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Setting up Semaphore files...${NC}"

# Function to copy playbook to template directory
copy_playbook_to_template() {
    local template_id=$1
    local playbook_path=$2
    local template_dir="${SEMAPHORE_BASE}/repository_1_template_${template_id}"
    local target_dir="${template_dir}/playbooks/network"
    
    echo -e "${YELLOW}📁 Setting up template ${template_id}...${NC}"
    
    # Create directory structure
    mkdir -p "${target_dir}"
    
    # Copy playbook
    if [ -f "${PROJECT_ROOT}/${playbook_path}" ]; then
        cp "${PROJECT_ROOT}/${playbook_path}" "${target_dir}/"
        echo -e "${GREEN}  ✅ Copied ${playbook_path}${NC}"
    else
        echo -e "${RED}  ❌ Playbook not found: ${playbook_path}${NC}"
        return 1
    fi
}

# Function to copy inventory file
copy_inventory() {
    local inventory_path=$1
    local inventory_id=$2
    
    echo -e "${YELLOW}📋 Setting up inventory ${inventory_id}...${NC}"
    
    if [ -f "${PROJECT_ROOT}/${inventory_path}" ]; then
        cp "${PROJECT_ROOT}/${inventory_path}" "${SEMAPHORE_BASE}/inventory_${inventory_id}"
        echo -e "${GREEN}  ✅ Copied ${inventory_path}${NC}"
    else
        echo -e "${RED}  ❌ Inventory not found: ${inventory_path}${NC}"
        return 1
    fi
}

# Create base directory structure
mkdir -p "${SEMAPHORE_BASE}"

# Create git repository structure (Semaphore looks here for playbooks)
echo -e "${YELLOW}📁 Setting up git repository structure...${NC}"
mkdir -p "${SEMAPHORE_BASE}/../playbooks/network"
mkdir -p "${SEMAPHORE_BASE}/../inventories/prod"

# Copy inventory files
copy_inventory "infra/ansible/inventories/network_switches.yml" "7"
copy_inventory "infra/ansible/inventories/prod/hosts.yml" "7_prod"

# Copy playbooks for each template
copy_playbook_to_template "14" "infra/ansible/playbooks/network/switch_specific_vlan_assignment.yml"
copy_playbook_to_template "22" "infra/ansible/playbooks/network/list_switch_interfaces.yml"

# Copy playbooks to git repository structure (where Semaphore actually looks)
echo -e "${YELLOW}📁 Copying playbooks to git repository...${NC}"
if [ -f "${PROJECT_ROOT}/infra/ansible/playbooks/network/switch_specific_vlan_assignment.yml" ]; then
    cp "${PROJECT_ROOT}/infra/ansible/playbooks/network/switch_specific_vlan_assignment.yml" "${SEMAPHORE_BASE}/../playbooks/network/"
    echo -e "${GREEN}  ✅ Copied switch_specific_vlan_assignment.yml to git repo${NC}"
fi

if [ -f "${PROJECT_ROOT}/infra/ansible/playbooks/network/list_switch_interfaces.yml" ]; then
    cp "${PROJECT_ROOT}/infra/ansible/playbooks/network/list_switch_interfaces.yml" "${SEMAPHORE_BASE}/../playbooks/network/"
    echo -e "${GREEN}  ✅ Copied list_switch_interfaces.yml to git repo${NC}"
fi

# Copy inventories to git repository structure
echo -e "${YELLOW}📋 Copying inventories to git repository...${NC}"
if [ -f "${PROJECT_ROOT}/infra/ansible/inventories/network_switches.yml" ]; then
    cp "${PROJECT_ROOT}/infra/ansible/inventories/network_switches.yml" "${SEMAPHORE_BASE}/../inventories/"
    echo -e "${GREEN}  ✅ Copied network_switches.yml to git repo${NC}"
fi

if [ -f "${PROJECT_ROOT}/infra/ansible/inventories/prod/hosts.yml" ]; then
    cp "${PROJECT_ROOT}/infra/ansible/inventories/prod/hosts.yml" "${SEMAPHORE_BASE}/../inventories/prod/"
    echo -e "${GREEN}  ✅ Copied hosts.yml to git repo${NC}"
fi

echo -e "${GREEN}🎉 Semaphore files setup complete!${NC}"
echo -e "${BLUE}📋 Directory structure created:${NC}"
echo -e "  ${SEMAPHORE_BASE}/"
echo -e "  ├── inventory_7"
echo -e "  ├── inventory_7_prod"
echo -e "  ├── repository_1_template_14/playbooks/network/"
echo -e "  ├── repository_1_template_22/playbooks/network/"
echo -e "  └── ../ (Git Repository)"
echo -e "      ├── playbooks/network/"
echo -e "      │   ├── list_switch_interfaces.yml"
echo -e "      │   └── switch_specific_vlan_assignment.yml"
echo -e "      └── inventories/"
echo -e "          ├── network_switches.yml"
echo -e "          └── prod/hosts.yml"

echo -e "${YELLOW}💡 Templates ready for use:${NC}"
echo -e "  Template 14: Switch-Specific VLAN Assignment"
echo -e "  Template 22: List Switch Interfaces (with Survey)"

# Verify files exist
echo -e "${BLUE}🔍 Verifying files...${NC}"
for template_id in 14 22; do
    playbook_file="${SEMAPHORE_BASE}/repository_1_template_${template_id}/playbooks/network/"
    if [ -d "${playbook_file}" ]; then
        playbook_count=$(find "${playbook_file}" -name "*.yml" | wc -l)
        echo -e "${GREEN}  ✅ Template ${template_id}: ${playbook_count} playbook(s)${NC}"
    else
        echo -e "${RED}  ❌ Template ${template_id}: No playbooks found${NC}"
    fi
done

inventory_file="${SEMAPHORE_BASE}/inventory_7"
if [ -f "${inventory_file}" ]; then
    echo -e "${GREEN}  ✅ Inventory 7: Available${NC}"
else
    echo -e "${RED}  ❌ Inventory 7: Not found${NC}"
fi

echo -e "${GREEN}✅ Setup verification complete!${NC}"
