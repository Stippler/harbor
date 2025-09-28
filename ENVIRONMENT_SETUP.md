# Environment Setup Guide

This guide covers different ways to set up isolated Python environments for Harbor.

## Quick Start (Recommended)

### For VPS Server:
```bash
# 1. Deploy code
./deploy.sh

# 2. Setup on VPS (creates virtual environment automatically)
sudo /home/cstippel/harbor/setup_vps.sh
```

### For Raspberry Pi Boat:
```bash
# Run on each Pi
sudo ./setup_boat_env.sh
```

## Environment Options

### 1. Python venv (Default)

**Pros:** Built-in, lightweight, fast
**Cons:** Basic package management

```bash
# Create environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Deactivate
deactivate
```

### 2. Conda Environment

**Pros:** Better package management, handles system libraries
**Cons:** Larger, more complex

```bash
# Setup with script
sudo ./setup_conda.sh

# Or manually
conda env create -f environment.yml
conda activate harbor

# Deactivate
conda deactivate
```

### 3. System-wide Installation (Not Recommended)

**Pros:** Simple
**Cons:** Can break system, no isolation

```bash
# Don't do this in production!
sudo pip install -r requirements.txt
```

## File Structure

```
harbor/
├── requirements.txt           # Server dependencies
├── requirements-boat.txt      # Boat/Pi dependencies  
├── environment.yml           # Conda environment
├── setup_vps.sh             # VPS setup (venv)
├── setup_conda.sh           # VPS setup (conda)
├── setup_boat_env.sh        # Pi boat setup
└── deploy.sh                # Deployment script
```

## Environment Comparison

| Method | Server | Boat/Pi | Isolation | Speed | Disk Usage |
|--------|--------|---------|-----------|-------|------------|
| venv | ✅ | ✅ | Good | Fast | Small |
| conda | ✅ | ⚠️ | Excellent | Medium | Large |
| system | ❌ | ❌ | None | Fast | Small |

## Dependencies

### Server Requirements (requirements.txt)
- aiohttp - Web framework
- aiortc - WebRTC implementation  
- websockets - WebSocket support
- av - Audio/video processing
- numpy - Numerical computing

### Boat Requirements (requirements-boat.txt)
- All server requirements plus:
- picamera2 - Raspberry Pi camera
- gpiozero - GPIO control

## Troubleshooting

### Virtual Environment Issues

```bash
# Remove and recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Permission Issues
```bash
# Fix ownership
sudo chown -R $USER:$USER /path/to/harbor

# Fix permissions
chmod +x *.sh
```

### Missing System Libraries
```bash
# Install system dependencies first
sudo apt update
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev

# For audio/video support
sudo apt install -y libavformat-dev libavcodec-dev libavdevice-dev
```

### Conda Issues
```bash
# Reset conda environment
conda env remove -n harbor
conda env create -f environment.yml

# Update conda
conda update conda
```

## Production Recommendations

### VPS Server
1. **Use venv** - Lightweight and sufficient
2. **Run as non-root user** - Security best practice
3. **Use systemd service** - Auto-restart and logging
4. **Enable firewall** - UFW with specific ports

### Raspberry Pi Boat
1. **Use venv** - Conda too heavy for Pi Zero
2. **Pin dependency versions** - Avoid breaking updates
3. **Use systemd service** - Auto-start on boot
4. **Monitor resources** - Pi Zero has limited RAM

### Development
1. **Use separate environments** - Don't mix dev/prod
2. **Version control requirements** - Pin versions in production
3. **Test in clean environments** - Catch missing dependencies

## Commands Reference

### Virtual Environment
```bash
# Create
python3 -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Deactivate
deactivate

# Remove
rm -rf venv
```

### Conda
```bash
# Create from file
conda env create -f environment.yml

# Create manually
conda create -n harbor python=3.9

# Activate
conda activate harbor

# Deactivate
conda deactivate

# Remove
conda env remove -n harbor

# List environments
conda env list

# Export current environment
conda env export > environment.yml
```

### Package Management
```bash
# Install from requirements
pip install -r requirements.txt

# Update all packages
pip install --upgrade -r requirements.txt

# List installed packages
pip list

# Create requirements file
pip freeze > requirements.txt

# Install specific version
pip install aiohttp==3.8.0
```

This setup ensures clean, isolated environments for both development and production!
