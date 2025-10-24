#!/bin/bash

echo "🚀 Setting up CI/CD environment for OpenBMC testing..."

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
echo "📦 Installing Docker..."
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
echo "📦 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.15.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Python and dependencies
echo "🐍 Installing Python and dependencies..."
sudo apt-get install -y python3 python3-pip python3-venv chromium-browser chromium-chromedriver

# Create and activate virtual environment
echo "📁 Creating Python virtual environment..."
python3 -m venv ~/venv/openbmc-ci
source ~/venv/openbmc-ci/bin/activate

# Upgrade pip in virtual environment
pip install --upgrade pip

# Install Jenkins dependencies in virtual environment
echo "📋 Installing Jenkins dependencies in virtual environment..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p jenkins_data test-results scripts

echo "✅ Environment setup completed!"
echo "🔑 Please logout and login again for Docker group changes to take effect"
echo "🐍 Virtual environment created at: ~/venv/openbmc-ci"
echo "🚀 Then run: docker-compose up -d"
echo ""
echo "📝 To activate virtual environment later, run:"
echo "   source ~/venv/openbmc-ci/bin/activate"
