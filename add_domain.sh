#!/bin/bash

# Add additional domain to existing Harbor VPS setup
# Usage: ./add_domain.sh example.com /path/to/app

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <domain> [app_port] [app_path]"
    echo "Examples:"
    echo "  $0 example.com                    # Static site"
    echo "  $0 api.example.com 3000           # Proxy to port 3000"
    echo "  $0 app.example.com 4000 /app      # Proxy to port 4000 with path"
    exit 1
fi

DOMAIN=$1
APP_PORT=${2:-""}
APP_PATH=${3:-"/"}

echo -e "${GREEN}🌐 Adding domain: $DOMAIN${NC}"
echo -e "${YELLOW}Port: ${APP_PORT:-"static"}${NC}"
echo -e "${YELLOW}Path: $APP_PATH${NC}"

# Create nginx configuration
if [ -n "$APP_PORT" ]; then
    # Proxy configuration
    cat > /etc/nginx/sites-available/$DOMAIN << EOF
# $DOMAIN - Proxied Application
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Proxy to application
    location $APP_PATH {
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
        
        # Handle large uploads
        client_max_body_size 10M;
    }
}
EOF
else
    # Static site configuration
    mkdir -p /var/www/$DOMAIN
    cat > /etc/nginx/sites-available/$DOMAIN << EOF
# $DOMAIN - Static Site
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    root /var/www/$DOMAIN;
    index index.html index.htm;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    location / {
        try_files \$uri \$uri/ =404;
    }
    
    # Optional: PHP support
    # location ~ \.php$ {
    #     include snippets/fastcgi-php.conf;
    #     fastcgi_pass unix:/var/run/php/php7.4-fpm.sock;
    # }
}
EOF
    
    # Create basic index.html
    cat > /var/www/$DOMAIN/index.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>$DOMAIN</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
        .container { max-width: 600px; margin: 0 auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to $DOMAIN</h1>
        <p>This domain is configured and ready to use.</p>
        <p>Upload your content to <code>/var/www/$DOMAIN/</code></p>
    </div>
</body>
</html>
EOF
    
    echo -e "${GREEN}✅ Created static site at /var/www/$DOMAIN${NC}"
fi

# Enable the site
ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/

# Test nginx configuration
echo -e "${YELLOW}Testing nginx configuration...${NC}"
if nginx -t; then
    echo -e "${GREEN}✅ Nginx configuration valid${NC}"
    
    # Reload nginx
    systemctl reload nginx
    echo -e "${GREEN}✅ Nginx reloaded${NC}"
else
    echo -e "${RED}❌ Nginx configuration invalid${NC}"
    # Remove the bad config
    rm -f /etc/nginx/sites-enabled/$DOMAIN
    exit 1
fi

# Setup SSL certificate
echo -e "${YELLOW}🔒 Setting up SSL certificate for $DOMAIN...${NC}"
if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    echo -e "${GREEN}SSL certificate already exists${NC}"
else
    echo -e "${YELLOW}Obtaining SSL certificate...${NC}"
    if certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN; then
        echo -e "${GREEN}✅ SSL certificate obtained${NC}"
    else
        echo -e "${RED}❌ Failed to obtain SSL certificate${NC}"
        echo -e "${YELLOW}You can try manually: certbot --nginx -d $DOMAIN${NC}"
    fi
fi

echo -e "\n${GREEN}🎉 Domain $DOMAIN added successfully!${NC}"

# Show status
echo -e "\n${YELLOW}Domain Status:${NC}"
echo -e "HTTP:  http://$DOMAIN"
echo -e "HTTPS: https://$DOMAIN"

if [ -n "$APP_PORT" ]; then
    echo -e "Proxying to: localhost:$APP_PORT"
    echo -e "\n${YELLOW}Make sure your application is running on port $APP_PORT${NC}"
else
    echo -e "Static files: /var/www/$DOMAIN/"
    echo -e "\n${YELLOW}Upload your content to /var/www/$DOMAIN/${NC}"
fi

echo -e "\n${YELLOW}Useful commands:${NC}"
echo -e "sudo nginx -t                    # Test configuration"
echo -e "sudo systemctl reload nginx     # Reload nginx"
echo -e "sudo certbot certificates       # List SSL certificates"
echo -e "ls /etc/nginx/sites-enabled/    # List enabled sites"
