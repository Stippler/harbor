# Simple Harbor Setup Guide

## Why Port 7890?

Instead of fighting over port 80/443 with nginx, Apache, or other services, Harbor now uses a dedicated port **7890**:

- ✅ **No conflicts** - Avoids port 80/443 battles
- ✅ **No nginx needed** - Direct connection to Harbor
- ✅ **No SSL complexity** - Keep it simple for development
- ✅ **Easy firewall** - Just open one port
- ✅ **Multiple domains** - Each service gets its own port

## Quick Setup

### 1. Deploy to VPS
```bash
# From your local machine
./deploy.sh
```

### 2. Setup on VPS
```bash
# SSH to your VPS
ssh -p 2222 cstippel@2.56.96.36

# Run simple setup (as root)
sudo /home/cstippel/harbor/setup_vps_simple.sh

# Start Harbor
sudo systemctl start harbor
```

### 3. Access Harbor
- **Web**: http://deepharbor.xyz:7890
- **Boat client**: ws://deepharbor.xyz:7890
- **Fallback**: ws://2.56.96.36:7890

## Port Configuration

### Current Setup (config.json)
```json
{
  "server": {
    "port": 7890,
    "public_port": 7890
  },
  "boat": {
    "server_url": "ws://deepharbor.xyz:7890",
    "fallback_server_url": "ws://2.56.96.36:7890"
  }
}
```

### Firewall Rules
```bash
sudo ufw allow 7890/tcp        # Harbor HTTP
sudo ufw allow 10000:20000/udp # WebRTC media
sudo ufw allow 2222/tcp        # Your SSH
```

## Multiple Domains on Same VPS

Each service gets its own port:

| Service | Domain | Port | Purpose |
|---------|--------|------|---------|
| Harbor | deepharbor.xyz | 7890 | WebRTC streaming |
| Blog | myblog.xyz | 8080 | Personal blog |
| API | api.example.com | 3000 | REST API |
| Admin | admin.example.com | 4000 | Admin panel |

### Adding Another Service

1. **Choose available port**:
```bash
./check_ports.sh  # Find available ports
```

2. **Open firewall**:
```bash
sudo ufw allow 8080/tcp  # For your new service
```

3. **Point domain to VPS**:
   - DNS A record: `myblog.xyz → 2.56.96.36`
   - Access: `http://myblog.xyz:8080`

## Troubleshooting

### Check if Harbor is running
```bash
sudo systemctl status harbor
netstat -tlnp | grep 7890
```

### View logs
```bash
sudo journalctl -u harbor -f
```

### Test connectivity
```bash
# From anywhere
curl -I http://deepharbor.xyz:7890
curl -I http://2.56.96.36:7890

# WebSocket test
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: test" \
     http://deepharbor.xyz:7890/ws
```

### Change port if needed
1. Edit `config.json`
2. Update firewall: `sudo ufw allow NEW_PORT/tcp`
3. Restart Harbor: `sudo systemctl restart harbor`

## Benefits of This Approach

### ✅ Pros
- **Simple**: No nginx/Apache configuration
- **Fast**: Direct connection to Harbor
- **Reliable**: No proxy layer to break
- **Flexible**: Easy to change ports
- **Debuggable**: Clear error messages
- **Scalable**: Each service independent

### ❌ Cons
- **Port in URL**: Users see `:7890` in address
- **No SSL**: Would need manual certificate setup
- **No caching**: No nginx caching layer
- **No load balancing**: Single Harbor instance

## Production Considerations

For production, you might want:

1. **SSL/HTTPS**: Use Let's Encrypt with certbot
2. **Domain without port**: Use nginx reverse proxy
3. **Load balancing**: Multiple Harbor instances
4. **Caching**: Static asset caching

But for development and simple deployments, **port 7890 works perfectly!**

## Common Issues

### "Connection refused"
- Check Harbor is running: `sudo systemctl status harbor`
- Check firewall: `sudo ufw status`
- Check port: `netstat -tlnp | grep 7890`

### "Port already in use"
- Find available port: `./check_ports.sh`
- Update config.json with new port
- Restart Harbor

### DNS not resolving
- Check A record: `dig deepharbor.xyz`
- Use IP directly: `http://2.56.96.36:7890`
- Wait for DNS propagation (up to 48 hours)

This simple approach gets you up and running quickly without the complexity of web server configuration!
