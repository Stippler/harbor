#!/bin/bash

# Fix port 80 conflict and setup domain-specific routing
# Run this on your VPS to diagnose and fix the issue

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔍 Diagnosing port 80 conflict...${NC}"

# Check what's using port 80
echo -e "${YELLOW}Services using port 80:${NC}"
sudo netstat -tlnp | grep :80 || echo "No services found on port 80"
sudo ss -tlnp | grep :80 || echo "No services found on port 80 (ss)"

# Check for common web servers
echo -e "\n${YELLOW}Checking for existing web servers:${NC}"
if systemctl is-active --quiet apache2 2>/dev/null; then
    echo -e "${RED}Apache2 is running${NC}"
    APACHE_RUNNING=true
else
    echo "Apache2: not running"
    APACHE_RUNNING=false
fi

if systemctl is-active --quiet nginx 2>/dev/null; then
    echo -e "${GREEN}Nginx is running${NC}"
    NGINX_RUNNING=true
else
    echo "Nginx: not running"
    NGINX_RUNNING=false
fi

if systemctl is-active --quiet lighttpd 2>/dev/null; then
    echo -e "${YELLOW}Lighttpd is running${NC}"
    LIGHTTPD_RUNNING=true
else
    echo "Lighttpd: not running"
    LIGHTTPD_RUNNING=false
fi

# Check for Harbor running on port 8080
echo -e "\n${YELLOW}Checking Harbor service:${NC}"
if systemctl is-active --quiet harbor 2>/dev/null; then
    echo -e "${GREEN}Harbor is running${NC}"
    sudo netstat -tlnp | grep :8080 || echo "Harbor not listening on 8080"
else
    echo "Harbor: not running"
fi

echo -e "\n${YELLOW}Solutions:${NC}"

if [ "$APACHE_RUNNING" = true ]; then
    echo -e "${YELLOW}Option 1: Stop Apache and use Nginx${NC}"
    echo "sudo systemctl stop apache2"
    echo "sudo systemctl disable apache2"
    echo ""
    
    echo -e "${YELLOW}Option 2: Configure Apache as reverse proxy${NC}"
    echo "Keep Apache running and configure it to proxy to Harbor"
    echo ""
fi

echo -e "${YELLOW}Option 3: Use different ports${NC}"
echo "Run Harbor directly on port 80 (not recommended for multiple domains)"
echo ""

echo -e "${YELLOW}Option 4: Domain-specific routing (Recommended)${NC}"
echo "Configure nginx to handle multiple domains"

read -p "Which option would you like? (1-4): " choice

case $choice in
    1)
        if [ "$APACHE_RUNNING" = true ]; then
            echo -e "${YELLOW}Stopping Apache...${NC}"
            sudo systemctl stop apache2
            sudo systemctl disable apache2
            echo -e "${GREEN}Apache stopped${NC}"
        fi
        echo -e "${YELLOW}Starting nginx...${NC}"
        sudo systemctl start nginx
        sudo systemctl enable nginx
        ;;
    2)
        echo -e "${YELLOW}Setting up Apache reverse proxy...${NC}"
        # Create Apache config for Harbor
        sudo tee /etc/apache2/sites-available/deepharbor.conf > /dev/null << 'EOF'
<VirtualHost *:80>
    ServerName deepharbor.xyz
    ServerAlias www.deepharbor.xyz
    
    ProxyPreserveHost On
    ProxyRequests Off
    
    # WebSocket support
    ProxyPass /ws ws://127.0.0.1:8080/ws
    ProxyPassReverse /ws ws://127.0.0.1:8080/ws
    
    ProxyPass /boat ws://127.0.0.1:8080/boat
    ProxyPassReverse /boat ws://127.0.0.1:8080/boat
    
    # Regular HTTP traffic
    ProxyPass / http://127.0.0.1:8080/
    ProxyPassReverse / http://127.0.0.1:8080/
</VirtualHost>
EOF
        sudo a2enmod proxy proxy_http proxy_wstunnel
        sudo a2ensite deepharbor.conf
        sudo systemctl reload apache2
        echo -e "${GREEN}Apache configured as reverse proxy${NC}"
        ;;
    3)
        echo -e "${YELLOW}You'll need to modify Harbor to run on port 80${NC}"
        echo "Edit config.json and change port to 80"
        echo "Note: This requires running as root and won't work with multiple domains"
        ;;
    4)
        echo -e "${YELLOW}Setting up domain-specific nginx configuration...${NC}"
        # This will be handled by the updated setup script
        ;;
esac

echo -e "\n${GREEN}Diagnosis complete!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Fix the port conflict above"
echo "2. Run the updated setup script"
echo "3. Configure domain-specific routing"
