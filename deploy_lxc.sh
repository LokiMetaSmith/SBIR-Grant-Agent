#!/bin/bash

# ==============================================================================
# Proxmox Deployment Script for SBIR Grant Agent
# ==============================================================================
#
# This script automates the creation and configuration of a Debian-based LXC
# container on Proxmox VE to run the SBIR Grant Agent application.
#
# Usage:
# 1. Make the script executable: chmod +x deploy_lxc.sh
# 2. Run the script on your Proxmox host: ./deploy_lxc.sh
#
# ==============================================================================

# --- Configuration ---
# Feel free to change these values to match your Proxmox setup.

# LXC Container Settings
CT_ID="199"                           # Container ID. Make sure it's not already in use.
CT_HOSTNAME="sbir-agent"              # Desired hostname for the container.
CT_PASSWORD="Password123"             # Root password for the container. Change this!
CT_CORES="1"                          # Number of CPU cores.
CT_MEMORY="1024"                      # RAM in MB.
CT_SWAP="512"                         # Swap in MB.
CT_DISK_SIZE="8G"                     # Disk size (e.g., 8G).

# Proxmox Host Settings
PROXMOX_STORAGE="local-lvm"           # Storage pool for the new container's disk.
PROXMOX_BRIDGE="vmbr0"                # Network bridge for the container.

# LXC Template Settings
# The script will try to find a recent Debian or Ubuntu template.
# Update this if you have a specific template you want to use.
TEMPLATE_STORAGE="local"              # Storage where your LXC templates are located.
TEMPLATE_NAME=$(pveam available --section system | grep -E 'debian-12|ubuntu-24' | grep 'standard' | awk '{print $2}' | sort -r | head -n 1)

# Application Settings
APP_DIR="/opt/sbir-agent"
APP_USER="appuser"

# --- Color Codes for Output ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- Script Functions ---

# Function to print a formatted message
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Function to print a warning message
warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to print an error message and exit
error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# --- Pre-flight Checks ---
log "Starting pre-flight checks..."

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    error "This script must be run as root. Please use 'sudo ./deploy_lxc.sh'."
fi

# Check for required Proxmox commands
if ! command_exists pct || ! command_exists pveam; then
    error "This script requires 'pct' and 'pveam' commands. Please run it on a Proxmox VE host."
fi

# Check if the chosen CT ID already exists
if pct status "$CT_ID" > /dev/null 2>&1; then
    error "Container with ID $CT_ID already exists. Please choose a different CT_ID."
fi

# Check for template
if [ -z "$TEMPLATE_NAME" ]; then
    error "Could not find a suitable Debian or Ubuntu template. Please download one via the Proxmox UI (local -> CT Templates)."
fi
log "Found template: $TEMPLATE_NAME"

# Download the template if it's not already available
if ! pveam list "$TEMPLATE_STORAGE" | grep -q "$TEMPLATE_NAME"; then
    log "Template not found locally. Downloading..."
    pveam download "$TEMPLATE_STORAGE" "$TEMPLATE_NAME" || error "Failed to download template."
fi

# --- Container Creation ---
log "Creating LXC container with ID $CT_ID..."

pct create "$CT_ID" "$TEMPLATE_STORAGE:vztmpl/$TEMPLATE_NAME" \
    --hostname "$CT_HOSTNAME" \
    --password "$CT_PASSWORD" \
    --cores "$CT_CORES" \
    --memory "$CT_MEMORY" \
    --swap "$CT_SWAP" \
    --rootfs "$PROXMOX_STORAGE:$CT_DISK_SIZE" \
    --net0 name=eth0,bridge="$PROXMOX_BRIDGE",ip=dhcp \
    --onboot 1 \
    --features nesting=1 \
    --unprivileged 1 || error "Failed to create LXC container."

log "Container created successfully."

# --- Container Configuration ---
log "Starting and configuring the container..."
pct start "$CT_ID" || error "Failed to start the container."

# Wait for the network to be up
log "Waiting for network to become available..."
sleep 15

# Get the IP address
IP_ADDRESS=$(pct exec "$CT_ID" -- ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
if [ -z "$IP_ADDRESS" ]; then
    warn "Could not determine container IP address automatically. Continuing with setup."
else
    log "Container IP Address: $IP_ADDRESS"
fi

# --- Tar and Push Application Source ---
log "Archiving local project files..."
# Create a tarball of the current directory, excluding files not needed for deployment.
# This makes the script self-contained and removes the need for a git repo.
tar --exclude='./venv' \
    --exclude='./.git' \
    --exclude='*.png' \
    --exclude='*.log' \
    --exclude='deploy_lxc.sh' \
    --exclude='PROXMOX_DEPLOY.md' \
    -czf /tmp/sbir-agent-source.tar.gz . || error "Failed to create source archive."

log "Pushing source code to the container..."
pct push "$CT_ID" /tmp/sbir-agent-source.tar.gz /root/sbir-agent-source.tar.gz || error "Failed to push source archive to container."
rm /tmp/sbir-agent-source.tar.gz # Clean up the archive on the host


# --- Run Setup Script Inside Container ---
log "Running setup script inside the container. This may take a few minutes..."
# Using a here-document to execute a setup script directly inside the container.
pct exec "$CT_ID" -- bash -c '
export DEBIAN_FRONTEND=noninteractive

# Update and install dependencies
apt-get update
apt-get install -y python3 python3-pip python3-venv curl

# Create a non-root user for the application
useradd -m -s /bin/bash "'"$APP_USER"'"

# Create app directory and extract source code
mkdir -p "'"$APP_DIR"'"
tar -xzf /root/sbir-agent-source.tar.gz -C "'"$APP_DIR"'"
rm /root/sbir-agent-source.tar.gz
chown -R "'"$APP_USER"'":"'"$APP_USER"'" "'"$APP_DIR"'"

# Switch to the app user to set up the virtual environment and dependencies
su - "'"$APP_USER"'" -c "
cd "'"$APP_DIR"'"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
"

# Create systemd service file
cat > /etc/systemd/system/sbir-agent.service <<EOSERVICE
[Unit]
Description=SBIR Grant Agent Flask Server
After=network.target

[Service]
User='"$APP_USER"'
Group='"$APP_USER"'
WorkingDirectory='"$APP_DIR"'
ExecStart='"$APP_DIR"'/venv/bin/python3 server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOSERVICE

# Enable and start the service
systemctl daemon-reload
systemctl enable sbir-agent.service
systemctl start sbir-agent.service
' || error "Setup script execution failed."

# --- Finalization ---
log "Setup complete!"
echo -e "\n${GREEN}=======================================================================${NC}"
echo -e "${GREEN} SBIR Grant Agent is now running in LXC container ${YELLOW}$CT_ID ($CT_HOSTNAME)${GREEN}.${NC}"
if [ ! -z "$IP_ADDRESS" ]; then
    echo -e "${GREEN} Application URL: ${YELLOW}http://$IP_ADDRESS:5000/sbir_agent.html${NC}"
fi
echo -e "\n${YELLOW}IMPORTANT NEXT STEPS:${NC}"
echo -e "1. SSH into your Proxmox host."
echo -e "2. Enter the container console: ${YELLOW}pct enter $CT_ID${NC}"
echo -e "3. Edit the environment file with your API keys: ${YELLOW}nano $APP_DIR/.env${NC}"
echo -e "4. Restart the service for the new keys to take effect: ${YELLOW}systemctl restart sbir-agent${NC}"
echo -e "${GREEN}=======================================================================${NC}\n"

exit 0