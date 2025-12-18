#!/bin/bash

# 🚀 CYBER CRACK PRO - Telegram Bot Setup Script
# Ini adalah script untuk langsung menjalankan bot di Telegram Anda

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[→]${NC} $1"
}

print_header() {
    echo -e "${CYAN}
################################################################################
# 🚀 CYBER CRACK PRO v3.0 - Telegram Bot Setup
# Langsung gunakan di akun Telegram Anda
################################################################################
${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_warning "This script should be run as root (using sudo)"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Setup cancelled."
        exit 1
    fi
fi

print_header

print_info "Starting Cyber Crack Pro Telegram Bot Setup..."

# Check prerequisites
print_info "Checking system prerequisites..."
required_commands=("docker" "docker-compose" "git" "python3" "pip3" "unzip" "zipalign" "curl")

for cmd in "${required_commands[@]}"; do
    if ! command -v $cmd &> /dev/null; then
        print_error "$cmd is not installed. Please install it first."
        exit 1
    fi
done

print_status "All prerequisites satisfied"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker service."
    exit 1
fi

print_status "Docker is running"

# Clone the repository or update if exists
if [ -d "cyber-crack-pro" ]; then
    print_info "Updating existing repository..."
    cd cyber-crack-pro
    git pull
else
    print_info "Cloning Cyber Crack Pro repository..."
    git clone https://github.com/cyber-crack-pro/cyber-crack-pro.git
    cd cyber-crack-pro
fi

print_status "Repository ready"

# Create environment file with your bot token
print_info "Creating environment configuration..."
cat > .env << EOF
# 🤖 CYBER CRACK PRO Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=8548539065:AAHLcyMQKHimwo1cLTuUKZl8OR1xngL_GeI
REDIS_URL=redis://localhost:6379
POSTGRES_URL=postgresql://cracker:securepassword123@localhost:5432/cybercrack
ORCHESTRATOR_URL=http://localhost:5000
API_GATEWAY_URL=http://localhost:5000

# Performance settings
MAX_WORKERS=10
UPLOAD_LIMIT_MB=500
GPU_ACCELERATION=true
AI_ENHANCED_ANALYSIS=true