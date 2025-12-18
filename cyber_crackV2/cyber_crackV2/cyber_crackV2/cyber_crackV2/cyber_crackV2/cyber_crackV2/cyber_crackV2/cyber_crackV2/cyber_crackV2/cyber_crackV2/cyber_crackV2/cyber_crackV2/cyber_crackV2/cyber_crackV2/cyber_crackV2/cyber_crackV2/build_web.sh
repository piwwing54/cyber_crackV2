#!/bin/bash
# 🚀 Cyber Crack Pro Build Script
# Compiles the full-stack web interface with improved error handling

set -e

echo "🚀 Building Cyber Crack Pro Web Interface with improved error handling..."

# Navigate to project directory
cd /home/piwwing/bot-tele/cyber-crack-pro

# Clean previous build
echo "🧹 Cleaning previous build..."
rm -f cyber-crack-web

# Build the Go backend
echo "🔨 Building Go backend with timeout and error handling fixes..."
cd backend
go build -o ../cyber-crack-web main.go
cd ..

echo "✅ Go backend built successfully with improved timeout handling!"
echo "✅ Web Interface ready at http://localhost:8080"
echo "✅ Admin Dashboard at http://localhost:8080/admin"
echo "✅ API available at http://localhost:8080/api/*"
echo ""
echo "🔧 Fixed issues:"
echo "   - Added timeout handling to prevent processes from hanging"
echo "   - Added better error status reporting"
echo "   - Improved error handling for analysis, cracking and stability testing"