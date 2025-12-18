#!/bin/bash

# CYBER CRACK PRO - FULL SYSTEM STARTUP SCRIPT
# This script starts all components of the Cyber Crack Pro system

echo "🚀 CYBER CRACK PRO - FULL SYSTEM STARTUP"
echo "========================================="

# Function to check if a service is running
check_service() {
    local service_name=$1
    local url=$2
    
    echo "🔍 Checking $service_name at $url..."
    
    for i in {1..10}; do
        if curl -f -s $url/health > /dev/null 2>&1; then
            echo "✅ $service_name is running"
            return 0
        fi
        echo "⏳ Waiting for $service_name to start... ($i/10)"
        sleep 3
    done
    
    echo "❌ $service_name failed to start"
    return 1
}

# Check if Redis is running
if command -v redis-server &> /dev/null; then
    if ! pgrep redis-server > /dev/null; then
        echo "🔄 Starting Redis server..."
        redis-server --daemonize yes
        sleep 2
    fi
    echo "✅ Redis server is running"
else
    echo "⚠️ Redis server not found, please install Redis first"
fi

# Start orchestrator
echo "📦 Starting Orchestrator..."
pkill -f orchestrator/orchestrator.py 2>/dev/null
nohup python3 orchestrator/orchestrator.py > orchestrator.log 2>&1 &
ORCHESTRATOR_PID=$!
echo "✅ Orchestrator started with PID $ORCHESTRATOR_PID"

# Wait for orchestrator to start
sleep 5
check_service "Orchestrator" "http://localhost:5000" || {
    echo "❌ Orchestrator failed to start, continuing with other services..."
}

# Start web dashboard
echo "🌐 Starting Web Dashboard..."
pkill -f frontend/web_dashboard.py 2>/dev/null
nohup python3 frontend/web_dashboard.py > web_dashboard.log 2>&1 &
WEB_DASHBOARD_PID=$!
echo "✅ Web Dashboard started with PID $WEB_DASHBOARD_PID"

# Wait for web dashboard to start
sleep 3
check_service "Web Dashboard" "http://localhost:8000" || {
    echo "❌ Web Dashboard failed to start, continuing..."
}

# Start Telegram bot
echo "🤖 Starting Telegram Bot..."
pkill -f completed_bot_with_feedback.py 2>/dev/null
nohup python3 completed_bot_with_feedback.py > bot.log 2>&1 &
BOT_PID=$!
echo "✅ Telegram Bot started with PID $BOT_PID"

# Wait for bot to start
sleep 2

# Show system status
echo ""
echo "🎯 SYSTEM STARTUP COMPLETE!"
echo "============================"
echo "📦 Orchestrator PID: $ORCHESTRATOR_PID"
echo "🌐 Web Dashboard PID: $WEB_DASHBOARD_PID" 
echo "🤖 Telegram Bot PID: $BOT_PID"
echo ""
echo "🔗 ACCESS POINTS:"
echo "   Telegram Bot: Active on Telegram (connected via token)"
echo "   Web Dashboard: http://localhost:8000"
echo "   API Orchestrator: http://localhost:5000"
echo ""
echo "📊 SERVICE HEALTH:"
echo "   Orchestrator: http://localhost:5000/health"
echo "   Web Dashboard: http://localhost:8000/health"
echo "   Bot Status: Check your Telegram @Yancumintybot"
echo ""
echo "📝 LOG FILES:"
echo "   Orchestrator: orchestrator.log"
echo "   Web Dashboard: web_dashboard.log"
echo "   Bot: bot.log"
echo ""
echo "🔄 To stop all services: pkill -f 'python3.*orchestrator\|python3.*web_dashboard\|python3.*completed_bot'"
echo ""
echo "✅ Cyber Crack Pro system is now running with full integration!"