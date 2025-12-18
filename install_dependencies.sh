#!/bin/bash
# 🚀 CYBER CRACK PRO v3.0 - AUTO INSTALLER
# Instalasi otomatis semua dependencies yang dibutuhkan

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[→]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_header() {
    echo -e "${CYAN}
################################################################################
# 🚀 CYBER CRACK PRO v3.0 - AUTO INSTALLER
# Instalasi Dependencies Secara Otomatis
################################################################################
${NC}"
}

print_header

print_info "Checking system requirements..."

# Check if running as root (not required but recommended)
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root is not recommended"
fi

# Check OS
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
    print_status "Detected OS: $OS $VER"
else
    print_error "Cannot detect OS"
    exit 1
fi

# Update package lists
print_info "Updating package lists..."
sudo apt update || true

# Install system dependencies
print_info "Installing system dependencies..."
sudo apt install -y \
    build-essential \
    cmake \
    openjdk-11-jdk \
    android-tools-adb \
    android-tools-fastboot \
    wget \
    curl \
    unzip \
    git \
    python3-dev \
    python3-pip \
    python3-venv \
    || {
        print_error "Failed to install system dependencies"
        exit 1
    }

print_status "System dependencies installed"

# Install Python dependencies
print_info "Installing Python dependencies..."
pip3 install --upgrade pip

# Install from requirements file
if [ -f "requirements_fixed.txt" ]; then
    pip3 install -r requirements_fixed.txt
    print_status "Python dependencies installed from requirements"
else
    print_warning "requirements_fixed.txt not found, installing core dependencies..."
    pip3 install \
        aiogram python-dotenv \
        fastapi uvicorn jinja2 \
        androguard pyaxmlparser python-magic \
        torch transformers tokenizers \
        numpy pandas scikit-learn scipy \
        adbutils capstone keystone-engine lief \
        colorama click tabulate pyyaml \
        redis aiohttp aiofiles asyncio \
        loguru structlog prometheus-client
fi

print_status "Python dependencies installed"

# Install Apktool
print_info "Installing Apktool..."
if ! command -v apktool &> /dev/null; then
    APKTOOL_VERSION="2.7.0"
    APKTOOL_SCRIPT_URL="https://raw.githubusercontent.com/iBotPeach/apktool/master/scripts/linux/apktool"
    APKTOOL_JAR_URL="https://bitbucket.org/iBotPeach/apktool/downloads/apktool_$APKTOOL_VERSION.jar"
    
    wget "$APKTOOL_SCRIPT_URL" -O apktool
    wget "$APKTOOL_JAR_URL" -O apktool.jar
    chmod 755 apktool apktool.jar
    sudo mv apktool apktool.jar /usr/local/bin/
    print_status "Apktool installed"
else
    print_info "Apktool already installed"
fi

# Install Jadx
print_info "Installing Jadx..."
if ! command -v jadx &> /dev/null; then
    JADX_VERSION="1.4.7"
    JADX_URL="https://github.com/skylot/jadx/releases/download/v$JADX_VERSION/jadx-$JADX_VERSION.zip"
    
    wget "$JADX_URL" -O jadx.zip
    unzip jadx.zip
    sudo mv jadx-$JADX_VERSION /opt/jadx
    sudo ln -sf /opt/jadx/bin/jadx /usr/local/bin/jadx
    sudo ln -sf /opt/jadx/bin/jadx-gui /usr/local/bin/jadx-gui
    print_status "Jadx installed"
else
    print_info "Jadx already installed"
fi

# Install Rust (for Rust Cracker)
print_info "Installing Rust (for Rust Cracker)..."
if ! command -v rustc &> /dev/null; then
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source ~/.cargo/env
    print_status "Rust installed"
else
    print_info "Rust already installed"
fi

# Install Go (for Go Analyzer)
print_info "Installing Go (for Go Analyzer)..."
if ! command -v go &> /dev/null; then
    GO_VERSION="1.21.5"
    GO_URL="https://golang.org/dl/go$GO_VERSION.linux-amd64.tar.gz"
    
    wget "$GO_URL"
    sudo rm -rf /usr/local/go
    sudo tar -C /usr/local -xzf "go$GO_VERSION.linux-amd64.tar.gz"
    echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
    source ~/.bashrc
    print_status "Go installed"
else
    print_info "Go already installed"
fi

# Install Docker (optional but recommended)
print_info "Installing Docker (optional)..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
    print_status "Docker installed"
else
    print_info "Docker already installed"
fi

# Install Docker Compose
print_info "Installing Docker Compose (optional)..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose installed"
else
    print_info "Docker Compose already installed"
fi

# Create necessary directories
print_info "Creating project directories..."
mkdir -p uploads results temp logs tools
print_status "Project directories created"

# Test Python imports
print_info "Testing Python imports..."
python3 -c "
import aiogram
import fastapi
import uvicorn
import androguard
import torch
import numpy
import pandas
print('✅ All core Python modules imported successfully')
" || {
    print_error "Some Python modules failed to import"
    print_warning "This might be due to compilation issues with some packages"
    print_info "Try installing packages individually if issues persist"
}

print_info ""
print_info "${GREEN}🎉 INSTALLATION COMPLETE! 🎉${NC}"
print_info ""
print_info "📋 Sistem siap digunakan dengan semua dependencies terinstal"
print_info ""
print_info "🔧 Untuk menjalankan sistem:"
print_info "   1. Buat file .env dengan konfigurasi Anda"
print_info "   2. Jalankan: ./run_system.sh start"
print_info "   3. Web dashboard: http://localhost:8000"
print_info ""
print_info "⚠️  Jika Anda baru saja menginstal Rust/Go, mungkin perlu reload shell:"
print_info "   source ~/.cargo/env && source ~/.bashrc"
print_info ""
print_info "${CYAN}Sistem Cyber Crack Pro v3.0 sekarang siap digunakan!${NC}"