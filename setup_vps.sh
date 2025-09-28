#!/bin/bash

# Harbor VPS Setup Script for deepharbor.xyz
# Run this on your VPS (2.56.96.36) as root or with sudo

set -e  # Exit on any error

echo "🚢 Setting up Harbor on VPS for deepharbor.xyz..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="deepharbor.xyz"
IP="2.56.96.36"
USER="cstippel"
HARBOR_DIR="/home/$USER/harbor"
SERVICE_NAME="harbor"

echo -e "${GREEN}Domain: $DOMAIN${NC}"
echo -e "${GREEN}IP: $IP${NC}"
echo -e "${GREEN}User: $USER${NC}"

# Update system
echo -e "${YELLOW}📦 Updating system packages...${NC}"
apt update && apt upgrade -y

# Install dependencies
echo -e "${YELLOW}🔧 Installing dependencies...${NC}"
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    nginx \
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
    libswresample-dev \
    certbot \
    python3-certbot-nginx

# Setup firewall
echo -e "${YELLOW}🔥 Configuring firewall...${NC}"
ufw --force enable
ufw allow ssh
ufw allow 2222/tcp  # Your SSH port
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 8080/tcp  # Harbor HTTP
ufw allow 10000:20000/udp  # WebRTC media

echo -e "${GREEN}✅ Firewall configured${NC}"
ufw status

# Create harbor directory if it doesn't exist
echo -e "${YELLOW}📁 Setting up Harbor directory...${NC}"
if [ ! -d "$HARBOR_DIR" ]; then
    mkdir -p "$HARBOR_DIR"
    chown $USER:$USER "$HARBOR_DIR"
fi

# Setup Python virtual environment
echo -e "${YELLOW}🐍 Setting up Python virtual environment...${NC}"

# Create virtual environment as the user (not root)
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
    
    # Activate and upgrade pip
    source venv/bin/activate
    echo 'Virtual environment activated'
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Harbor dependencies from requirements.txt
    if [ -f 'requirements.txt' ]; then
        echo 'Installing Harbor dependencies from requirements.txt...'
        pip install -r requirements.txt
    else
        echo 'requirements.txt not found, installing basic dependencies...'
        pip install aiohttp aiortc websockets av numpy
    fi
    
    echo 'Python packages installed:'
    pip list
"

echo -e "${GREEN}✅ Python virtual environment ready at $HARBOR_DIR/venv${NC}"

# Verify the virtual environment
if [ -f "$HARBOR_DIR/venv/bin/python3" ]; then
    echo -e "${GREEN}✅ Virtual environment created successfully${NC}"
    sudo -u $USER "$HARBOR_DIR/venv/bin/python3" --version
else
    echo -e "${RED}❌ Failed to create virtual environment${NC}"
    exit 1
fi

# Setup systemd service
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

# Check for port conflicts
echo -e "${YELLOW}🔍 Checking for port conflicts...${NC}"
PORT_80_USED=$(netstat -tlnp | grep :80 | wc -l)
if [ "$PORT_80_USED" -gt 0 ]; then
    echo -e "${RED}⚠️  Port 80 is already in use:${NC}"
    netstat -tlnp | grep :80
    
    # Check if Apache is running
    if systemctl is-active --quiet apache2 2>/dev/null; then
        echo -e "${YELLOW}Apache2 detected. Stopping it to use nginx...${NC}"
        systemctl stop apache2
        systemctl disable apache2
        echo -e "${GREEN}✅ Apache2 stopped${NC}"
    fi
    
    # Check for other services
    BLOCKING_SERVICES=$(netstat -tlnp | grep :80 | awk '{print $7}' | cut -d'/' -f2 | sort -u)
    if [ ! -z "$BLOCKING_SERVICES" ]; then
        echo -e "${RED}Other services using port 80: $BLOCKING_SERVICES${NC}"
        echo -e "${YELLOW}You may need to stop them manually${NC}"
    fi
fi

# Setup nginx reverse proxy with domain-specific configuration
echo -e "${YELLOW}🌐 Configuring Nginx for multiple domains...${NC}"

# Create main Harbor site configuration
cat > /etc/nginx/sites-available/harbor-$DOMAIN << EOF
# Harbor WebRTC Streaming - $DOMAIN
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # WebSocket upgrade for /ws and /boat endpoints
    location /ws {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }

    location /boat {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }

    # Regular HTTP traffic
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Handle large uploads
        client_max_body_size 10M;
    }
}

# Fallback server for IP access
server {
    listen 80 default_server;
    server_name $IP _;

    # Redirect to main domain or serve basic page
    location / {
        return 301 http://$DOMAIN\$request_uri;
    }
}
EOF

# Enable nginx site
ln -sf /etc/nginx/sites-available/harbor-$DOMAIN /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default  # Remove default site

# Test nginx configuration
echo -e "${YELLOW}Testing nginx configuration...${NC}"
if nginx -t; then
    echo -e "${GREEN}✅ Nginx configuration valid${NC}"
else
    echo -e "${RED}❌ Nginx configuration invalid${NC}"
    echo -e "${YELLOW}Checking nginx error log:${NC}"
    tail -20 /var/log/nginx/error.log || echo "No error log found"
    exit 1
fi

# Setup SSL certificate (Let's Encrypt)
echo -e "${YELLOW}🔒 Setting up SSL certificate...${NC}"
if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    echo -e "${GREEN}SSL certificate already exists${NC}"
else
    echo -e "${YELLOW}Obtaining SSL certificate...${NC}"
    certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
fi

# Enable and start services
echo -e "${YELLOW}🚀 Starting services...${NC}"
systemctl daemon-reload
systemctl enable nginx
systemctl restart nginx
systemctl enable $SERVICE_NAME

echo -e "${GREEN}✅ Setup complete!${NC}"

# Display status
echo -e "\n${YELLOW}📊 Service Status:${NC}"
systemctl status nginx --no-pager -l
echo ""
systemctl status $SERVICE_NAME --no-pager -l

echo -e "\n${GREEN}🎉 Harbor VPS Setup Complete!${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "1. Upload your Harbor code to: $HARBOR_DIR"
echo -e "2. Make sure config.json is in: $HARBOR_DIR/config.json"
echo -e "3. Start Harbor service: systemctl start $SERVICE_NAME"
echo -e "4. Check logs: journalctl -u $SERVICE_NAME -f"
echo -e "\n${GREEN}URLs:${NC}"
echo -e "Web interface: https://$DOMAIN"
echo -e "Boat client URL: wss://$DOMAIN"
echo -e "Fallback IP: ws://$IP:8080"

echo -e "\n${YELLOW}Useful commands:${NC}"
echo -e "sudo systemctl status $SERVICE_NAME    # Check service status"
echo -e "sudo journalctl -u $SERVICE_NAME -f   # View live logs"
echo -e "sudo systemctl restart $SERVICE_NAME  # Restart service"
echo -e "sudo nginx -t                         # Test nginx config"
echo -e "sudo systemctl reload nginx          # Reload nginx"
EOF
