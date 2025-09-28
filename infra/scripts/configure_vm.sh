#!/usr/bin/env bash
#
# VM Configuration Helper Script
# Run this inside the ansible-control VM to prepare it for Semaphore deployment
#

set -euo pipefail

echo "=========================================="
echo "Configuring ansible-control VM"
echo "=========================================="

# Update system
echo "1. Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo "2. Installing essential packages..."
sudo apt install -y \
    openssh-server \
    curl \
    wget \
    git \
    htop \
    net-tools \
    qemu-guest-agent

# Enable and start SSH
echo "3. Configuring SSH..."
sudo systemctl enable ssh
sudo systemctl start ssh

# Enable and start QEMU guest agent
echo "4. Configuring QEMU guest agent..."
sudo systemctl enable qemu-guest-agent
sudo systemctl start qemu-guest-agent

# Create ubuntu user if it doesn't exist
echo "5. Configuring user account..."
if ! id "ubuntu" &>/dev/null; then
    sudo adduser --disabled-password --gecos "" ubuntu
    sudo usermod -aG sudo ubuntu
    echo "ubuntu ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/ubuntu
fi

# Set up SSH directory for ubuntu user
sudo mkdir -p /home/ubuntu/.ssh
sudo chown ubuntu:ubuntu /home/ubuntu/.ssh
sudo chmod 700 /home/ubuntu/.ssh

# Display network information
echo "6. Network configuration:"
echo "----------------------------------------"
ip addr show | grep -E "(inet|UP|DOWN)"
echo "----------------------------------------"

echo ""
echo "VM Configuration Complete!"
echo ""
echo "Next steps:"
echo "1. Copy your SSH public key to /home/ubuntu/.ssh/authorized_keys"
echo "2. Note the IP address shown above"
echo "3. Update the Ansible inventory with the correct IP"
echo "4. Run the Semaphore deployment script"
echo ""
echo "To copy SSH key from your workstation:"
echo "ssh-copy-id ubuntu@<VM_IP_ADDRESS>"
echo ""
echo "=========================================="
