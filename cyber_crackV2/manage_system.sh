#!/bin/bash
# 🚀 CYBER CRACK PRO v3.0 - ALL-IN-ONE BACKGROUND STARTER
# Menjalankan semua server dalam mode background tanpa mati

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
###############################################################################
# 🚀 CYBER CRACK PRO v3.0 - ALL SERVICES STARTER
# Running ALL servers in background: API + BOT + DASHBOARD
###############################################################################
${NC}"
}

# Fungsi untuk menghentikan semua proses yang sedang berjalan
stop_all_services() {
    print_warning "Stopping all background services..."
    pkill -f "uvicorn.*backend_api\|python.*complete_telegram_bot\|python.*web_dashboard" 2>/dev/null || true
    sleep 2
    # Cek apakah masih ada proses yang berjalan
    if pgrep -f "uvicorn.*backend_api\|python.*complete_telegram_bot\|python.*web_dashboard" > /dev/null; then
        pkill -9 -f "uvicorn.*backend_api\|python.*complete_telegram_bot\|python.*web_dashboard" 2>/dev/null || true
        print_status "Force killed remaining processes"
    fi
    print_status "All services stopped"
}

# Fungsi untuk mengecek apakah layanan berjalan
check_services() {
    print_info "Checking service status..."
    
    if pgrep -f "uvicorn.*:app.*--port 8001" > /dev/null; then
        print_status "Backend API Server: Running (Port 8001)"
    else
        print_error "Backend API Server: Not running"
    fi
    
    if pgrep -f "uvicorn.*web_dashboard:app" > /dev/null; then
        print_status "Web Dashboard: Running (Port 8000)"
    else
        print_error "Web Dashboard: Not running"
    fi
    
    if pgrep -f "complete_telegram_bot\|bot.*polling" > /dev/null; then
        print_status "Telegram Bot: Running"
    else
        print_error "Telegram Bot: Not running"
    fi
}

# Main execution
case "${1:-start}" in
    start)
        print_header
        
        # Stop semua proses lama dulu
        stop_all_services
        
        print_info "Starting all services in background..."
        
        # Buat direktori yang diperlukan
        mkdir -p uploads results logs temp
        
        # Jalankan BACKEND API SERVER di background
        print_info "Starting Backend API Server on port 8001..."
        nohup python -u backend_api.py > logs/backend_api.log 2>&1 &
        BACKEND_PID=$!
        echo $BACKEND_PID > backend_api.pid
        print_status "Backend API Server started with PID: $BACKEND_PID"

        # Tunggu sebentar agar backend siap
        sleep 3

        # Jalankan WEB DASHBOARD di background
        print_info "Starting Web Dashboard on port 8000..."
        nohup python -c "
import sys
sys.path.append('.')
import uvicorn
from web_dashboard import app

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')
" > logs/web_dashboard.log 2>&1 &
        DASHBOARD_PID=$!
        echo $DASHBOARD_PID > web_dashboard.pid
        print_status "Web Dashboard started with PID: $DASHBOARD_PID"

        # Tunggu sebentar agar dashboard siap
        sleep 2

        # Jalankan TELEGRAM BOT di background
        print_info "Starting Telegram Bot..."
        nohup python -u complete_telegram_bot.py > logs/bot.log 2>&1 &
        BOT_PID=$!
        echo $BOT_PID > bot.pid
        print_status "Telegram Bot started with PID: $BOT_PID"
        
        # Tunggu sebentar agar bot siap
        sleep 3
        
        print_info ""
        print_info "${GREEN}🎉 ALL SERVICES STARTED SUCCESSFULLY! 🎉${NC}"
        print_info ""
        print_info "🔗 Services running in background:"
        print_info "   • Backend API: http://localhost:8001"
        print_info "   • Web Dashboard: http://localhost:8000"
        print_info "   • Telegram Bot: Active on your bot channel"
        print_info ""
        print_info "📊 Access your admin dashboard at: http://localhost:8000"
        print_info "🤖 Send /start to your bot on Telegram to begin"
        print_info ""
        print_info "💡 Services will continue running in background even after terminal closes"
        print_info "🔧 Use './manage_system.sh status' to check service status"
        print_info "🔄 Use './manage_system.sh stop' to stop all services"
        ;;
        
    stop)
        print_header
        stop_all_services
        ;;
        
    restart)
        print_header
        stop_all_services
        sleep 3
        $0 start  # Jalankan kembali dengan command start
        ;;
        
    status)
        print_header
        check_services
        ;;
        
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        echo "  start:   Start all services in background"
        echo "  stop:    Stop all services" 
        echo "  restart: Restart all services"
        echo "  status:  Check status of all services"
        ;;
esac

print_info ""
print_info "${CYAN}CYBER CRACK PRO v3.0 - ALL SERVICES MANAGER${NC}"