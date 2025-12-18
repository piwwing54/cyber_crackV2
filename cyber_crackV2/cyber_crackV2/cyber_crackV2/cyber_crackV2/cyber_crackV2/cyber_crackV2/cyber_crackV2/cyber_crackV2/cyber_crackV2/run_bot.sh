#!/bin/bash
# 🚀 SCRIPT JALANKAN CYBER CRACK PRO TELEGRAM BOT LANGSUNG
# Gunakan script ini untuk menjalankan bot secara langsung

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
# 🚀 CYBER CRACK PRO - TELEGRAM BOT RUNNER
# Langsung terhubung ke bot @Yancumintybot (ID: 8548539065)
################################################################################
${NC}"
}

# Check if Docker is running
print_info "Checking Docker service..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker service first."
    exit 1
fi

print_status "Docker is running"

# Navigate to project directory
PROJECT_DIR="/home/piwwing/bot-tele/cyber-crack-pro"
if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Project directory not found: $PROJECT_DIR"
    exit 1
fi

cd $PROJECT_DIR

print_info "Setting up Cyber Crack Pro in: $PROJECT_DIR"

# Create necessary directories
mkdir -p uploads results logs temp models
print_status "Created directories: uploads, results, logs, temp, models"

# Create .env file with the bot token
cat > .env << EOF
# 🤖 Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=8548539065:AAHLcyMQKHimwo1cLTuUKZl8OR1xngL_GeI
REDIS_URL=redis://redis:6379
POSTGRES_URL=postgresql://cracker:securepassword123@postgres:5432/cybercrack
ORCHESTRATOR_URL=http://orchestrator:5000
API_GATEWAY_URL=http://localhost:5000

# Performance Settings
MAX_WORKERS=10
UPLOAD_LIMIT_MB=500
GPU_ACCELERATION=false
AI_ENHANCED_ANALYSIS=true
LOG_LEVEL=INFO
EOF

print_status "Created environment configuration"

# Build the Docker images using docker-compose
print_info "Building Docker images (this may take several minutes)..."

# Create a minimal docker-compose file for just the essential services
cat > docker-compose-temp.yml << 'EOF'
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - ./data/redis:/data
    networks:
      - cyber_crack_net

  go-analyzer:
    build:
      context: .
      dockerfile: core/go-analyzer/Dockerfile
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    networks:
      - cyber_crack_net
    volumes:
      - ./uploads:/app/uploads

  rust-cracker:
    build:
      context: .
      dockerfile: core/rust-cracker/Dockerfile
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    networks:
      - cyber_crack_net
    volumes:
      - ./uploads:/app/uploads

  cpp-breaker:
    build:
      context: .
      dockerfile: core/cpp-breaker/Dockerfile
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    networks:
      - cyber_crack_net
    volumes:
      - ./uploads:/app/uploads

  java-dex:
    build:
      context: .
      dockerfile: core/java-dex/Dockerfile
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    networks:
      - cyber_crack_net
    volumes:
      - ./uploads:/app/uploads

  python-bridge:
    build:
      context: .
      dockerfile: core/python-bridge/Dockerfile
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    networks:
      - cyber_crack_net
    volumes:
      - ./uploads:/app/uploads

  orchestrator:
    build:
      context: .
      dockerfile: brain/Dockerfile.orchestrator
    environment:
      - REDIS_URL=redis://redis:6379
      - POSTGRES_URL=postgresql://cracker:securepassword123@postgres:5432/cybercrack
      - GO_ANALYZER_URL=http://go-analyzer:8080
      - RUST_CRACKER_URL=http://rust-cracker:8081
      - CPP_BREAKER_URL=http://cpp-breaker:8082
      - JAVA_DEX_URL=http://java-dex:8083
      - PYTHON_BRIDGE_URL=http://python-bridge:8084
    depends_on:
      - redis
      - postgres
      - go-analyzer
      - rust-cracker
      - cpp-breaker
      - java-dex
      - python-bridge
    networks:
      - cyber_crack_net
    volumes:
      - ./uploads:/app/uploads
      - ./results:/app/results

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=cybercrack
      - POSTGRES_USER=cracker
      - POSTGRES_PASSWORD=securepassword123
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    networks:
      - cyber_crack_net

  # MAIN TELEGRAM BOT SERVICE
  telegram-bot:
    build:
      context: .
      dockerfile: frontend/Dockerfile.telegram
    environment:
      - TELEGRAM_BOT_TOKEN=8548539065:AAHLcyMQKHimwo1cLTuUKZl8OR1xngL_GeI
      - ORCHESTRATOR_URL=http://orchestrator:5000
      - REDIS_URL=redis://redis:6379
    depends_on:
      - orchestrator
      - redis
    networks:
      - cyber_crack_net
    volumes:
      - ./uploads:/app/uploads
      - ./results:/app/results

networks:
  cyber_crack_net:
    driver: bridge

volumes:
  redis_data:
  postgres_data:
EOF

# Build images
docker-compose -f docker-compose-temp.yml build --parallel

print_status "Docker images built successfully!"

# Start the services
print_info "Starting Cyber Crack Pro services..."
docker-compose -f docker-compose-temp.yml up -d

print_status "Services started successfully!"

# Wait for the bot to be ready
print_info "Waiting for Telegram bot to be ready..."
sleep 30

# Check the logs to see the bot status
print_info "Bot startup logs:"
docker-compose -f docker-compose-temp.yml logs telegram-bot

print_info ""
print_info "${GREEN}🎉 CYBER CRACK PRO TELEGRAM BOT IS NOW RUNNING! 🎉${NC}"
print_info ""
print_info "🤖 Your bot @Yancumintybot should now be operational"
print_info "🔗 Send /start to your bot on Telegram to begin"
print_info "📁 Upload APK files for instant cracking"
print_info "⚡ Processing will begin automatically"
print_info ""
print_info "${CYAN}Bot is connected to the following services:${NC}"
print_info "   • Go Analyzer (Ultra Fast) - Port 8080"
print_info "   • Rust Cracker (Binary)    - Port 8081" 
print_info "   • C++ Breaker (GPU)        - Port 8082"
print_info "   • Java DEX (Android)      - Port 8083"
print_info "   • Python Bridge (AI)      - Port 8084"
print_info "   • Orchestrator (Main)     - Port 5000"
print_info ""
print_info "${YELLOW}To stop the bot, run: docker-compose -f docker-compose-temp.yml down${NC}"

# Clean up temp file
rm -f docker-compose-temp.yml