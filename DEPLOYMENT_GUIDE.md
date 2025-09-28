# Harbor Deployment Guide

## Complete Setup Process

### 1. Deploy Harbor Server (VPS)

```bash
# From your local machine
./deploy.sh
```

This will:
- Upload Harbor code to VPS
- Restart Harbor service automatically
- Harbor will be available at `http://deepharbor.xyz:7890`

### 2. Deploy Boat Client (Raspberry Pi)

```bash
# From your local machine
./deploy_boat.sh [pi_hostname] [pi_user]

# Examples:
./deploy_boat.sh raspberrypi.local pi
./deploy_boat.sh 192.168.1.100 pi
./deploy_boat.sh myboat.local ys
```

This will:
- Upload boat code to Pi
- Setup Python virtual environment
- Install dependencies (picamera2, gpiozero, etc.)
- Create systemd service
- Start boat streaming automatically

## How It Works

### Automatic Streaming
1. **Boat starts** → Connects to Harbor server
2. **Boat registers** → Sends capabilities (camera resolution, etc.)
3. **Boat creates offer** → Automatically starts WebRTC streaming
4. **Harbor stores offer** → Ready for browser clients
5. **Browser connects** → Gets live stream immediately

### Architecture
```
Raspberry Pi Boat ←→ Harbor Server ←→ Browser Clients
    (Camera)           (Relay)         (Web Interface)
```

## URLs and Access

- **Web Interface**: `http://deepharbor.xyz:7890`
- **Boat Connection**: `ws://deepharbor.xyz:7890` (fallback: `ws://2.56.96.36:7890`)

## Service Management

### VPS (Harbor Server)
```bash
# SSH to VPS
ssh -p 2222 cstippel@2.56.96.36

# Service commands
sudo systemctl status harbor
sudo systemctl restart harbor
sudo journalctl -u harbor -f
```

### Raspberry Pi (Boat Client)
```bash
# SSH to Pi
ssh pi@raspberrypi.local

# Service commands
sudo systemctl status harbor-boat
sudo systemctl restart harbor-boat
sudo journalctl -u harbor-boat -f
```

## Troubleshooting

### Harbor Server Issues
```bash
# Check if Harbor is running
netstat -tlnp | grep 7890

# Check logs
sudo journalctl -u harbor -f

# Test connectivity
curl -I http://localhost:7890
```

### Boat Client Issues
```bash
# Check boat service
sudo systemctl status harbor-boat

# Check logs
sudo journalctl -u harbor-boat -f

# Test manual run
cd /home/pi/harbor
source .venv/bin/activate
python3 boat_app.py
```

### Browser Client Issues
- **No boats showing**: Check boat is connected and registered
- **Connection failed**: Check WebRTC relay between boat and server
- **No video**: Check camera permissions and picamera2 setup

## Configuration

### Server Config (config.json)
```json
{
  "server": {
    "port": 7890,
    "public_domain": "deepharbor.xyz",
    "fallback_ip": "2.56.96.36"
  }
}
```

### Boat Config (config.json on Pi)
```json
{
  "boat": {
    "server_url": "ws://deepharbor.xyz:7890",
    "fallback_server_url": "ws://2.56.96.36:7890",
    "boat_id": "boat-1"
  }
}
```

## Multiple Boats

To add more boats:

1. **Deploy to each Pi**:
```bash
./deploy_boat.sh boat2.local pi
./deploy_boat.sh boat3.local pi
```

2. **Update boat IDs** on each Pi:
```bash
# On each Pi, edit config.json
nano /home/pi/harbor/config.json
# Change "boat_id": "boat-1" to unique IDs like "boat-2", "boat-3"

# Restart boat service
sudo systemctl restart harbor-boat
```

3. **Browser will show all boats** in the dropdown

## Firewall Ports

### VPS
- TCP 7890 - Harbor HTTP/WebSocket
- UDP 10000-20000 - WebRTC media streams

### Raspberry Pi
- No inbound ports needed (client connects out)

## Performance Tips

### For Raspberry Pi Zero
- Use lower resolution: 160x120 or 320x240
- Reduce FPS to 15-20 for better performance
- Ensure good SD card (Class 10 or better)

### For VPS
- Monitor CPU/memory usage with multiple boats
- Consider upgrading VPS if handling many boats
- Use SSD storage for better performance

## Security Notes

- **No authentication** currently - anyone can access streams
- **HTTP only** - no SSL/encryption
- **Open WebRTC** - direct P2P connections
- Consider adding authentication for production use

This setup provides automatic boat streaming with minimal configuration!
