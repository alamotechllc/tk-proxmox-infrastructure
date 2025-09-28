#!/bin/bash

# Semaphore File Monitor Script
# Checks if required files exist and restores them if missing

set -e

# Configuration
PROJECT_ROOT="/Users/mike.turner/APP_Projects/tk-proxmox"
SEMAPHORE_BASE="/tmp/semaphore"
REQUIRED_FILES=(
    "playbooks/network/list_switch_interfaces.yml"
    "playbooks/network/switch_specific_vlan_assignment.yml"
    "inventories/network_switches.yml"
    "inventories/prod/hosts.yml"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Monitoring Semaphore files...${NC}"

# Check if files exist
missing_files=()
for file in "${REQUIRED_FILES[@]}"; do
    full_path="${SEMAPHORE_BASE}/${file}"
    if [ ! -f "${full_path}" ]; then
        missing_files+=("${file}")
        echo -e "${RED}  ❌ Missing: ${file}${NC}"
    else
        echo -e "${GREEN}  ✅ Found: ${file}${NC}"
    fi
done

# If files are missing, restore them
if [ ${#missing_files[@]} -gt 0 ]; then
    echo -e "${YELLOW}📁 ${#missing_files[@]} files missing, restoring...${NC}"
    
    # Run the setup script to restore all files
    cd "${PROJECT_ROOT}"
    ./infra/scripts/setup_semaphore_files.sh
    
    echo -e "${GREEN}✅ Files restored successfully!${NC}"
else
    echo -e "${GREEN}✅ All files present, no action needed.${NC}"
fi

# Verify restoration
echo -e "${BLUE}🔍 Verifying restoration...${NC}"
all_good=true
for file in "${REQUIRED_FILES[@]}"; do
    full_path="${SEMAPHORE_BASE}/${file}"
    if [ -f "${full_path}" ]; then
        size=$(stat -f%z "${full_path}" 2>/dev/null || echo "unknown")
        echo -e "${GREEN}  ✅ ${file} (${size} bytes)${NC}"
    else
        echo -e "${RED}  ❌ ${file} - Still missing!${NC}"
        all_good=false
    fi
done

if [ "$all_good" = true ]; then
    echo -e "${GREEN}🎉 All Semaphore files are in place!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some files are still missing after restoration attempt.${NC}"
    exit 1
fi
