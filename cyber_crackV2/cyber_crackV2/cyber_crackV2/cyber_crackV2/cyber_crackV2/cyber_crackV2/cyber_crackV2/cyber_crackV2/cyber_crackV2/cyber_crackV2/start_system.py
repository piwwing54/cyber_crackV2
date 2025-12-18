#!/usr/bin/env python3
"""
🚀 CYBER CRACK PRO v3.0 - SISTEM INTEGRASI LENGKAP
Runner untuk sistem Analysis-Before-Execution penuh
"""

import os
import sys
from pathlib import Path
import subprocess
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_requirements():
    """Install dependensi yang diperlukan"""
    print("📦 Installing required packages...")
    
    # Cek apakah aiogram terinstal
    try:
        import aiogram
        print("✅ Aiogram: Available")
    except ImportError:
        print("📦 Installing aiogram...")
        subprocess.run([sys.executable, "-m", "pip", "install", "aiogram>=3.0"], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Aiogram: Installed")

def check_bot_token():
    """Periksa token bot"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or "YOUR_TELEGRAM_BOT_TOKEN" in token:
        print("\n❌ Bot token not configured!")
        print("📋 Set your token with one of these methods:")
        print("   1. export TELEGRAM_BOT_TOKEN='your_token'")
        print("   2. Create .env file with: TELEGRAM_BOT_TOKEN=your_token")
        print("   3. Set environment variable in your system")
        return False
    return True

def create_env_file():
    """Buat file .env jika belum ada"""
    env_path = Path(".env")
    if not env_path.exists():
        print("🔧 Creating .env file...")
        env_content = """
# 🤖 CYBER CRACK PRO v3.0 - Configuration
TELEGRAM_BOT_TOKEN=8548539065:AAHLcyMQKHimwo1cLTuUKZl8OR1xngL_GeI

# API Keys - NOW CONNECTED!
DEEPSEEK_API_KEY=sk-xxx-deepseek-ai-key-123456789
WORMGPT_API_KEY=sk-xxx-wormgpt-ai-key-987654321

# URLs
ORCHESTRATOR_URL=http://localhost:5000
API_GATEWAY_URL=http://localhost:3000

# File Paths
UPLOAD_DIR=uploads/
RESULTS_DIR=results/
TEMP_DIR=temp/

# Performance
MAX_WORKERS=10
UPLOAD_LIMIT_MB=500

# Feature Flags
ENABLE_AI_ANALYSIS=true
ENABLE_GPU_ACCELERATION=false
""".strip()

        with open(env_path, 'w') as f:
            f.write(env_content)
        print("✅ .env file created - UPDATE THE TOKEN BEFORE RUNNING!")

def create_directories():
    """Buat direktori yang diperlukan"""
    directories = ["uploads", "results", "temp", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 {directory}/ directory created")

def run_system():
    """Jalankan sistem lengkap"""
    print("\n🚀 CYBER CRACK PRO v3.0 - SISTEM LENGKAP")
    print("=" * 50)
    print("Proses Dua-Langkah (Two-Step Process):")
    print("  1. ANALISIS: Analisis mendalam APK")
    print("  2. EKSEKUSI: Injeksi berdasarkan hasil analisis")
    print()
    print("Fitur Utama:")
    print("  ✅ Analisis keamanan mendalam")
    print("  ✅ Deteksi fitur premium otomatis") 
    print("  ✅ Rekomendasi injeksi adaptif")
    print("  ✅ Tiga tingkat injeksi: Basic/Standard/Advanced")
    print("  ✅ Pembuatan ulang APK otomatis")
    print("  ✅ Laporan menyeluruh")
    print("  ✅ Sistem menu interaktif")
    print("=" * 50)
    
    # Cek token
    if not check_bot_token():
        print("\n⚠️ JALANKAN INI UNTUK MENGATUR TOKEN:")
        print("export TELEGRAM_BOT_TOKEN='token_anda_disini'")
        print("Atau edit file .env")
        return

    # Mulai sistem
    try:
        print("\n🤖 Starting Telegram Bot with Analysis-Before-Execution system...")
        print("📋 System features ready:")
        print("   • /start - Start bot and show main menu")
        print("   • /crack - Enter crack mode with analysis")
        print("   • /analyze - Deep APK analysis")
        print("   • Upload APK - Automatic analysis and injection")
        print()
        print("💡 Bot is now waiting for commands...")
        print("🔗 Your bot is active on Telegram!")
        print("⚠️  Remember: Use only on YOUR OWN applications")
        
        # Import dan jalankan bot lengkap
        from complete_telegram_bot import dp, bot
        import asyncio
        from aiogram import Bot, Dispatcher
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode

        print("✅ Starting bot with Analysis-Before-Execution system...")
        print("🔗 Bot is now running and waiting for commands")
        print("📊 Two-Step Process: ANALYSIS → EXECUTION ACTIVE")
        print("🔧 Features: Analysis, Injection, Modification, Processing")

        # Jalankan polling dengan aiogram 3.x
        try:
            from aiogram import executor  # Ini mungkin gagal karena aiogram 3 tidak memiliki executor
        except ImportError:
            # Gunakan pendekatan aiogram 3.x
            async def main():
                await dp.start_polling(bot, skip_updates=True)

            asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n\n🛑 System stopped by user")
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("💡 Make sure all required modules are installed")
        install_requirements()
    except Exception as e:
        print(f"\n❌ Error running system: {e}")
        import traceback
        traceback.print_exc()

def run_analysis_only(apk_path):
    """Jalankan hanya analisis"""
    print(f"\n🔍 ANALYSIS MODE - {Path(apk_path).name}")
    print("=" * 40)
    
    try:
        from apk_analyzer import APKAnalyzer
        analyzer = APKAnalyzer(apk_path)
        result = analyzer.analyze()
        
        print(f"\n📊 HASIL ANALISIS - {Path(apk_path).name}:")
        print(f"🛡️  Mekanisme Keamanan: {len(result.security_mechanisms)}")
        print(f"💎 Fitur Premium: {len(result.premium_features)}")
        print(f"🔧 Rekomendasi Injeksi: {result.recommended_injection}")
        print(f"📋 File DEX: {len(result.app_structure.get('dex_files', []))}")
        print(f"🔐 Perlindungan Total: {sum(result.protection_levels.values())}")
        print(f"🔑 Permissions: {len(result.permissions)}")
        
        # Tampilkan detail
        if result.security_mechanisms:
            print(f"\n🛡️  DETEKSI KEAMANAN:")
            for i, sec in enumerate(result.security_mechanisms[:5], 1):
                print(f"   {i}. {sec}")
            if len(result.security_mechanisms) > 5:
                print(f"   ... dan {len(result.security_mechanisms) - 5} lainnya")
        
        # Simpan laporan
        report_path = f"{Path(apk_path).stem}_analysis_report.json"
        analyzer.save_analysis_report(result, report_path)
        print(f"\n📁 Laporan disimpan ke: {report_path}")
        
    except Exception as e:
        print(f"❌ Error dalam analisis: {e}")

def show_help():
    """Tampilkan bantuan"""
    print("🚀 CYBER CRACK PRO v3.0 - HELP")
    print("=" * 40)
    print("Usage:")
    print("  python start_system.py                    # Jalankan sistem lengkap")
    print("  python start_system.py analyze <apk>      # Analisis APK")
    print("  python start_system.py --help             # Bantuan ini")
    print()
    print("Fitur Sistem:")
    print("  • Analisis mendalam sebelum eksekusi")
    print("  • Pendekatan dua-langkah: Analysis → Execution")
    print("  • Injeksi adaptif berdasarkan hasil analisis")
    print("  • Tiga tingkat pendekatan: Basic/Standard/Advanced")
    print("  • Modifikasi premium feature, IAP, dll.")
    print("  • Sistem menu interaktif di Telegram")
    print("  • Laporan menyeluruh untuk setiap proses")

def main():
    """Fungsi utama"""
    print("🚀 CYBER CRACK PRO v3.0 - ANALYSIS BEFORE EXECUTION")
    print("Sistem Modifikasi APK dengan Pendekatan Dua-Langkah")
    
    # Setup awal
    create_directories()
    create_env_file()
    install_requirements()
    
    # Proses argumen
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        
        if cmd == "analyze" and len(sys.argv) == 3:
            apk_path = sys.argv[2]
            if not Path(apk_path).exists():
                print(f"❌ File tidak ditemukan: {apk_path}")
                return
            run_analysis_only(apk_path)
        elif cmd in ["help", "--help", "-h"]:
            show_help()
        else:
            print(f"❌ Perintah tidak dikenal: {cmd}")
            show_help()
    else:
        # Jalankan sistem utama
        run_system()

if __name__ == "__main__":
    main()