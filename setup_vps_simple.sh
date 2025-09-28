#!/bin/bash

# Simple Harbor VPS Setup - Uses dedicated port 7890
# No nginx, no SSL complexity, just works!

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
DOMAIN="deepharbor.xyz"
IP="2.56.96.36"
USER="cstippel"
HARBOR_DIR="/home/$USER/harbor"
HARBOR_PORT="7890"
SERVICE_NAME="harbor"

echo -e "${GREEN}🚢 Simple Harbor VPS Setup${NC}"
echo -e "${YELLOW}Domain: $DOMAIN${NC}"
echo -e "${YELLOW}Port: $HARBOR_PORT${NC}"
echo -e "${YELLOW}User: $USER${NC}"

# Update system
echo -e "${YELLOW}📦 Updating system packages...${NC}"
apt update && apt upgrade -y

# Install basic dependencies
echo -e "${YELLOW}🔧 Installing dependencies...${NC}"
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    ufw \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev

# Setup firewall - MUCH SIMPLER!
echo -e "${YELLOW}🔥 Configuring firewall...${NC}"
ufw --force enable
ufw allow ssh
ufw allow 2222/tcp          # Your SSH port
ufw allow $HARBOR_PORT/tcp  # Harbor HTTP port
ufw allow 10000:20000/udp   # WebRTC media

echo -e "${GREEN}✅ Firewall configured for port $HARBOR_PORT${NC}"
ufw status

# Create harbor directory
echo -e "${YELLOW}📁 Setting up Harbor directory...${NC}"
if [ ! -d "$HARBOR_DIR" ]; then
    mkdir -p "$HARBOR_DIR"
    chown $USER:$USER "$HARBOR_DIR"
fi

# Setup Python virtual environment
echo -e "${YELLOW}🐍 Setting up Python virtual environment...${NC}"
sudo -u $USER bash -c "
    cd '$HARBOR_DIR'
    
    # Remove existing venv if it exists
    if [ -d 'venv' ]; then
        echo 'Removing existing virtual environment...'
        rm -rf venv
    fi
    
    # Create new virtual environment
    echo 'Creating virtual environment...'
    python3 -m venv venv
    
    # Activate and install packages
    source venv/bin/activate
    echo 'Virtual environment activated'
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Harbor dependencies
    if [ -f 'requirements.txt' ]; then
        echo 'Installing from requirements.txt...'
        pip install -r requirements.txt
    else
        echo 'Installing basic dependencies...'
        pip install aiohttp aiortc websockets av numpy
    fi
    
    echo 'Python packages installed:'
    pip list
"

echo -e "${GREEN}✅ Python virtual environment ready${NC}"

# Create systemd service
echo -e "${YELLOW}⚙️ Creating systemd service...${NC}"
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Harbor WebRTC Streaming Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HARBOR_DIR
Environment=PATH=$HARBOR_DIR/venv/bin
ExecStart=$HARBOR_DIR/venv/bin/python3 app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable service
systemctl daemon-reload
systemctl enable $SERVICE_NAME

echo -e "${GREEN}✅ Setup complete!${NC}"

# Display connection info
echo -e "\n${GREEN}🎉 Harbor VPS Setup Complete!${NC}"
echo -e "\n${YELLOW}Connection URLs:${NC}"
echo -e "Web interface: http://$DOMAIN:$HARBOR_PORT"
echo -e "Web interface: http://$IP:$HARBOR_PORT"
echo -e "Boat client:   ws://$DOMAIN:$HARBOR_PORT"
echo -e "Boat fallback: ws://$IP:$HARBOR_PORT"

echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "1. Make sure your Harbor code is in: $HARBOR_DIR"
echo -e "2. Check config.json uses port $HARBOR_PORT"
echo -e "3. Start Harbor: sudo systemctl start $SERVICE_NAME"
echo -e "4. Check status: sudo systemctl status $SERVICE_NAME"
echo -e "5. View logs: sudo journalctl -u $SERVICE_NAME -f"

echo -e "\n${YELLOW}DNS Setup:${NC}"
echo -e "Point $DOMAIN to $IP (A record)"
echo -e "No need for port 80/443 - we use $HARBOR_PORT!"

echo -e "\n${YELLOW}Useful commands:${NC}"
echo -e "sudo systemctl start $SERVICE_NAME     # Start Harbor"
echo -e "sudo systemctl stop $SERVICE_NAME      # Stop Harbor"
echo -e "sudo systemctl restart $SERVICE_NAME   # Restart Harbor"
echo -e "sudo journalctl -u $SERVICE_NAME -f    # View logs"
echo -e "netstat -tlnp | grep $HARBOR_PORT       # Check if running"

echo -e "\n${GREEN}🌟 No nginx, no SSL complexity, just works!${NC}"
