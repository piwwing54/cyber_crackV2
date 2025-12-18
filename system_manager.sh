#!/bin/bash

# CYBER CRACK PRO - SYSTEM MANAGEMENT SCRIPT
# Use this script to manage the complete Cyber Crack Pro system

set -e  # Exit on any error

show_help() {
    echo "🤖 CYBER CRACK PRO - SYSTEM MANAGEMENT"
    echo "====================================="
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start    - Start the complete system"
    echo "  stop     - Stop the complete system"
    echo "  restart  - Restart the complete system"
    echo "  status   - Show system status"
    echo "  logs     - Show all system logs"
    echo "  logs-orchestrator - Show orchestrator logs"
    echo "  logs-web        - Show web dashboard logs"
    echo "  logs-bot        - Show telegram bot logs"
    echo "  logs-redis      - Show redis logs"
    echo "  health   - Check system health"
    echo "  help     - Show this help message"
    echo ""
}

start_system() {
    echo "🚀 Starting Cyber Crack Pro system..."
    docker-compose up -d
    echo "✅ System started! Services will be available shortly."
    echo "📊 Checking status in 30 seconds..."
    sleep 30
    docker-compose ps
}

stop_system() {
    echo "🛑 Stopping Cyber Crack Pro system..."
    docker-compose down
    echo "✅ System stopped!"
}

restart_system() {
    echo "🔄 Restarting Cyber Crack Pro system..."
    docker-compose down
    sleep 5
    docker-compose up -d
    echo "✅ System restarted! Services will be available shortly."
    echo "📊 Checking status in 30 seconds..."
    sleep 30
    docker-compose ps
}

show_status() {
    echo "📊 Cyber Crack Pro System Status:"
    echo "================================="
    docker-compose ps
}

show_logs() {
    echo "📝 All System Logs:"
    echo "=================="
    docker-compose logs
}

show_orchestrator_logs() {
    echo "🤖 Orchestrator Logs:"
    echo "===================="
    docker-compose logs orchestrator
}

show_web_logs() {
    echo "🌐 Web Dashboard Logs:"
    echo "======================"
    docker-compose logs web-dashboard
}

show_bot_logs() {
    echo "🤖 Telegram Bot Logs:"
    echo "====================="
    docker-compose logs telegram-bot
}

show_redis_logs() {
    echo "💾 Redis Logs:"
    echo "=============="
    docker-compose logs redis
}

check_health() {
    echo "🏥 Cyber Crack Pro Health Check:"
    echo "==============================="
    
    echo "Checking Orchestrator: "
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        echo "✅ Orchestrator: Healthy"
        curl -s http://localhost:5000/health | python3 -m json.tool
    else
        echo "❌ Orchestrator: Not responding"
    fi
    
    echo ""
    echo "Checking Web Dashboard: "
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Web Dashboard: Healthy"
        curl -s http://localhost:8000/health | python3 -m json.tool
    else
        echo "❌ Web Dashboard: Not responding (may need more time to start)"
    fi
    
    echo ""
    echo "Container Status:"
    docker-compose ps
}

case "$1" in
    start)
        start_system
        ;;
    stop)
        stop_system
        ;;
    restart)
        restart_system
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    "logs-orchestrator")
        show_orchestrator_logs
        ;;
    "logs-web")
        show_web_logs
        ;;
    "logs-bot")
        show_bot_logs
        ;;
    "logs-redis")
        show_redis_logs
        ;;
    health)
        check_health
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        exit 1
        ;;
esac