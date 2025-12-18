#!/bin/bash
# Script untuk kompilasi ulang modul Java DEX

echo "🔨 Compiling Java DEX Engine with updated signing functionality..."

cd /home/piwwing/bot-tele/cyber-crack-pro/core/java-dex

# Pastikan Maven tersedia
if ! command -v mvn &> /dev/null; then
    echo "❌ Maven not found. Installing Maven..."
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y maven
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y maven
    elif command -v pacman &> /dev/null; then
        sudo pacman -S maven
    else
        echo "❌ Cannot auto-install Maven. Please install it manually."
        exit 1
    fi
fi

# Pastikan Java tersedia
if ! command -v java &> /dev/null; then
    echo "❌ Java not found. Installing OpenJDK..."
    if command -v apt &> /dev/null; then
        sudo apt install -y openjdk-11-jdk
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y java-11-openjdk-devel
    elif command -v pacman &> /dev/null; then
        sudo pacman -S openjdk11
    else
        echo "❌ Cannot auto-install Java. Please install OpenJDK 11 manually."
        exit 1
    fi
    export JAVA_HOME=/usr/lib/jvm/java-11-openjdk
fi

# Compile dan package dengan Maven
echo "📦 Building Java DEX Engine..."
mvn clean package -DskipTests

if [ $? -eq 0 ]; then
    echo "✅ Java DEX Engine built successfully!"
    echo "✅ New JAR file created in target/ directory"
    
    # Update executable binary
    cp target/java-dex-3.0.0.jar cyber-crack-web
    chmod +x cyber-crack-web
    
    echo "✅ Updated the cyber-crack-web binary with new functionality"
else
    echo "❌ Build failed. Please check the error messages above."
    exit 1
fi