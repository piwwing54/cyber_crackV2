#!/bin/bash
# Script untuk membuat keystore debug dan menginstal tools yang diperlukan

echo "🚀 Setting up Cyber Crack Pro APK signing..."

# Buat direktori .android jika belum ada
mkdir -p ~/.android

# Periksa apakah debug.keystore sudah ada
if [ ! -f ~/.android/debug.keystore ]; then
    echo "🔐 Creating debug keystore..."
    keytool -genkey -v \
        -keystore ~/.android/debug.keystore \
        -alias androiddebugkey \
        -storepass android \
        -keypass android \
        -keyalg RSA \
        -keysize 2048 \
        -validity 10000 \
        -dname "CN=Android Debug,O=Android,C=US"
    
    if [ $? -eq 0 ]; then
        echo "✅ Debug keystore created successfully"
    else
        echo "❌ Failed to create debug keystore"
        exit 1
    fi
else
    echo "✅ Debug keystore already exists"
fi

# Periksa apakah apksigner tersedia
if ! command -v apksigner &> /dev/null; then
    echo "📦 Installing Android build tools..."
    
    # Untuk Ubuntu/Debian
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y android-tools
    # Untuk Fedora/RHEL
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y android-tools
    # Untuk Arch Linux
    elif command -v pacman &> /dev/null; then
        sudo pacman -S android-tools
    else
        echo "⚠️  Could not automatically install Android tools"
        echo "💡 Please install Android SDK build-tools manually"
        echo "   For most systems: sudo apt install android-tools"
    fi
fi

# Periksa apakah zipalign tersedia
if ! command -v zipalign &> /dev/null; then
    echo "⚠️  zipalign not found, but it's needed for proper APK alignment"
    echo "💡  Please ensure Android build-tools are in your PATH"
fi

echo "✅ Setup completed! Your system should now be able to sign APKs properly."
echo ""
echo "📋 You can verify with:"
echo "   keytool -list -v -keystore ~/.android/debug.keystore -storepass android"
echo ""
echo "🔧 To test APK signing:"
echo "   apksigner sign --ks ~/.android/debug.keystore --ks-pass pass:android <your-apk-file>"