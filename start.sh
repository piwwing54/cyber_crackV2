#!/bin/bash
# Single command startup script for Cyber Crack Pro v3.0

echo "🚀 CYBER CRACK PRO v3.0 - SIMPLE STARTER"
echo "========================================"

# Check for NVIDIA support
if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU detected - using GPU-optimized configuration"
    DOCKERFILE_SUFFIX=""
else
    echo "💻 No NVIDIA GPU detected - using CPU-only configuration"
    DOCKERFILE_SUFFIX=".cpu"
fi

# Create uploads and results directories if they don't exist
mkdir -p uploads results

# Export environment variables
export TELEGRAM_BOT_TOKEN="8548539065:AAHLcyMQKHimwo1cLTuUKZl8OR1xngL_GeI"
export DEEPSEEK_API_KEY="YOUR_DEEPSEEK_API_KEY_HERE_OR_WEB_INTEGRATION"
export WORMGPT_API_KEY="YOUR_WORMGPT_API_KEY_HERE_OR_ENDPOINT_INTEGRATION"
export POSTGRES_PASSWORD="securepassword123"
export REDIS_PASSWORD="redis_secure_password"
export GRAFANA_ADMIN_PASSWORD="admin_secure_password"

echo "🔧 Starting Cyber Crack Pro with all services..."

# Run docker compose in background
if [ -f "docker-compose-full.yml" ]; then
    docker-compose -f docker-compose-full.yml up -d --build
else
    # Fallback to minimal config if full config doesn't exist
    docker-compose -f docker-compose-core.yml up -d --build
fi

echo "⏳ Waiting for services to start..."

# Wait for services to become available
sleep 30

# Check status
echo "📋 SYSTEM STATUS:"
docker-compose -f docker-compose-full.yml ps

echo ""
echo "🌐 ACCESS POINTS:"
echo "   • Web Dashboard: http://localhost:8000"
echo "   • Orchestrator API: http://localhost:5000"
echo "   • Python Bridge: http://localhost:8084"
echo "   • Monitoring: http://localhost:3001 (admin/admin)"
echo "   • Database: localhost:5432 (PostgreSQL), localhost:6379 (Redis)"

echo ""
echo "📱 Telegram Bot: @Yancumintybot"
echo ""
echo "🎉 CYBER CRACK PRO IS NOW RUNNING!"
echo "   Use: docker-compose -f docker-compose-full.yml logs for details"
echo "   Use: docker-compose -f docker-compose-full.yml down to stop"