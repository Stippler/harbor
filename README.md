# Harbor WebRTC Camera Streaming System

Harbor is a WebRTC-based camera streaming system designed for Raspberry Pi boats with relay server architecture.

## Architecture

The system consists of two main components:

### 1. Harbor Server (Relay)
- Runs on a central server/computer
- Relays WebRTC streams between boat clients and browser clients
- Provides web interface for viewing boat streams
- Manages boat connections and availability

### 2. Boat Client
- Runs on Raspberry Pi Zero (or other Pi models)
- Captures camera feed and streams via WebRTC
- Connects to Harbor server as a client
- Includes GPIO control for LEDs and motors

## Quick Start

### Running the Harbor Server

```bash
# Start the relay server
python3 app.py --host 0.0.0.0 --port 8080
```

The server will be available at `http://localhost:8080`

### Running a Boat Client

```bash
# On the Raspberry Pi
python3 boat_app.py --server ws://your-harbor-server:8080 --boat-id my-boat-1
```

## Installation

### Server Requirements
```bash
pip install aiohttp aiortc websockets
```

### Boat Client Requirements (Raspberry Pi)
```bash
pip install aiohttp aiortc websockets picamera2 gpiozero
```

## Configuration

### Harbor Server Options
- `--host`: Host to bind to (default: 0.0.0.0)
- `--port`: Port to bind to (default: 8080)
- `--cert`: Path to TLS cert for HTTPS
- `--key`: Path to TLS key for HTTPS

### Boat Client Options
- `--server`: Harbor server URL (required)
- `--width`: Camera width (default: 160)
- `--height`: Camera height (default: 120)
- `--fps`: Camera FPS (default: 30)
- `--boat-id`: Unique boat identifier

## Usage

1. Start the Harbor server on your main computer
2. Start boat clients on each Raspberry Pi
3. Open the web interface at the server URL
4. Select a boat from the dropdown
5. Click "Connect" to start streaming

## Features

- **WebRTC Streaming**: Low-latency video streaming
- **Multi-boat Support**: Connect multiple boats to one server
- **Web Interface**: Modern responsive web UI
- **GPIO Control**: LED and motor control on boat clients
- **Auto-discovery**: Boats automatically register with server
- **Fallback Modes**: Demo mode when camera unavailable

## File Structure

```
harbor/
├── app.py                 # Main Harbor server application
├── boat_app.py           # Boat client application
├── harbor/               # Harbor server package
│   ├── __init__.py
│   ├── client.py         # Web interface HTML
│   ├── server.py         # WebSocket server for boats/browsers
│   └── relay.py          # WebRTC relay functionality
└── boat/                 # Boat client package
    ├── __init__.py
    ├── client.py         # Boat WebRTC client
    ├── video.py          # Camera streaming
    ├── motor.py          # Motor control
    ├── led.py            # LED control
    └── websocket.py      # Local WebSocket server
```

## Network Requirements

- Boats need network access to reach the Harbor server
- WebRTC uses UDP for media streams
- WebSocket connections for signaling
- Default ports: 8080 (HTTP), 8443 (HTTPS if enabled)

## Troubleshooting

### Camera Issues
- Ensure camera is enabled: `sudo raspi-config`
- Check picamera2 installation
- Verify camera permissions

### Network Issues
- Check firewall settings
- Ensure boats can reach server IP
- Verify WebSocket connectivity

### GPIO Issues
- Run with sudo if GPIO access fails
- Check pin assignments
- Verify gpiozero installation

## Development

The system is built with:
- **aiohttp**: Async web framework
- **aiortc**: WebRTC implementation
- **picamera2**: Raspberry Pi camera interface
- **gpiozero**: GPIO control library

## License

This project is open source and available under the MIT License.