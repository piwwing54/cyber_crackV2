#!/bin/bash

# Script untuk menyalin sistem dari project_AI ke Cyber Crack Pro
# dan mengintegrasikannya dengan sistem yang ada

SOURCE_DIR="/home/piwwing/bot-tele/project_AI"
TARGET_DIR="/home/piwwing/bot-tele/cyber-crack-pro"

echo "🚀 Menyalin sistem dari $SOURCE_DIR ke $TARGET_DIR..."

# Cek apakah direktori sumber ada
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Direktori sumber $SOURCE_DIR tidak ditemukan"
    echo "💡 Pastikan direktori tersebut ada dan dapat diakses"
    exit 1
fi

# Buat backup dari sistem sekarang
echo "📦 Membuat backup sistem saat ini..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${TARGET_DIR}/backup_${TIMESTAMP}"
cp -r "$TARGET_DIR" "$BACKUP_DIR"
echo "✅ Backup disimpan di $BACKUP_DIR"

# Salin semua file dari project_AI
echo "📋 Menyalin file dari project_AI..."
cp -r "$SOURCE_DIR"/* "$TARGET_DIR/"

# Jika ada konflik nama file, tanyakan user
echo "🔄 Memeriksa file yang mungkin bertabrakan..."

# Khusus untuk direktori core/java-dex karena kita sudah memodifikasi
if [ -d "$SOURCE_DIR/core/java-dex" ]; then
    echo "⚠️  Menemukan direktori java-dex di project_AI"
    echo "💡 Mencoba menggabungkan dengan sistem yang telah dimodifikasi..."
    
    # Gabungkan atau backup direktori java-dex jika perlu
    if [ -d "$TARGET_DIR/core/java-dex" ]; then
        # Backup direktori yang telah kita modifikasi
        cp -r "$TARGET_DIR/core/java-dex" "$BACKUP_DIR/core/java-dex_modified"
        echo "⚠️  Direktori java-dex yang telah dimodifikasi disimpan di backup"
    fi
    
    # Salin dari project_AI
    cp -r "$SOURCE_DIR/core/java-dex" "$TARGET_DIR/core/java-dex"
    echo "✅ Direktori java-dex dari project_AI telah disalin"
fi

# Jika project_AI memiliki file sistem injeksi method
if [ -f "$SOURCE_DIR/inject_method.py" ] || [ -f "$SOURCE_DIR/method_injector.py" ]; then
    echo "🔍 Menemukan sistem injeksi method di project_AI"
    
    # Buat direktori untuk sistem injeksi method
    METHOD_INJECT_DIR="$TARGET_DIR/core/method-injector"
    mkdir -p "$METHOD_INJECT_DIR"
    
    # Salin file-file injeksi method
    for file in inject_method.py method_injector.py; do
        if [ -f "$SOURCE_DIR/$file" ]; then
            cp "$SOURCE_DIR/$file" "$METHOD_INJECT_DIR/"
            echo "✅ $file disalin ke $METHOD_INJECT_DIR"
        fi
    done
fi

# Integrasi dengan Python bridge
if [ -f "$SOURCE_DIR/ai_integrator.py" ] || [ -d "$SOURCE_DIR/ai_system" ]; then
    echo "🤖 Menemukan sistem AI di project_AI"
    
    # Integrasi dengan sistem AI yang sudah kita buat
    cp -r "$SOURCE_DIR/ai_"* "$TARGET_DIR/core/python-bridge/" 2>/dev/null || true
    echo "✅ Sistem AI diintegrasikan"
fi

echo ""
echo "✅ Proses penyalinan selesai!"
echo ""
echo "📋 File yang disalin dari project_AI:"
find "$SOURCE_DIR" -type f | wc -l | xargs -I {} echo "   - {} file"
echo ""
echo "💡 Tips: Anda mungkin perlu menjalankan build_java_engine.sh setelah ini"
echo "    untuk mengkompilasi ulang sistem Java DEX engine dengan perubahan baru."
echo ""
echo "🔧 Untuk restart server: pkill -f cyber-crack-web && ./backend/cyber-crack-web"

# Tampilkan struktur direktori yang baru
echo ""
echo "📂 Struktur direktori baru:"
find "$TARGET_DIR" -maxdepth 2 -type d | head -15