#!/usr/bin/env python3
"""
🚀 CYBER CRACK PRO v3.0 - SYSTEM SETUP
Setup script untuk inisialisasi sistem dan verifikasi dependencies
"""

import os
import sys
import subprocess
from pathlib import Path
import importlib.util

def check_python_version():
    """Periksa versi Python"""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} - OK")
    return True

def check_core_dependencies():
    """Periksa dependencies utama"""
    dependencies = [
        ("aiogram", "aiogram"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("androguard", "androguard"),
        ("torch", "torch"),
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("redis", "redis.asyncio"),
        ("aiohttp", "aiohttp"),
        ("pydantic", "pydantic"),
    ]
    
    print("\n🔍 Checking core dependencies...")
    missing_deps = []
    
    for display_name, import_name in dependencies:
        try:
            if "." in import_name:
                # Handle submodules like redis.asyncio
                parts = import_name.split(".")
                mod = importlib.import_module(parts[0])
                for part in parts[1:]:
                    mod = getattr(mod, part)
            else:
                importlib.import_module(import_name)
            print(f"✅ {display_name}")
        except ImportError:
            print(f"❌ {display_name}")
            missing_deps.append(display_name)
    
    if missing_deps:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
        print("💡 Install with: pip install -r requirements_fixed.txt")
        return False
    else:
        print("\n✅ All core dependencies are available")
        return True

def check_system_tools():
    """Periksa tools sistem"""
    print("\n🔍 Checking system tools...")
    tools = [
        ("java", ["--version"]),
        ("adb", ["--version"]),
        ("apktool", ["--version"]),
        ("jadx", ["--version"])
    ]
    missing_tools = []

    for tool, args in tools:
        try:
            # Coba beberapa varian perintah untuk mendapatkan versi
            possible_args = [args, ["-v"], ["-V"], ["--help"]]

            found = False
            for cmd_args in possible_args:
                try:
                    result = subprocess.run([tool] + cmd_args,
                                           capture_output=True,
                                           text=True,
                                           timeout=5)
                    if result.returncode == 0 or "version" in result.stdout.lower() or "version" in result.stderr.lower():
                        print(f"✅ {tool}")
                        found = True
                        break
                except:
                    continue

            if not found:
                missing_tools.append(tool)
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubProcessError):
            missing_tools.append(tool)

    if missing_tools:
        print(f"⚠️  Missing system tools: {', '.join(missing_tools)}")
        print("💡 Install missing tools manually or use arch_installer.sh")
    else:
        print("✅ All system tools are available")

    return len(missing_tools) == 0

def create_directories():
    """Buat direktori yang dibutuhkan"""
    dirs = ["uploads", "results", "temp", "logs", "models", "tools"]
    print("\n🔍 Creating required directories...")
    
    for directory in dirs:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 {directory}/")
    
    print("✅ Directories created")

def check_dotenv():
    """Periksa file .env"""
    print("\n🔍 Checking .env configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("💡 Creating example .env file...")
        create_example_env()
        return False
    else:
        print("✅ .env file exists")
        return True

def create_example_env():
    """Buat contoh file .env"""
    env_content = """# 🤖 CYBER CRACK PRO v3.0 - Configuration
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
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("📄 Example .env file created")
    print("⚠️  UPDATE THE VALUES WITH YOUR ACTUAL CONFIGURATION!")

def run_compatibility_check():
    """Jalankan kompatibilitas check penuh"""
    print("\n🎯 Running full compatibility check...")
    
    results = []
    results.append(("Python Version", check_python_version()))
    results.append(("Core Dependencies", check_core_dependencies()))
    results.append(("System Tools", check_system_tools()))
    results.append(("Environment", check_dotenv()))
    
    print("\n📊 COMPATIBILITY CHECK RESULTS:")
    print("-" * 40)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:<20} {status}")
        if not passed:
            all_passed = False
    
    print("-" * 40)
    if all_passed:
        print("\n🎉 ALL CHECKS PASSED! System ready to use.")
        print("🚀 Run: ./run_system.sh start")
        return True
    else:
        print("\n⚠️  SOME CHECKS FAILED! Please install missing components.")
        print("🔧 Run: bash install_dependencies.sh")
        return False

def main():
    """Fungsi utama setup"""
    print("🚀 CYBER CRACK PRO v3.0 - SYSTEM SETUP")
    print("=" * 50)
    
    success = run_compatibility_check()
    
    if success:
        print("\n✅ Cyber Crack Pro v3.0 installation is complete and verified!")
        print("💡 You can now start the system with: ./run_system.sh start")
    else:
        print("\n❌ Some components need to be installed before using the system.")
        print("🔧 Run: bash install_dependencies.sh to install missing components")
        sys.exit(1)

if __name__ == "__main__":
    main()