#!/bin/bash

# Setup script for Raspberry Pi boat client
# Run this on each Raspberry Pi

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚤 Setting up Boat Client Environment...${NC}"

# Configuration
BOAT_DIR="/home/pi/harbor-boat"
USER="pi"

# Update system
echo -e "${YELLOW}📦 Updating system...${NC}"
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo -e "${YELLOW}🔧 Installing system dependencies...${NC}"
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
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

# Create boat directory
echo -e "${YELLOW}📁 Setting up boat directory...${NC}"
mkdir -p "$BOAT_DIR"
cd "$BOAT_DIR"

# Create virtual environment
echo -e "${YELLOW}🐍 Creating Python virtual environment...${NC}"
python3 -m venv venv

# Activate and install dependencies
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install boat dependencies
if [ -f "requirements-boat.txt" ]; then
    echo -e "${YELLOW}📋 Installing from requirements-boat.txt...${NC}"
    pip install -r requirements-boat.txt
else
    echo -e "${YELLOW}📋 Installing basic boat dependencies...${NC}"
    pip install aiohttp aiortc websockets av numpy picamera2 gpiozero
fi

echo -e "${GREEN}✅ Boat environment setup complete!${NC}"

# Create activation script
cat > activate_boat.sh << 'EOF'
#!/bin/bash
cd /home/pi/harbor-boat
source venv/bin/activate
echo "🚤 Boat environment activated!"
echo "Run: python3 boat_app.py --server ws://deepharbor.xyz:8080"
EOF

chmod +x activate_boat.sh

# Create systemd service for boat
echo -e "${YELLOW}⚙️ Creating boat systemd service...${NC}"
sudo tee /etc/systemd/system/harbor-boat.service > /dev/null << EOF
[Unit]
Description=Harbor Boat Client
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$BOAT_DIR
Environment=PATH=$BOAT_DIR/venv/bin
ExecStart=$BOAT_DIR/venv/bin/python3 boat_app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ Boat client setup complete!${NC}"

echo -e "\n${YELLOW}Usage:${NC}"
echo -e "1. Copy harbor boat files to: $BOAT_DIR"
echo -e "2. Edit config.json with your boat settings"
echo -e "3. Test: ./activate_boat.sh && python3 boat_app.py"
echo -e "4. Install service: sudo systemctl enable harbor-boat"
echo -e "5. Start service: sudo systemctl start harbor-boat"
echo -e "6. View logs: sudo journalctl -u harbor-boat -f"

echo -e "\n${YELLOW}Quick test:${NC}"
echo -e "source venv/bin/activate"
echo -e "python3 -c 'import aiohttp, aiortc, websockets; print(\"All imports successful!\")'"
