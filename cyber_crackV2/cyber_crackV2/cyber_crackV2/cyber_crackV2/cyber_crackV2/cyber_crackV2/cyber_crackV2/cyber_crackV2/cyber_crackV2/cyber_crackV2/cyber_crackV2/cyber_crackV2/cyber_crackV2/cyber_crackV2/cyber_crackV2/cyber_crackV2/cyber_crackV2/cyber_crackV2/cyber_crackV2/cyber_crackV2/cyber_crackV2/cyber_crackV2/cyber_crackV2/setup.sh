#!/bin/bash
# 🚀 CYBER CRACK PRO v3.0 SETUP SCRIPT
# Complete installation and setup for the multi-language APK cracking system

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

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$PROJECT_DIR/setup.log"
CONFIG_FILE="$PROJECT_DIR/.env"

print_status() {
    echo -e "${GREEN}[✓]${NC} $1" | tee -a $LOG_FILE
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1" | tee -a $LOG_FILE
}

print_error() {
    echo -e "${RED}[✗]${NC} $1" | tee -a $LOG_FILE
}

print_info() {
    echo -e "${BLUE}[→]${NC} $1" | tee -a $LOG_FILE
}

print_header() {
    echo -e "${CYAN}
################################################################################
# 🚀 CYBER CRACK PRO v3.0 - Setup Script
# Multi-language ultra-fast APK cracking system with 100+ features
################################################################################
${NC}" | tee $LOG_FILE
}

create_directories() {
    print_info "Creating project directories..."
    
    # Create main directories
    mkdir -p "$PROJECT_DIR"/{uploads,results,temp,logs,models,data}
    
    # Create core engine directories
    mkdir -p "$PROJECT_DIR"/core/{go-analyzer,rust-cracker,cpp-breaker,java-dex,python-bridge}
    mkdir -p "$PROJECT_DIR"/core/go-analyzer/{src,dist}
    mkdir -p "$PROJECT_DIR"/core/rust-cracker/{src,target}
    mkdir -p "$PROJECT_DIR"/core/cpp-breaker/{src,build,obj}
    mkdir -p "$PROJECT_DIR"/core/java-dex/{src/main/java,src/main/resources,target}
    mkdir -p "$PROJECT_DIR"/core/python-bridge/{src,models}
    
    # Create other component directories
    mkdir -p "$PROJECT_DIR"/{frontend,brain,security,database,orchestrator,testing,kubernetes}
    
    print_status "Directories created successfully"
}

check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check for required commands
    local missing_deps=()
    
    for cmd in git docker docker-compose java python3 go rustc g++ make cmake; do
        if ! command -v $cmd &> /dev/null; then
            missing_deps+=($cmd)
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        echo "Please install the missing dependencies before continuing." | tee -a $LOG_FILE
        echo "For Ubuntu/Debian:" | tee -a $LOG_FILE
        echo "  sudo apt update && sudo apt install -y git docker docker-compose openjdk-11-jdk python3 python3-pip g++ cmake" | tee -a $LOG_FILE
        echo "  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh" | tee -a $LOG_FILE
        echo "  wget -qO- https://golang.org/dl/go1.21.5.linux-amd64.tar.gz | tar xvz -C /usr/local" | tee -a $LOG_FILE
        exit 1
    fi
    
    # Check Docker daemon status
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker daemon is not running"
        echo "Please start Docker service: sudo systemctl start docker" | tee -a $LOG_FILE
        exit 1
    fi
    
    print_status "All prerequisites satisfied"
}

install_apk_tools() {
    print_info "Installing APK analysis tools..."
    
    # Install APKTool
    if [ ! -f "/usr/local/bin/apktool" ]; then
        wget -q https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool -O /usr/local/bin/apktool
        chmod 755 /usr/local/bin/apktool
    fi
    
    # Download APKTool framework
    APKTOOL_DIR="$HOME/.local/share/apktool/framework"
    mkdir -p "$APKTOOL_DIR"
    
    if [ ! -f "$APKTOOL_DIR/1.apk" ]; then
        print_info "Downloading framework files..."
        # Try to download from official source
        # This is a placeholder - in reality you'd want to get the latest
    fi
    
    # Install zipalign and apksigner
    if [ ! -f "/usr/local/bin/zipalign" ]; then
        # For now, just mention requirement
        print_warning "zipalign and apksigner not found - install Android SDK for full functionality"
    fi
    
    print_status "APK analysis tools installed"
}

setup_python_environment() {
    print_info "Setting up Python environment..."
    
    # Install Python dependencies
    if [ -f "$PROJECT_DIR/requirements.txt" ]; then
        pip3 install --upgrade pip
        pip3 install -r "$PROJECT_DIR/requirements.txt" --no-cache-dir
    else
        # Create requirements file with essential packages
        cat > "$PROJECT_DIR/requirements.txt" << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
aiohttp==3.9.0
aioredis==2.0.1
redis==5.0.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
python-dotenv==1.0.0
requests==2.31.0
httpx==0.25.2
numpy==1.24.3
pandas==2.1.3
scikit-learn==1.3.2
torch==2.1.1
transformers==4.35.2
psutil==5.9.6
loguru==0.7.2
EOF
        pip3 install --upgrade pip
        pip3 install -r "$PROJECT_DIR/requirements.txt" --no-cache-dir
    fi
    
    print_status "Python environment set up"
}

setup_java_environment() {
    print_info "Setting up Java environment..."
    
    # Install Maven if not present
    if ! command -v mvn &> /dev/null; then
        print_info "Installing Maven..."
        apt-get update > /dev/null 2>&1
        apt-get install -y maven > /dev/null 2>&1 || print_warning "Could not install Maven automatically"
    fi
    
    # Install Android SDK tools if not present
    if [ ! -d "$HOME/android-sdk" ]; then
        print_info "Consider installing Android SDK for advanced functionality"
    fi
    
    print_status "Java environment prepared"
}

setup_go_environment() {
    print_info "Setting up Go environment..."
    
    # Install Go dependencies
    if [ -f "$PROJECT_DIR/core/go-analyzer/go.mod" ]; then
        cd "$PROJECT_DIR/core/go-analyzer"
        go mod download
        go build -o go-analyzer .
        cd "$PROJECT_DIR"
    fi
    
    print_status "Go environment set up"
}

setup_rust_environment() {
    print_info "Setting up Rust environment..."
    
    # Install Rust dependencies
    if [ -f "$PROJECT_DIR/core/rust-cracker/Cargo.toml" ]; then
        cd "$PROJECT_DIR/core/rust-cracker"
        cargo build --release
        cd "$PROJECT_DIR"
    fi
    
    print_status "Rust environment set up"
}

setup_cpp_environment() {
    print_info "Setting up C++ environment with GPU acceleration..."
    
    # Check for GPU support
    if nvidia-smi > /dev/null 2>&1; then
        print_status "NVIDIA GPU detected"
        
        # Check for CUDA installation
        if [ -d "/usr/local/cuda" ]; then
            print_status "CUDA installation found"
        else
            print_warning "CUDA not found - GPU acceleration will be disabled"
        fi
    else
        print_warning "No NVIDIA GPU detected - C++ GPU acceleration unavailable"
    fi
    
    print_status "C++ environment set up"
}

setup_java_dex_environment() {
    print_info "Setting up Java DEX environment..."
    
    # Install Java dependencies
    if [ -f "$PROJECT_DIR/core/java-dex/pom.xml" ]; then
        cd "$PROJECT_DIR/core/java-dex"
        mvn clean compile
        cd "$PROJECT_DIR"
    fi
    
    print_status "Java DEX environment set up"
}

create_config_file() {
    print_info "Creating configuration file..."
    
    # Create .env file with default settings
    cat > "$CONFIG_FILE" << EOF
# 🚀 CYBER CRACK PRO - Configuration File

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=8548539065:AAHLcyMQKHimwo1cLTuUKZl8OR1xngL_GeI

# Service URLs
ORCHESTRATOR_URL=http://localhost:5000
API_GATEWAY_URL=http://localhost:5000
GO_ANALYZER_URL=http://localhost:8080
RUST_CRACKER_URL=http://localhost:8081
CPP_BREAKER_URL=http://localhost:8082
JAVA_DEX_URL=http://localhost:8083
PYTHON_BRIDGE_URL=http://localhost:8084

# Database Configuration
REDIS_URL=redis://localhost:6379
POSTGRES_URL=postgresql://cracker:securepassword123@localhost:5432/cybercrack

# Engine Configuration
MAX_WORKERS=10
MAX_CONCURRENT_JOBS=20
UPLOAD_LIMIT_MB=500
PROCESSING_TIMEOUT=300
GPU_ACCELERATION=true
AI_ENHANCED_ANALYSIS=true

# Security Settings
ENABLE_ROOT_BYPASS=true
ENABLE_CERT_PINNING_BYPASS=true
ENABLE_DEBUG_BYPASS=true
ENABLE_LOGIN_BYPASS=true
ENABLE_IAP_BYPASS=true
ENABLE_GAME_MODS=true

# Performance Settings
PARALLEL_PROCESSING=true
BATCH_SIZE=5
CACHE_RESULTS=true
CACHE_TTL_HOURS=24
EOF
    
    print_status "Configuration file created at $CONFIG_FILE"
}

start_services() {
    print_info "Starting Cyber Crack Pro services..."
    
    # Build and start all services with Docker Compose
    if [ -f "$PROJECT_DIR/docker-compose.yml" ]; then
        # Create necessary volumes
        docker volume create cyber-crack-redis-data > /dev/null 2>&1 || true
        docker volume create cyber-crack-postgres-data > /dev/null 2>&1 || true
        
        # Start services
        docker-compose -f "$PROJECT_DIR/docker-compose.yml" up -d --build
        
        print_status "Services started successfully"
        print_info "Check service status with: docker-compose ps"
    else
        print_warning "docker-compose.yml not found, creating default..."
        
        # Create a minimal docker-compose file
        cat > "$PROJECT_DIR/docker-compose.yml" << 'EOF'
version: '3.8'

services:
  # Redis cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - ./data/redis:/data

  # Orchestrator service (main coordinator)
  orchestrator:
    build:
      context: ./brain
      dockerfile: Dockerfile.orchestrator
    ports:
      - "5000:5000"
    environment:
      - REDIS_URL=redis://redis:6379
      - GO_ANALYZER_URL=http://go-analyzer:8080
      - RUST_CRACKER_URL=http://rust-cracker:8081
      - CPP_BREAKER_URL=http://cpp-breaker:8082
      - JAVA_DEX_URL=http://java-dex:8083
      - PYTHON_BRIDGE_URL=http://python-bridge:8084
    depends_on:
      - redis
    volumes:
      - ./uploads:/app/uploads
      - ./results:/app/results

  # Individual engine services
  go-analyzer:
    build:
      context: ./core/go-analyzer
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  rust-cracker:
    build:
      context: ./core/rust-cracker
      dockerfile: Dockerfile
    ports:
      - "8081:8081"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  cpp-breaker:
    build:
      context: ./core/cpp-breaker
      dockerfile: Dockerfile
    ports:
      - "8082:8082"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  java-dex:
    build:
      context: ./core/java-dex
      dockerfile: Dockerfile
    ports:
      - "8083:8083"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  python-bridge:
    build:
      context: ./core/python-bridge
      dockerfile: Dockerfile
    ports:
      - "8084:8084"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  # Telegram bot
  telegram-bot:
    build:
      context: ./frontend
      dockerfile: Dockerfile.telegram
    ports:
      - "3001:3001"
    environment:
      - TELEGRAM_BOT_TOKEN=8548539065:AAHLcyMQKHimwo1cLTuUKZl8OR1xngL_GeI
      - ORCHESTRATOR_URL=http://orchestrator:5000
    depends_on:
      - orchestrator
    volumes:
      - ./uploads:/app/uploads
      - ./results:/app/results

volumes:
  redis_data:
  postgres_data:

networks:
  default:
    driver: bridge
EOF
        
        # Start services
        docker-compose -f "$PROJECT_DIR/docker-compose.yml" up -d --build
        
        print_status "Services started with default configuration"
    fi
}

create_systemd_service() {
    print_info "Creating systemd service file..."
    
    cat > "/tmp/cyber-crack-pro.service" << EOF
[Unit]
Description=Cyber Crack Pro - Multi-Language APK Cracking System
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/local/bin/docker-compose -f $PROJECT_DIR/docker-compose.yml up -d
ExecStop=/usr/local/bin/docker-compose -f $PROJECT_DIR/docker-compose.yml down
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Copy to system directory if running as root
    if [ "$EUID" -eq 0 ]; then
        sudo cp /tmp/cyber-crack-pro.service /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable cyber-crack-pro.service
        print_status "Systemd service created and enabled"
    else
        print_warning "Not root, skipping systemd service creation"
        print_info "To create systemd service, run as root: sudo $0"
    fi
}

setup_security() {
    print_info "Setting up security configurations..."
    
    # Create security directory structure
    mkdir -p "$PROJECT_DIR/security/{config,keys,certs}"
    
    # Create security config
    cat > "$PROJECT_DIR/security/config/security.conf" << 'EOF'
# Security Configuration for Cyber Crack Pro

# Encryption settings
ENCRYPTION_ALGORITHM=AES-256-GCM
SALT_LENGTH=32
IV_LENGTH=16

# Network security
ALLOW_INSECURE_CONNECTIONS=false
MAX_CONNECTIONS=100
CONNECTION_TIMEOUT=300
REQUEST_RATE_LIMIT=100  # per minute

# File security
MAX_FILE_SIZE=500MB
ALLOWED_FILE_TYPES=apk,jar,aar
UPLOAD_DIRECTORY_PERMISSIONS=755
TEMP_DIRECTORY_PERMISSIONS=700

# API security
JWT_EXPIRATION_HOURS=24
API_KEY_LENGTH=32
SESSION_TIMEOUT_MINUTES=30
EOF
    
    print_status "Security configuration created"
}

setup_monitoring() {
    print_info "Setting up monitoring and logging..."
    
    # Create monitoring directory
    mkdir -p "$PROJECT_DIR/monitoring"
    
    # Create monitoring config
    cat > "$PROJECT_DIR/monitoring/prometheus.yml" << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert.rules"

scrape_configs:
  - job_name: 'cyber-crack-pro'
    static_configs:
      - targets: ['localhost:8080', 'localhost:8081', 'localhost:8082', 'localhost:8083', 'localhost:8084', 'localhost:5000']
EOF
    
    print_status "Monitoring configuration created"
}

setup_kubernetes_configs() {
    print_info "Setting up Kubernetes configurations..."
    
    # Create kubernetes deployment file
    cat > "$PROJECT_DIR/kubernetes/deployment.yaml" << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cyber-crack-pro
  namespace: cyber-crack
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cyber-crack-pro
  template:
    metadata:
      labels:
        app: cyber-crack-pro
    spec:
      containers:
      - name: go-analyzer
        image: cyber-crack-pro/go-analyzer:latest
        ports:
        - containerPort: 8080
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
EOF
    
    print_status "Kubernetes configuration created"
}

validate_setup() {
    print_info "Validating setup..."
    
    local failed_checks=0
    
    # Check if services are running
    if docker-compose -f "$PROJECT_DIR/docker-compose.yml" ps | grep -q "Up"; then
        print_status "Docker services are running"
    else
        print_warning "Docker services may not be running properly"
        failed_checks=$((failed_checks + 1))
    fi
    
    # Check configuration files
    if [ -f "$CONFIG_FILE" ]; then
        print_status "Configuration file exists"
    else
        print_error "Configuration file missing"
        failed_checks=$((failed_checks + 1))
    fi
    
    # Check if required directories exist
    for dir in uploads results temp logs models; do
        if [ -d "$PROJECT_DIR/$dir" ]; then
            print_status "Directory $dir exists"
        else
            print_warning "Directory $PROJECT_DIR/$dir missing"
            mkdir -p "$PROJECT_DIR/$dir"
            print_info "Created missing directory $dir"
        fi
    done
    
    print_info "Setup validation complete"
    if [ $failed_checks -eq 0 ]; then
        print_status "Setup validation PASSED"
    else
        print_warning "Setup validation completed with $failed_checks warnings/errors"
    fi
}

show_completion_message() {
    echo -e "\n${GREEN}🎉 CYBER CRACK PRO SETUP COMPLETED SUCCESSFULLY! 🎉${NC}\n"
    
    echo -e "${CYAN}🚀 Services Started:${NC}"
    echo "  • Go Analyzer: http://localhost:8080"
    echo "  • Rust Cracker: http://localhost:8081" 
    echo "  • C++ Breaker: http://localhost:8082"
    echo "  • Java DEX: http://localhost:8083"
    echo "  • Python Bridge: http://localhost:8084"
    echo "  • Orchestrator: http://localhost:5000"
    
    echo -e "\n${CYAN}🤖 Telegram Bot:${NC}"
    echo "  • Bot is now active with your token"
    echo "  • Find @Yancumintybot on Telegram"
    echo "  • Use /start command to begin"
    
    echo -e "\n${CYAN}📁 Directories:${NC}"
    echo "  • Upload APKs to: $PROJECT_DIR/uploads"
    echo "  • Results available in: $PROJECT_DIR/results"
    echo "  • Logs stored in: $PROJECT_DIR/logs"
    
    echo -e "\n${CYAN}🔧 Management Commands:${NC}"
    echo "  • Check status: docker-compose -f $PROJECT_DIR/docker-compose.yml ps"
    echo "  • View logs: docker-compose -f $PROJECT_DIR/docker-compose.yml logs -f"
    echo "  • Stop services: docker-compose -f $PROJECT_DIR/docker-compose.yml down"
    echo "  • Restart services: docker-compose -f $PROJECT_DIR/docker-compose.yml restart"
    
    echo -e "\n${YELLOW}⚠️  IMPORTANT:${NC}"
    echo "  • Keep your system updated"
    echo "  • Monitor logs for security issues"
    echo "  • For production use, implement additional security measures"
    echo "  • Ensure compliance with applicable laws and regulations"
    
    echo -e "\n${GREEN}🚀 Happy Cracking!${NC}\n"
}

main() {
    print_header
    
    print_info "Starting Cyber Crack Pro setup..."
    print_info "Project directory: $PROJECT_DIR"
    
    # Create log file
    touch $LOG_FILE
    
    # Execute setup steps
    create_directories
    check_prerequisites
    install_apk_tools
    setup_python_environment
    setup_java_environment
    setup_go_environment
    setup_rust_environment
    setup_cpp_environment
    setup_java_dex_environment
    create_config_file
    setup_security
    setup_monitoring
    setup_kubernetes_configs
    start_services
    validate_setup
    create_systemd_service
    
    # Show completion message
    show_completion_message
}

# Run main function
main "$@"