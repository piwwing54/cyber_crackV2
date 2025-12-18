#!/usr/bin/env powershell
# 🚀 CYBER CRACK PRO - Windows PowerShell Startup Script

Write-Host "🚀 CYBER CRACK PRO v3.0 - WINDOWS STARTUP SCRIPT" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Yellow

# Check prerequisites
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Cyan

# Check Docker
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "✅ Docker found: $(docker --version)" -ForegroundColor Green
} else {
    Write-Host "❌ Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check Python
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "✅ Python found: $(python --version)" -ForegroundColor Green
} else {
    Write-Host "❌ Python not found." -ForegroundColor Red
    exit 1
}

# Check Git
if (Get-Command git -ErrorAction SilentlyContinue) {
    Write-Host "✅ Git found: $(git --version)" -ForegroundColor Green
} else {
    Write-Host "❌ Git not found." -ForegroundColor Red
    exit 1
}

# Create project directories
Write-Host "📁 Creating project directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path "uploads" -Force
New-Item -ItemType Directory -Path "results" -Force  
New-Item -ItemType Directory -Path "models" -Force
New-Item -ItemType Directory -Path "patterns" -Force
New-Item -ItemType Directory -Path "logs" -Force
Write-Host "✅ Directories created" -ForegroundColor Green

# Check if .env exists, if not create it
if (-not (Test-Path ".env")) {
    Write-Host "📄 Creating .env file..." -ForegroundColor Cyan
    @"
# 🚀 Cyber Crack Pro Environment Variables
TELEGRAM_BOT_TOKEN=8548539065:AAHLcyMQKHimwo1cLTuUKZl8OR1xngL_GeI
DEEPSEEK_API_KEY=your_deepseek_api_key_here
WORMGPT_API_KEY=your_wormgpt_api_key_here
POSTGRES_DB=cybercrackpro
POSTGRES_USER=cracker
POSTGRES_PASSWORD=securepassword123
REDIS_URL=redis://localhost:6379
ORCHESTRATOR_URL=http://localhost:5000
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ .env file created" -ForegroundColor Green
}

# Start the services
Write-Host "🔌 Starting Cyber Crack Pro services..." -ForegroundColor Cyan

# Build services
Write-Host "🔨 Building Docker services..." -ForegroundColor Yellow
docker-compose build --parallel

# Start services
Write-Host "🚀 Starting services..." -ForegroundColor Yellow
docker-compose up -d --scale go-analyzer=2 --scale rust-cracker=2 --scale cpp-breaker=1

# Wait for services to start
Write-Host "⏳ Waiting for services to initialize (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check service status
Write-Host "📊 Checking service status..." -ForegroundColor Cyan
docker-compose ps

# Test API connections
Write-Host "🌐 Testing API connectivity..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get
    Write-Host "✅ Orchestrator: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Orchestrator not responding" -ForegroundColor Red
}

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8080/health" -Method Get
    Write-Host "✅ Go Analyzer: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Go Analyzer not responding" -ForegroundColor Red
}

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8081/health" -Method Get
    Write-Host "✅ Rust Cracker: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Rust Cracker not responding" -ForegroundColor Red
}

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000" -Method Get
    Write-Host "✅ Web Dashboard accessible" -ForegroundColor Green
} catch {
    Write-Host "❌ Web Dashboard not responding" -ForegroundColor Red
}

Write-Host "" -ForegroundColor White
Write-Host "🎉 CYBER CRACK PRO v3.0 IS NOW RUNNING!" -ForegroundColor Magenta
Write-Host "=========================================" -ForegroundColor Magenta

Write-Host "" -ForegroundColor White
Write-Host "🎯 Access Points:" -ForegroundColor Yellow
Write-Host "   Web Dashboard: http://localhost:8000" -ForegroundColor White
Write-Host "   API Gateway: http://localhost:3000" -ForegroundColor White  
Write-Host "   Orchestrator: http://localhost:5000" -ForegroundColor White
Write-Host "   Telegram Bot: Configure your bot token in .env" -ForegroundColor White
Write-Host "" -ForegroundColor White

Write-Host "⚙️ Management Commands:" -ForegroundColor Yellow
Write-Host "   View logs: docker-compose logs -f" -ForegroundColor White
Write-Host "   Stop services: docker-compose down" -ForegroundColor White
Write-Host "   Restart: docker-compose restart" -ForegroundColor White
Write-Host "   Status: docker-compose ps" -ForegroundColor White
Write-Host "" -ForegroundColor White

Write-Host "🚀 System is ready for APK cracking operations!" -ForegroundColor Green
Write-Host "   Upload APK files to get started!" -ForegroundColor Green