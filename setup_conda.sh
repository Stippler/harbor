#!/bin/bash

# Alternative setup using Conda instead of venv
# Run this if you prefer Conda over Python venv

set -e

# Configuration
DOMAIN="deepharbor.xyz"
IP="2.56.96.36"
USER="cstippel"
HARBOR_DIR="/home/$USER/harbor"
ENV_NAME="harbor"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🐍 Setting up Harbor with Conda environment...${NC}"

# Install Miniconda if not present
if ! command -v conda &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Miniconda...${NC}"
    
    # Download and install Miniconda
    cd /tmp
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    chmod +x Miniconda3-latest-Linux-x86_64.sh
    
    # Install as the user
    sudo -u $USER bash -c "./Miniconda3-latest-Linux-x86_64.sh -b -p /home/$USER/miniconda3"
    
    # Add conda to PATH
    sudo -u $USER bash -c "echo 'export PATH=/home/$USER/miniconda3/bin:\$PATH' >> /home/$USER/.bashrc"
    
    # Initialize conda
    sudo -u $USER /home/$USER/miniconda3/bin/conda init bash
    
    echo -e "${GREEN}✅ Miniconda installed${NC}"
fi

# Create conda environment
echo -e "${YELLOW}🌍 Creating Conda environment...${NC}"

sudo -u $USER bash -c "
    export PATH=/home/$USER/miniconda3/bin:\$PATH
    cd '$HARBOR_DIR'
    
    # Remove existing environment if it exists
    if conda env list | grep -q '$ENV_NAME'; then
        echo 'Removing existing conda environment...'
        conda env remove -n $ENV_NAME -y
    fi
    
    # Create new environment with Python 3.9+
    echo 'Creating conda environment: $ENV_NAME'
    conda create -n $ENV_NAME python=3.9 -y
    
    # Activate environment
    source /home/$USER/miniconda3/etc/profile.d/conda.sh
    conda activate $ENV_NAME
    
    # Install dependencies
    echo 'Installing dependencies with conda and pip...'
    
    # Install some packages via conda (often faster and better compatibility)
    conda install -c conda-forge numpy av -y
    
    # Install remaining packages via pip
    if [ -f 'requirements.txt' ]; then
        pip install -r requirements.txt
    else
        pip install aiohttp aiortc websockets
    fi
    
    # Create environment.yml for future reference
    conda env export > environment.yml
    
    echo 'Conda environment ready!'
    conda list
"

echo -e "${GREEN}✅ Conda environment '$ENV_NAME' created${NC}"

# Update systemd service to use conda
echo -e "${YELLOW}⚙️ Creating systemd service for Conda...${NC}"
cat > /etc/systemd/system/harbor.service << EOF
[Unit]
Description=Harbor WebRTC Streaming Server (Conda)
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HARBOR_DIR
Environment=PATH=/home/$USER/miniconda3/envs/$ENV_NAME/bin:/home/$USER/miniconda3/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/home/$USER/miniconda3/envs/$ENV_NAME/bin/python app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ Conda setup complete!${NC}"

# Instructions
echo -e "\n${YELLOW}To activate the environment manually:${NC}"
echo -e "source /home/$USER/miniconda3/etc/profile.d/conda.sh"
echo -e "conda activate $ENV_NAME"

echo -e "\n${YELLOW}To update dependencies:${NC}"
echo -e "conda activate $ENV_NAME"
echo -e "pip install -r requirements.txt --upgrade"

echo -e "\n${YELLOW}Environment location:${NC}"
echo -e "/home/$USER/miniconda3/envs/$ENV_NAME/"
