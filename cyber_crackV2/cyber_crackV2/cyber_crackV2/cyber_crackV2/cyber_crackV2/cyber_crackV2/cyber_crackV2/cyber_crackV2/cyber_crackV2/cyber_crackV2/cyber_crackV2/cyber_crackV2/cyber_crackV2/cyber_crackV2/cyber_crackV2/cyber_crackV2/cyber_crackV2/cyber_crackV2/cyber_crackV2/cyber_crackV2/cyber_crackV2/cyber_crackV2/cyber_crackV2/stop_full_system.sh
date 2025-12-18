#!/bin/bash

# CYBER CRACK PRO - FULL SYSTEM SHUTDOWN SCRIPT
# This script stops all components of the Cyber Crack Pro system

echo "🛑 CYBER CRACK PRO - FULL SYSTEM SHUTDOWN"
echo "========================================"

# Kill all system processes
echo "🔄 Stopping Telegram Bot..."
pkill -f completed_bot_with_feedback.py
sleep 1

echo "🔄 Stopping Web Dashboard..."
pkill -f frontend/web_dashboard.py
sleep 1

echo "🔄 Stopping Orchestrator..."
pkill -f orchestrator/orchestrator.py
sleep 1

# Kill any remaining python processes that might be part of the system
pkill -f "python3.*orchestrator\|python3.*web_dashboard\|python3.*completed_bot\|python3.*master_coordinator"

echo "✅ All services stopped successfully!"
echo ""
echo "📝 LOG FILES SAVED:"
echo "   - bot.log"
echo "   - web_dashboard.log" 
echo "   - orchestrator.log"
echo ""
echo "💡 Use './start_full_system.sh' to restart the system"