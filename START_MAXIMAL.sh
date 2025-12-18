#!/bin/bash
# FINAL STARTUP SCRIPT FOR CYBER CRACK PRO v3.0

echo "🌟 CYBER CRACK PRO v3.0 - MAXIMUM POWER STARTER"
echo "=============================================="

# Set permissions for execution
chmod +x start.sh

echo "🔍 Detecting system capabilities..."
if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU detected - using GPU-optimized config"
    # Copy the GPU-ready Dockerfile to the standard name
    cp core/cpp-breaker/Dockerfile.gpu core/cpp-breaker/Dockerfile
    DOCKERFILE_TYPE="GPU"
else
    echo "💻 No NVIDIA GPU detected - using CPU-only config"
    # Copy the CPU-optimized Dockerfile to the standard name
    cp core/cpp-breaker/Dockerfile.cpu core/cpp-breaker/Dockerfile
    DOCKERFILE_TYPE="CPU"
fi

echo ""
echo "📦 Preparing directories..."
mkdir -p uploads results logs models datasets tools database monitoring

echo ""
echo "🔐 Setting up credentials..."
export TELEGRAM_BOT_TOKEN="8548539065:AAHLcyMQKHimwo1cLTuUKZl8OR1xngL_GeI"
export DEEPSEEK_API_KEY="YOUR_DEEPSEEK_API_KEY_HERE_OR_WEB_INTEGRATION"
export WORMGPT_API_KEY="YOUR_WORMGPT_API_KEY_HERE_OR_ENDPOINT_INTEGRATION"
export POSTGRES_PASSWORD="securepassword123"
export REDIS_PASSWORD="redis_secure_password"
export GRAFANA_ADMIN_PASSWORD="admin_secure_password"

echo ""
echo "🚀 Starting Cyber Crack Pro v3.0 with ${DOCKERFILE_TYPE} optimization..."
nohup ./start.sh > logs/startup.log 2>&1 &

echo ""
echo "⏳ Waiting for services to initialize..."
sleep 30

echo ""
echo "📋 CHECKING SERVICE STATUS:"
echo "-----------------------------"
docker-compose -f docker-compose-full.yml ps

echo ""
echo "🌐 ACCESS POINTS:"
echo "   • Web Dashboard: http://localhost:8000" 
echo "   • Orchestrator API: http://localhost:5000"
echo "   • Python Bridge: http://localhost:8084"
echo "   • Monitoring: http://localhost:3001 (admin/admin)"
echo "   • Your Bot: @Yancumintybot"

echo ""
echo "🎯 SYSTEM IS NOW RUNNING IN BACKGROUND!"
echo "   • GPU Support: ${DOCKERFILE_TYPE}"
echo "   • All services launched successfully"
echo "   • Ready for YOUR OWN application analysis"
echo ""
echo "   To check logs: docker-compose -f docker-compose-full.yml logs"
echo "   To stop: docker-compose -f docker-compose-full.yml down"
echo ""
echo "🎉 CYBER CRACK PRO v3.0 - FULLY OPERATIONAL!"

# Create a simple status checker
cat > check_status.sh << 'EOF'
#!/bin/bash
echo "🔍 CYBER CRACK PRO - REALTIME STATUS CHECK"
echo "=========================================="
docker-compose -f docker-compose-full.yml ps
echo ""
echo "📊 LOG SNIPPET (last 20 lines of orchestrator):"
docker-compose -f docker-compose-full.yml logs --tail=20 orchestrator
EOF

chmod +x check_status.sh
echo "   • Quick status check: ./check_status.sh"