#!/bin/bash
# 🚀 CYBER CRACK PRO v3.0 - SISTEM PENUH
# Skrip untuk menjalankan sistem lengkap Analysis-Before-Execution

set -e  # Exit on error

# Warna untuk output
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
# 🚀 CYBER CRACK PRO v3.0 - SISTEM LENGKAP
# Analysis Before Execution System - Two-Step Process
# ANALISIS → EKSEKUSI (Comprehensive APK Modification System)
################################################################################
${NC}"
}

# Fungsi untuk menghentikan proses yang sedang berjalan
stop_system() {
    print_info "Menghentikan sistem yang sedang berjalan..."
    
    # Matikan proses Python yang mungkin berjalan
    pids=$(pgrep -f "complete_telegram_bot\|simple_telegram_bot\|cyber_crack_pro")
    if [ ! -z "$pids" ]; then
        echo "$pids" | xargs kill -9 2>/dev/null || true
        print_status "Proses lama dihentikan"
    else
        print_info "Tidak ada proses aktif ditemukan"
    fi
}

# Fungsi untuk menjalankan sistem
start_system() {
    print_header
    
    # Cek apakah Python tersedia
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 tidak ditemukan!"
        exit 1
    fi
    
    print_status "Python3 ditemukan"
    
    # Cek apakah aiogram terinstal
    if python3 -c "import aiogram" &> /dev/null; then
        print_status "Aiogram ditemukan"
    else
        print_warning "Aiogram tidak ditemukan, menginstal..."
        pip3 install aiogram python-dotenv || {
            print_error "Gagal menginstal aiogram"
            exit 1
        }
        print_status "Aiogram berhasil diinstal"
    fi
    
    # Buat direktori yang diperlukan
    mkdir -p uploads results temp logs
    print_status "Direktori sistem dibuat"
    
    # Periksa apakah .env ada
    if [ ! -f ".env" ]; then
        print_warning "File .env tidak ditemukan, membuat contoh..."
        cat > .env << EOF
# 🤖 CYBER CRACK PRO v3.0 - Configuration
TELEGRAM_BOT_TOKEN=8548539065:AAHLcyMQKHimwo1cLTuUKZl8OR1xngL_GeI

# Optional configurations
REDIS_URL=redis://localhost:6379
POSTGRES_URL=postgresql://localhost:5432/cybercrack
UPLOAD_DIR=uploads/
RESULTS_DIR=results/
TEMP_DIR=temp/
MAX_WORKERS=10
UPLOAD_LIMIT_MB=100
LOG_LEVEL=INFO
EOF
        print_status "File .env contoh dibuat - PERBARUI DENGAN TOKEN ANDA!"
    fi
    
    # Baca bot token dari .env
    if [ -f ".env" ]; then
        # Gunakan grep dan sed untuk ekstrak token
        TELEGRAM_BOT_TOKEN=$(grep "^TELEGRAM_BOT_TOKEN=" .env | cut -d'=' -f2-)
    fi

    # Periksa bot token - hanya periksa apakah tidak kosong
    if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
        print_error "Bot token belum dikonfigurasi!"
        print_info "Edit file .env dan perbarui TELEGRAM_BOT_TOKEN dengan token Anda"
        print_info "Dapatkan token dari @BotFather di Telegram"
        exit 1
    fi

    # Periksa apakah token memiliki format yang valid (harus memiliki titik dua dan panjang tertentu)
    if [[ ! "$TELEGRAM_BOT_TOKEN" =~ ^[0-9]+:[A-Za-z0-9_-]+$ ]]; then
        print_error "Format bot token tidak valid!"
        print_info "Token harus dalam format: digit:alphanumeric_string"
        print_info "Dapatkan token dari @BotFather di Telegram"
        exit 1
    fi
    
    print_status "Token bot dikonfigurasi"
    
    # Cek apakah semua file sistem ada
    required_files=(
        "apk_analyzer.py"
        "injection_orchestrator.py" 
        "complete_telegram_bot.py"
        "cyber_crack_pro_system.py"
        "start_system.py"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "File $file tidak ditemukan!"
            exit 1
        fi
    done
    
    print_status "Semua file sistem ditemukan"
    
    # Tampilkan info sistem
    print_info ""
    print_info "${CYAN}🚀 CYBER CRACK PRO v3.0 - SISTEM AKTIF${NC}"
    print_info ""
    print_info "📁 Lokasi: $(pwd)"
    print_info "🤖 Bot: Active"
    print_info "📋 Modul Analisis: Available"
    print_info "🔧 Sistem Injeksi: Ready"
    print_info "📊 Pendekatan: Analysis Before Execution (Two-Step Process)"
    print_info ""
    print_info "🎯 FITUR SISTEM:"
    print_info "   • Analisis mendalam sebelum eksekusi"
    print_info "   • Pendekatan tiga tingkat: Basic/Standard/Advanced"
    print_info "   • Menu interaktif Telegram lengkap"
    print_info "   • Pembuatan laporan menyeluruh"
    print_info "   • Sistem fallback otomatis"
    print_info ""
    print_info "💡 Petunjuk: Kirim /start ke bot Anda di Telegram"
    print_info "⚠️  Gunakan hanya pada aplikasi yang Anda miliki"
    print_info ""
    
    # Jalankan bot dengan log
    print_info "🚀 Menjalankan sistem bot..."
    echo "[$(date)] Starting Cyber Crack Pro v3.0" >> logs/bot.log
    
    # Jalankan bot utama
    python3 complete_telegram_bot.py 2>&1 | tee -a logs/bot.log &
    
    BOT_PID=$!
    print_status "Bot berjalan dengan PID: $BOT_PID"
    
    # Tambahkan PID ke file untuk referensi
    echo $BOT_PID > bot.pid
    
    print_info ""
    print_info "${GREEN}🎉 SISTEM BERHASIL DIAKTIFKAN! 🎉${NC}"
    print_info ""
    print_info "🔗 Bot aktif dan siap menerima perintah di Telegram"
    print_info "📊 Sistem Analysis-Before-Execution: ACTIVE"
    print_info "🔄 Proses Dua-Langkah: ANALISIS → EKSEKUSI"
    print_info ""
}

# Fungsi untuk restart sistem
restart_system() {
    print_info "Restarting system..."
    stop_system
    sleep 2
    start_system
}

# Fungsi untuk status sistem
status_system() {
    if [ -f "bot.pid" ]; then
        PID=$(cat bot.pid)
        if ps -p $PID > /dev/null 2>&1; then
            print_status "Bot aktif (PID: $PID)"
            return 0
        else
            print_info "Bot tidak aktif (PID file ditemukan tetapi proses tidak berjalan)"
            return 1
        fi
    else
        print_info "Bot tidak aktif"
        return 1
    fi
}

# Fungsi untuk stop
stop_only() {
    stop_system
    if [ -f "bot.pid" ]; then
        rm bot.pid
    fi
    print_status "Sistem telah dimatikan"
}

# Main logic
case "${1:-start}" in
    start)
        if status_system; then
            print_warning "Sistem sudah berjalan!"
            echo "Gunakan 'stop' untuk menghentikan atau 'restart' untuk restart"
        else
            start_system
        fi
        ;;
    stop)
        stop_only
        ;;
    restart)
        restart_system
        ;;
    status)
        status_system
        ;;
    *)
        echo "Penggunaan: $0 {start|stop|restart|status}"
        echo "  start:   Jalankan sistem (default)"
        echo "  stop:    Hentikan sistem"
        echo "  restart: Restart sistem"
        echo "  status:  Cek status sistem"
        ;;
esac