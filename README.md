# Harbor 🌊

**High-Performance WebRTC Camera Streaming for Raspberry Pi**

Harbor is a modern, responsive WebRTC video streaming server designed specifically for Raspberry Pi, featuring real-time camera streaming, GPIO LED control, and a beautiful web interface that works on desktop and mobile devices.

![Harbor Interface](https://img.shields.io/badge/Interface-Responsive-blue) ![Python](https://img.shields.io/badge/Python-3.8%2B-green) ![WebRTC](https://img.shields.io/badge/WebRTC-Enabled-orange) ![License](https://img.shields.io/badge/License-MIT-red)

## ✨ Features

### 🎥 **WebRTC Video Streaming**
- **Low-latency streaming** optimized for Raspberry Pi camera
- **High-performance capture** with threaded processing
- **Automatic fallback** to demo mode for testing without hardware
- **Configurable resolution and FPS** (up to 1080p@60fps)
- **Browser-based viewing** with no client software required

### 🔌 **GPIO Control**
- **Real-time LED control** via WebSocket commands
- **Dual motor control** with H-bridge driver support (L298N, etc.)
- **Mock mode** for development without GPIO hardware  
- **Flexible pin configuration** supporting all GPIO pins
- **Multiple LED support** with concurrent control
- **Robot movement patterns** (forward, backward, turn, spin)

### 🌐 **Modern Web Interface**
- **Responsive design** optimized for mobile and desktop
- **Dark/light mode** support with system preference detection
- **Touch-friendly controls** for mobile devices
- **Real-time connection status** with visual indicators
- **Live command logging** with timestamps

### 🔒 **Security & Production Ready**
- **HTTPS/TLS support** for secure WebRTC connections
- **Self-signed certificate generation** for testing
- **Production deployment** configurations
- **Graceful error handling** and recovery

## 🚀 Quick Start

### **1. Automated Setup**
```bash
# Clone or navigate to the project directory
cd harbor

# Run the automated setup (creates conda environment and installs everything)
./setup_environment.sh
```

### **2. Start the Server**
```bash
# HTTP mode (development)
./start_harbor.sh

# HTTPS mode (production)  
./start_harbor_https.sh
```

### **3. Open in Browser**
Navigate to `http://localhost:8080` (or `https://localhost:8443` for HTTPS)

## 📋 Installation

### **Prerequisites**
- **Python 3.8+** 
- **Conda** (Miniconda or Anaconda)
- **Optional**: Raspberry Pi with camera module and GPIO access

### **Dependencies**

#### **Core Dependencies**
```bash
pip install aiohttp aiortc av numpy
```

#### **Raspberry Pi Dependencies** (optional)
```bash
pip install picamera2 gpiozero
```

### **Environment Setup**

#### **Using Conda (Recommended)**
```bash
# Create environment from file
conda env create -f environment.yml

# Activate environment
conda activate harbor

# Install additional dependencies
pip install -r requirements.txt
```

#### **Using pip**
```bash
# Install core dependencies
pip install -r requirements.txt

# For Raspberry Pi, uncomment Pi-specific packages in requirements.txt
```

## 🔧 Usage

### **Command Line Options**
```bash
python app.py [OPTIONS]

Options:
  --host HOST          Host to bind to (default: 0.0.0.0)
  --port PORT          Port to bind to (default: 8080)
  --width WIDTH        Camera width in pixels (default: 640)
  --height HEIGHT      Camera height in pixels (default: 480)
  --fps FPS           Camera FPS (default: 30)
  --cert CERT         Path to TLS certificate for HTTPS
  --key KEY           Path to TLS private key for HTTPS
```

### **Startup Scripts**

#### **HTTP Server**
```bash
# Basic startup
./start_harbor.sh

# Custom configuration
./start_harbor.sh [host] [port] [width] [height] [fps]

# Example: 1080p at 30fps on port 8080
./start_harbor.sh 0.0.0.0 8080 1920 1080 30
```

#### **HTTPS Server**
```bash
# HTTPS with auto-generated certificates
./start_harbor_https.sh

# Custom HTTPS configuration
./start_harbor_https.sh [host] [port] [width] [height] [fps]
```

### **System Check**
```bash
# Verify system requirements and dependencies
python check_system.py
```

## 🖥️ Web Interface

### **Video Streaming**
- **Connect button** to establish WebRTC connection
- **Status indicators** showing connection state (idle/connecting/connected/error)
- **Video placeholder** with instructions before connection
- **Demo mode notification** when camera hardware is unavailable

### **LED Control**
- **GPIO pin selector** (1-40) with validation
- **LED ON/OFF buttons** with visual feedback
- **Real-time command responses** in the log

### **Network Testing**
- **Ping command** for latency measurement
- **Connection log** with timestamps
- **WebSocket status** monitoring

### **Mobile Support**
- **Touch-optimized controls** with larger buttons
- **Single-column layout** on small screens
- **Swipe-friendly scrolling** in log areas
- **Responsive typography** and spacing

## 🔧 Development

### **Project Structure**
```
harbor/
├── app.py                 # Main application entry point
├── harbor/                # Core package
│   ├── __init__.py       # App factory and configuration
│   ├── client.py         # Web interface (HTML/CSS/JS)
│   ├── led.py            # GPIO LED controller
│   ├── video.py          # Camera streaming with demo mode
│   ├── webrtc.py         # WebRTC offer/answer handling
│   └── websocket.py      # WebSocket command interface
├── setup_environment.sh  # Automated environment setup
├── start_harbor.sh       # HTTP startup script
├── start_harbor_https.sh # HTTPS startup script
├── check_system.py       # System verification
├── environment.yml       # Conda environment specification
├── requirements.txt      # Python dependencies
└── test_*.py            # Testing scripts
```

### **Demo Mode**
Harbor includes a comprehensive demo mode that works without any hardware:

- **Synthetic video generation** with animated patterns
- **Mock GPIO control** with proper logging
- **Full WebRTC functionality** using canvas-generated streams
- **Automatic fallback** when Pi hardware is unavailable

### **Testing Without Hardware**
```bash
# The application automatically detects missing hardware
# and enables demo mode with:
# - Animated video stream
# - Mock LED control
# - Full web interface functionality
# - WebRTC streaming simulation

python app.py  # Works on any laptop/desktop
```

## 🚀 Deployment

### **Raspberry Pi Setup**

#### **1. System Dependencies**
```bash
sudo apt update
sudo apt install python3-pip python3-venv
```

#### **2. Enable Hardware**
```bash
sudo raspi-config
# Enable: Camera, GPIO interfaces
```

#### **3. Install Python Dependencies**
```bash
pip install aiohttp aiortc av numpy picamera2 gpiozero
```

#### **4. Run with Proper Permissions**
```bash
# May need sudo for GPIO access
sudo python app.py --host 0.0.0.0 --port 80
```

### **Production Deployment**

#### **HTTPS Configuration**
```bash
# Generate certificates (for testing)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Start with HTTPS
python app.py --cert cert.pem --key key.pem --port 8443
```

#### **Systemd Service** (Optional)
```ini
[Unit]
Description=Harbor WebRTC Streaming
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/harbor
ExecStart=/home/pi/harbor/start_harbor.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

### **Docker Deployment** (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8080
CMD ["python", "app.py", "--host", "0.0.0.0"]
```

## 🔍 Troubleshooting

### **Common Issues**

#### **WebRTC Connection Fails**
- Ensure HTTPS for cross-origin scenarios
- Check browser console for errors
- Verify network connectivity and firewall settings
- Try different browsers (Chrome, Firefox, Safari)

#### **Camera Not Working**
- Check if `picamera2` is installed for Pi hardware
- Verify camera is enabled in `raspi-config`
- Application will automatically fall back to demo mode

#### **GPIO Control Not Working**
- Ensure `gpiozero` is installed
- Check GPIO permissions (may need `sudo`)
- Verify pin numbers are correct (1-40)
- Demo mode provides mock GPIO for testing

#### **Performance Issues**
- Adjust resolution with `--width` and `--height`
- Lower FPS with `--fps` parameter
- Monitor CPU usage during streaming
- Check network bandwidth

### **System Verification**
```bash
# Run comprehensive system check
python check_system.py

# Check specific components
python -c "from harbor import create_app; print('✅ Harbor imports OK')"
```

### **Debug Mode**
```bash
# Enable verbose logging
python app.py --host 0.0.0.0 --port 8080
# Check console output for detailed information
```

## 🌟 Advanced Features

### **Custom Video Configurations**
```bash
# 4K streaming (if supported)
python app.py --width 3840 --height 2160 --fps 30

# Low latency mode
python app.py --width 320 --height 240 --fps 60

# High quality mode
python app.py --width 1920 --height 1080 --fps 30
```

### **Multiple LED Control**
The web interface supports controlling multiple LEDs:
- Change GPIO pin number in the interface
- Send commands to different pins
- Monitor responses in real-time log

### **Network Testing**
- Use the Ping button to measure latency
- Monitor WebSocket connection status
- Check server logs for connection details

## 🤝 Contributing

### **Development Setup**
```bash
# Fork the repository
# Clone your fork
git clone https://github.com/yourusername/harbor.git
cd harbor

# Set up development environment
./setup_environment.sh

# Run system checks
python check_system.py

# Start development server
./start_harbor.sh
```

### **Code Structure**
- **Backend**: Python with aiohttp for async web server
- **WebRTC**: aiortc library for peer-to-peer streaming
- **Frontend**: Vanilla HTML/CSS/JavaScript (no frameworks)
- **Hardware**: picamera2 for Pi camera, gpiozero for GPIO

### **Testing**
```bash
# Test LED controller
python test_led.py --mode states --pins 17 18 19

# Test camera functionality
python test2.py  # Basic camera test
python test3.py  # Performance test
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **aiortc** for excellent WebRTC implementation
- **Raspberry Pi Foundation** for amazing hardware
- **aiohttp** for high-performance async web server
- **PyAV** for video processing capabilities

---

## 📞 Support

### **Getting Help**
1. **Check the logs** - Server provides detailed error messages
2. **Run system check** - `python check_system.py`
3. **Browser console** - Check for JavaScript errors
4. **Try demo mode** - Works without any hardware

### **Reporting Issues**
When reporting issues, please include:
- Python version (`python --version`)
- Operating system and version
- Hardware details (if using Raspberry Pi)
- Error messages from console/logs
- Steps to reproduce the issue

---

**Harbor - Bringing high-performance WebRTC streaming to Raspberry Pi! 🌊**
