#!/bin/bash

# Deploy Harbor Boat Client to Raspberry Pi
# Usage: ./deploy_boat.sh [pi_host] [pi_user]

set -e

# Configuration
PI_HOST="${1:-harbor}"
PI_USER="${2:-ys}"
PI_PORT="22"
REMOTE_DIR="/home/$PI_USER/harbor"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚤 Deploying Harbor Boat Client to Pi...${NC}"
echo -e "${YELLOW}Pi Host: $PI_HOST (using SSH config)${NC}"
echo -e "${YELLOW}Pi User: $PI_USER${NC}"

# Check if we can connect to Pi
echo -e "${YELLOW}🔗 Testing Pi connection...${NC}"
if ! ssh -o ConnectTimeout=10 $PI_USER@$PI_HOST "echo 'Connection successful'"; then
    echo -e "${RED}❌ Cannot connect to Pi. Check SSH connection.${NC}"
    echo -e "${YELLOW}Try: ssh $PI_USER@$PI_HOST${NC}"
    exit 1
fi

# Create remote directory
echo -e "${YELLOW}📁 Creating remote directory...${NC}"
ssh $PI_USER@$PI_HOST "mkdir -p $REMOTE_DIR"

# Copy only essential boat files to Pi (skip large files)
echo -e "${YELLOW}📤 Uploading updated boat files...${NC}"
rsync -avz --progress \
    --include='boat/' \
    --include='boat/**' \
    --include='boat_app.py' \
    --include='config.json' \
    --exclude='*' \
    ./ $PI_USER@$PI_HOST:$REMOTE_DIR/

echo -e "${GREEN}✅ Files uploaded successfully${NC}"

# Make scripts executable
echo -e "${YELLOW}🔧 Setting permissions...${NC}"
ssh $PI_USER@$PI_HOST "chmod +x $REMOTE_DIR/*.py"

# Check and update Python environment (use existing .venv)
echo -e "${YELLOW}🐍 Checking existing Python environment...${NC}"
ssh $PI_USER@$PI_HOST "
    cd $REMOTE_DIR
    
    # Check if .venv exists
    if [ -d '.venv' ]; then
        echo 'Using existing virtual environment'
        source .venv/bin/activate
        
        # Check if required packages are installed
        echo 'Checking installed packages...'
        pip list | grep -E '(aiohttp|aiortc|websockets)' || {
            echo 'Installing missing packages...'
            pip install aiohttp aiortc websockets
        }
        
        echo 'Python environment ready'
    else
        echo 'No .venv found, creating new one...'
        python3 -m venv .venv
        source .venv/bin/activate
        pip install --upgrade pip
        pip install aiohttp aiortc websockets av numpy picamera2 gpiozero
    fi
"

# Create or update systemd service for boat
echo -e "${YELLOW}⚙️ Checking boat systemd service...${NC}"
ssh $PI_USER@$PI_HOST "
    # Check if service already exists
    if [ -f '/etc/systemd/system/harbor-boat.service' ]; then
        echo 'Service already exists, updating if needed...'
    else
        echo 'Creating new service...'
    fi
    
    sudo tee /etc/systemd/system/harbor-boat.service > /dev/null << 'EOF'
[Unit]
Description=Harbor Boat Client
After=network.target

[Service]
Type=simple
User=$PI_USER
WorkingDirectory=$REMOTE_DIR
Environment=PATH=$REMOTE_DIR/.venv/bin
ExecStart=$REMOTE_DIR/.venv/bin/python3 boat_app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable harbor-boat
"

echo -e "${GREEN}✅ Boat service ready${NC}"

# Start the boat service
echo -e "${YELLOW}🚀 Starting boat service...${NC}"
ssh $PI_USER@$PI_HOST "
    sudo systemctl restart harbor-boat
    sleep 2
    sudo systemctl status harbor-boat --no-pager -l
"

echo -e "\n${GREEN}🎉 Boat deployment complete!${NC}"

echo -e "\n${YELLOW}Useful commands for Pi:${NC}"
echo -e "ssh $PI_HOST                          # Connect to Pi (using SSH config)"
echo -e "sudo systemctl status harbor-boat     # Check status"
echo -e "sudo journalctl -u harbor-boat -f    # View logs"
echo -e "sudo systemctl restart harbor-boat   # Restart service"

echo -e "\n${YELLOW}Test manual run:${NC}"
echo -e "cd $REMOTE_DIR && source .venv/bin/activate && python3 boat_app.py"

echo -e "\n${GREEN}🌟 Boat should now be streaming automatically!${NC}"
