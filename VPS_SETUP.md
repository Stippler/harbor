# VPS Setup Guide for Harbor WebRTC Streaming

This guide covers setting up Harbor on a VPS (Virtual Private Server) for boat camera streaming.

## Prerequisites

- Ubuntu/Debian VPS with root access
- Domain name pointing to your VPS (optional but recommended)
- At least 1GB RAM, 1 CPU core
- Network connectivity between boats and VPS

## 1. Server Setup

### Automated Setup (Recommended)

The easiest way is to use the provided setup scripts:

```bash
# Deploy from your local machine
./deploy.sh

# Then on the VPS (as root/sudo)
sudo /home/cstippel/harbor/setup_vps.sh
```

### Manual Setup

If you prefer manual setup:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3 python3-pip python3-venv git build-essential libssl-dev libffi-dev python3-dev libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libswresample-dev

# Clone and setup Harbor
git clone <your-harbor-repo-url>
cd harbor

# Create isolated virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies from requirements.txt
pip install --upgrade pip
pip install -r requirements.txt
```

### Alternative: Conda Environment

If you prefer Conda:

```bash
# Use the conda setup script
sudo /home/cstippel/harbor/setup_conda.sh

# Or manually:
conda env create -f environment.yml
conda activate harbor
```

### Configure Harbor Server

Edit `config.json`:

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8080,
    "public_domain": "your-domain.com",
    "public_port": 8080,
    "ssl": {
      "enabled": false,
      "cert_file": "/etc/letsencrypt/live/your-domain.com/fullchain.pem",
      "key_file": "/etc/letsencrypt/live/your-domain.com/privkey.pem"
    }
  },
  "webrtc": {
    "ice_servers": [
      {
        "urls": "stun:stun.l.google.com:19302"
      }
    ]
  }
}
```

## 2. Firewall Configuration

### UFW (Ubuntu Firewall)

```bash
# Enable firewall
sudo ufw enable

# Allow SSH
sudo ufw allow ssh

# Allow Harbor HTTP port
sudo ufw allow 8080/tcp

# Allow HTTPS if using SSL
sudo ufw allow 443/tcp

# Allow WebRTC UDP range (for media streams)
sudo ufw allow 10000:20000/udp

# Check status
sudo ufw status
```

### iptables (Alternative)

```bash
# Allow established connections
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow SSH
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow Harbor HTTP
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT

# Allow HTTPS
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow WebRTC UDP
sudo iptables -A INPUT -p udp --dport 10000:20000 -j ACCEPT

# Save rules (Ubuntu/Debian)
sudo iptables-save > /etc/iptables/rules.v4
```

## 3. Port Requirements

### Required Ports

| Port | Protocol | Purpose | Direction |
|------|----------|---------|-----------|
| 8080 | TCP | HTTP Web Interface | Inbound |
| 443 | TCP | HTTPS (if SSL enabled) | Inbound |
| 10000-20000 | UDP | WebRTC Media Streams | Inbound |

### Port Forwarding (if behind NAT)

If your VPS is behind a firewall/router, forward these ports:
- TCP 8080 → VPS:8080 (or 443 → VPS:443 for HTTPS)
- UDP 10000-20000 → VPS:10000-20000

## 4. SSL/HTTPS Setup (Recommended)

### Using Let's Encrypt

```bash
# Install certbot
sudo apt install -y certbot

# Get certificate (replace with your domain)
sudo certbot certonly --standalone -d your-domain.com

# Update config.json to enable SSL
# Set "enabled": true and correct cert paths
```

### Update Harbor Config for SSL

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 443,
    "public_domain": "your-domain.com",
    "public_port": 443,
    "ssl": {
      "enabled": true,
      "cert_file": "/etc/letsencrypt/live/your-domain.com/fullchain.pem",
      "key_file": "/etc/letsencrypt/live/your-domain.com/privkey.pem"
    }
  }
}
```

## 5. Running Harbor as a Service

### Create systemd service

```bash
sudo nano /etc/systemd/system/harbor.service
```

Add this content:

```ini
[Unit]
Description=Harbor WebRTC Streaming Server
After=network.target

[Service]
Type=simple
User=harbor
WorkingDirectory=/home/harbor/harbor
Environment=PATH=/home/harbor/harbor/venv/bin
ExecStart=/home/harbor/harbor/venv/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Create harbor user and setup permissions

```bash
# Create user
sudo useradd -m -s /bin/bash harbor

# Copy harbor files to user directory
sudo cp -r /path/to/harbor /home/harbor/
sudo chown -R harbor:harbor /home/harbor/harbor

# Enable and start service
sudo systemctl enable harbor
sudo systemctl start harbor
sudo systemctl status harbor
```

## 6. Boat Client Configuration

On each Raspberry Pi boat, edit `config.json`:

```json
{
  "boat": {
    "server_url": "ws://your-domain.com:8080",
    "boat_id": "boat-1",
    "camera": {
      "width": 160,
      "height": 120,
      "fps": 30
    },
    "gpio": {
      "enable_motors": true,
      "enable_leds": true
    }
  }
}
```

For HTTPS, use `wss://your-domain.com` instead.

## 7. Network Requirements

### Boat Network Requirements

- Boats need internet access to reach the VPS
- Minimum 1 Mbps upload speed per boat
- Low latency connection preferred

### NAT Traversal

If boats are behind NAT/firewalls, you may need TURN servers:

```json
{
  "webrtc": {
    "ice_servers": [
      {
        "urls": "stun:stun.l.google.com:19302"
      },
      {
        "urls": "turn:your-turn-server.com:3478",
        "username": "user",
        "credential": "pass"
      }
    ]
  }
}
```

## 8. Monitoring and Logs

### View Harbor logs

```bash
# Service logs
sudo journalctl -u harbor -f

# Direct logs (if running manually)
cd /home/harbor/harbor
source venv/bin/activate
python3 app.py
```

### Monitor system resources

```bash
# CPU and memory usage
htop

# Network connections
sudo netstat -tulpn | grep :8080

# WebRTC connections
sudo ss -u | grep :10000
```

## 9. Troubleshooting

### Common Issues

1. **Boats can't connect**: Check firewall, domain name, port forwarding
2. **No video stream**: Check WebRTC UDP ports, NAT configuration
3. **SSL certificate errors**: Verify certificate paths and permissions
4. **High latency**: Check network connection, consider TURN server

### Debug Commands

```bash
# Test connectivity from boat
telnet your-domain.com 8080

# Check WebSocket connection
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: test" \
     http://your-domain.com:8080/boat

# Check SSL certificate
openssl s_client -connect your-domain.com:443
```

## 10. Security Considerations

- Use HTTPS/WSS in production
- Consider authentication for boat connections
- Regular security updates
- Monitor for unusual network activity
- Backup configuration files

## 11. Performance Tuning

### For high traffic (many boats)

```bash
# Increase file descriptor limits
echo "harbor soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "harbor hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize network settings
echo "net.core.rmem_max = 16777216" | sudo tee -a /etc/sysctl.conf
echo "net.core.wmem_max = 16777216" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### Resource monitoring

- Monitor CPU usage (should be < 80%)
- Monitor memory usage
- Monitor network bandwidth
- Consider load balancing for many boats

This setup should give you a production-ready Harbor streaming server!
