#!/usr/bin/env python3
"""
🚀 CYBER CRACK PRO v3.0 - SISTEM UTAMA PENUH
Runner utama yang menggabungkan semua komponen sistem
"""

import os
import sys
import asyncio
from pathlib import Path
import subprocess

def setup_environment():
    """Setup lingkungan dan direktori yang diperlukan"""
    print("🔧 Setting up environment...")
    
    # Buat direktori yang diperlukan
    directories = ["uploads", "results", "temp", "logs", "config"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    # Cek apakah semua modul yang diperlukan tersedia
    try:
        import aiogram
        print("✅ Aiogram: Available")
    except ImportError:
        print("❌ Aiogram: Not installed. Install with: pip install aiogram")
        return False
    
    try:
        import apk_analyzer
        print("✅ APK Analyzer: Available")
    except ImportError:
        print("⚠️ APK Analyzer: Not available in current location")
    
    try:
        import injection_orchestrator
        print("✅ Injection Orchestrator: Available")
    except ImportError:
        print("⚠️ Injection Orchestrator: Not available in current location")
    
    return True

def check_bot_token():
    """Periksa apakah bot token sudah disetel"""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    if not token or "YOUR_TELEGRAM_BOT_TOKEN" in token:
        print("\n❌ TELEGRAM_BOT_TOKEN not configured!")
        print("📋 Please set your Telegram bot token:")
        print("   Linux/Mac: export TELEGRAM_BOT_TOKEN='your_bot_token'")
        print("   Windows: set TELEGRAM_BOT_TOKEN=your_bot_token")
        print("   Or add to .env file: TELEGRAM_BOT_TOKEN=your_bot_token")
        return False
    
    print(f"✅ Bot token configured: {'Yes' if token else 'No'}")
    return True

def run_system_mode():
    """Jalankan sistem dalam mode lengkap"""
    print("\n🚀 Running Cyber Crack Pro v3.0 - Full System Mode")
    print("=" * 60)
    
    if not setup_environment():
        print("❌ Environment setup failed!")
        return
    
    if not check_bot_token():
        print("❌ Please configure your bot token before running!")
        return
    
    try:
        from complete_telegram_bot import main as run_bot
        print("🤖 Starting Telegram Bot with Analysis-Before-Execution system...")
        print("📋 Features available:")
        print("   • Comprehensive APK analysis")
        print("   • Adaptive injection methods") 
        print("   • Two-step process: Analysis → Execution")
        print("   • Multiple security bypass techniques")
        print("   • Premium feature unlocking")
        print("   • IAP bypass")
        print("   • Root detection bypass")
        print("   • Certificate pinning bypass")
        print()
        print("💡 Bot is now ready to receive commands")
        print("🔗 Connect to your bot on Telegram and send /start")
        
        # Jalankan bot
        asyncio.run(run_bot())
        
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        print("\n📋 Required modules:")
        print("   pip install aiogram python-dotenv")
        
    except Exception as e:
        print(f"❌ Error running system: {e}")
        import traceback
        traceback.print_exc()

def run_analysis_mode(apk_path):
    """Jalankan hanya mode analisis"""
    print(f"\n🔍 Running Analysis Mode for: {Path(apk_path).name}")
    
    try:
        from apk_analyzer import APKAnalyzer
        analyzer = APKAnalyzer(apk_path)
        result = analyzer.analyze()
        
        print(f"\n📊 ANALYSIS RESULTS FOR: {Path(apk_path).name}")
        print(f"🛡️ Security Mechanisms: {len(result.security_mechanisms)}")
        print(f"💎 Premium Features: {len(result.premium_features)}")
        print(f"🔧 Recommended Injection: {result.recommended_injection}")
        print(f"📋 DEX Files: {len(result.app_structure.get('dex_files', []))}")
        print(f"🔐 Protection Levels: {sum(result.protection_levels.values())}")
        print(f"🔑 Permissions: {len(result.permissions)}")
        
        # Tampilkan detail keamanan
        if result.security_mechanisms:
            print(f"\n🛡️ SECURITY MECHANISMS DETECTED:")
            for sec in result.security_mechanisms:
                print(f"   • {sec}")
        
        # Tampilkan detail fitur premium
        if result.premium_features:
            print(f"\n💎 PREMIUM FEATURES FOUND:")
            for feature in result.premium_features:
                print(f"   • {feature}")
        
        # Simpan laporan
        report_path = f"{Path(apk_path).stem}_analysis_report.json"
        analyzer.save_analysis_report(result, report_path)
        print(f"\n📁 Analysis report saved to: {report_path}")
        
    except Exception as e:
        print(f"❌ Error in analysis mode: {e}")

def run_injection_mode(apk_path):
    """Jalankan mode analisis dan injeksi penuh"""
    print(f"\n🔧 Running Analysis + Injection Mode for: {Path(apk_path).name}")
    
    try:
        from cyber_crack_pro_system import CyberCrackProSystem
        system = CyberCrackProSystem()
        
        print("🔍 Step 1: Comprehensive analysis...")
        print("🚀 Step 2: Adaptive injection execution...")
        print("📦 Step 3: APK rebuild...")
        print()
        
        result = asyncio.run(system.process_apk(apk_path))
        
        print(f"\n🎯 PROCESSING RESULTS:")
        print(f"✅ Success: {result.success}")
        print(f"📱 Original: {Path(result.original_apk).name}")
        if result.modified_apk:
            print(f"📦 Modified: {result.modified_apk}")
        print(f"⏰ Processing Time: {result.processing_time:.2f} seconds")
        
        if result.analysis:
            print(f"\n🔍 ANALYSIS RESULTS:")
            print(f"🛡️ Security Mechanisms: {len(result.analysis.security_mechanisms)}")
            print(f"💎 Premium Features: {len(result.analysis.premium_features)}")
            print(f"🔧 Recommended Injection: {result.analysis.recommended_injection}")
        
        if result.injection:
            print(f"\n🔧 INJECTION RESULTS:")
            print(f"🔧 Injection Type: {result.injection.injection_type}")
            print(f"📝 Changes Applied: {len(result.injection.changes_applied)}")
            
            print(f"\n📋 CHANGES APPLIED:")
            for i, change in enumerate(result.injection.changes_applied[:10], 1):  # Tampilkan 10 pertama
                print(f"   {i}. {change}")
            
            if len(result.injection.changes_applied) > 10:
                print(f"   ... and {len(result.injection.changes_applied) - 10} more changes")
                
    except Exception as e:
        print(f"❌ Error in injection mode: {e}")
        import traceback
        traceback.print_exc()

def show_help():
    """Tampilkan bantuan"""
    print("🚀 CYBER CRACK PRO v3.0 - HELP")
    print("=" * 40)
    print("Usage:")
    print("  python cyber_crack_pro.py full          # Run full system (Telegram bot)")
    print("  python cyber_crack_pro.py analyze <apk> # Analyze APK")
    print("  python cyber_crack_pro.py process <apk> # Analyze + Inject + Build")
    print("  python cyber_crack_pro.py help          # Show this help")
    print()
    print("Features:")
    print("  • Comprehensive APK analysis")
    print("  • Adaptive injection methods")
    print("  • Two-step process: Analysis → Execution")
    print("  • Security bypass techniques")
    print("  • Premium feature unlocking")
    print("  • IAP bypass")
    print("  • Certificate pinning bypass")
    print("  • Root detection bypass")

def main():
    """Fungsi utama"""
    print("🚀 CYBER CRACK PRO v3.0 - INTEGRATED SYSTEM")
    print("Analysis → Execution (Two-Step Process)")
    print()
    
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "full":
        run_system_mode()
    elif command == "analyze" and len(sys.argv) == 3:
        apk_path = sys.argv[2]
        if not Path(apk_path).exists():
            print(f"❌ APK file not found: {apk_path}")
            return
        run_analysis_mode(apk_path)
    elif command == "process" and len(sys.argv) == 3:
        apk_path = sys.argv[2]
        if not Path(apk_path).exists():
            print(f"❌ APK file not found: {apk_path}")
            return
        run_injection_mode(apk_path)
    elif command == "help" or command in ["-h", "--help"]:
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()