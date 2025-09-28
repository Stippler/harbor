#!/bin/bash

# Deploy Harbor to VPS
# Run this from your local machine

set -e

# Configuration
VPS_HOST="2.56.96.36"
VPS_USER="cstippel"
VPS_PORT="2222"
REMOTE_DIR="/home/cstippel/harbor"
DOMAIN="deepharbor.xyz"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚢 Deploying Harbor to VPS...${NC}"
echo -e "${YELLOW}VPS: $VPS_HOST:$VPS_PORT${NC}"
echo -e "${YELLOW}User: $VPS_USER${NC}"
echo -e "${YELLOW}Domain: $DOMAIN${NC}"

# Check if we can connect to VPS
echo -e "${YELLOW}🔗 Testing VPS connection...${NC}"
if ! ssh -p $VPS_PORT $VPS_USER@$VPS_HOST "echo 'Connection successful'"; then
    echo -e "${RED}❌ Cannot connect to VPS. Check your SSH config.${NC}"
    exit 1
fi

# Create remote directory
echo -e "${YELLOW}📁 Creating remote directory...${NC}"
ssh -p $VPS_PORT $VPS_USER@$VPS_HOST "mkdir -p $REMOTE_DIR"

# Copy files to VPS (excluding unwanted files)
echo -e "${YELLOW}📤 Uploading Harbor files...${NC}"
rsync -avz --progress \
    --exclude '.git' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.DS_Store' \
    --exclude 'venv' \
    --exclude 'deploy.sh' \
    -e "ssh -p $VPS_PORT" \
    ./ $VPS_USER@$VPS_HOST:$REMOTE_DIR/

echo -e "${GREEN}✅ Files uploaded successfully${NC}"

# Make scripts executable
echo -e "${YELLOW}🔧 Setting permissions...${NC}"
ssh -p $VPS_PORT $VPS_USER@$VPS_HOST "chmod +x $REMOTE_DIR/*.py $REMOTE_DIR/*.sh"

# Note: Python environment will be set up by setup_vps.sh
echo -e "${YELLOW}📝 Python environment will be configured by setup_vps.sh${NC}"

# Display next steps
echo -e "\n${GREEN}🎉 Deployment complete!${NC}"
echo -e "\n${YELLOW}Next steps (run on VPS as root/sudo):${NC}"
echo -e "1. SSH to VPS: ssh -p $VPS_PORT $VPS_USER@$VPS_HOST"
echo -e "2. Run SIMPLE setup: sudo $REMOTE_DIR/setup_vps_simple.sh"
echo -e "3. Start Harbor: sudo systemctl start harbor"
echo -e "4. Check status: sudo systemctl status harbor"

echo -e "\n${YELLOW}Or run this one-liner on VPS:${NC}"
echo -e "${GREEN}sudo $REMOTE_DIR/setup_vps_simple.sh && sudo systemctl start harbor${NC}"

echo -e "\n${YELLOW}URLs after setup (port 7890):${NC}"
echo -e "Web: http://$DOMAIN:7890"
echo -e "Boat: ws://$DOMAIN:7890"
echo -e "Fallback: ws://$VPS_HOST:7890"

echo -e "\n${YELLOW}Check logs:${NC}"
echo -e "sudo journalctl -u harbor -f"
