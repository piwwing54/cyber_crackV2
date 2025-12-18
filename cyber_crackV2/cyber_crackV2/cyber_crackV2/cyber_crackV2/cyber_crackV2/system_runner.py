#!/usr/bin/env python3
"""
CYBER CRACK PRO - Complete System Runner
Handles all the complexities of running the full system with proper error handling
"""

import sys
import os
import subprocess
import time
from pathlib import Path
import asyncio

def check_docker():
    """Check if Docker is available"""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Docker is available")
            return True
        else:
            print("❌ Docker is not available")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Docker is not available")
        return False

def check_docker_compose():
    """Check if Docker Compose is available"""
    try:
        result = subprocess.run(['docker-compose', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Docker Compose is available")
            return True
        else:
            print("❌ Docker Compose is not available")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Docker Compose is not available")
        return False

def create_env_file():
    """Create a basic .env file if it doesn't exist"""
    env_path = Path('.env')
    if not env_path.exists():
        print("📝 Creating basic .env file...")
        env_content = """
# Cyber Crack Pro Environment Configuration
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
DEEPSEEK_API_KEY=YOUR_DEEPSEEK_API_KEY_HERE
WORMGPT_API_KEY=YOUR_WORMGPT_API_KEY_HERE

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=cybercrackpro
POSTGRES_USER=cracker
POSTGRES_PASSWORD=securepassword123

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=

# Orchestrator Configuration
ORCHESTRATOR_URL=http://localhost:5000
API_GATEWAY_URL=http://localhost:3000

# Engine URLs
GO_ENGINE_URL=http://localhost:8080
RUST_ENGINE_URL=http://localhost:8081
CPP_ENGINE_URL=http://localhost:8082
JAVA_ENGINE_URL=http://localhost:8083
PYTHON_ENGINE_URL=http://localhost:8084

# Feature Flags
ENABLE_AI_ANALYSIS=true
ENABLE_GPU_ACCELERATION=false
ENABLE_DOCKER_SUPPORT=true
"""
        env_path.write_text(env_content.strip())
        print("✅ Basic .env file created")
        print("💡 Please update with your actual API keys before running full system")
    else:
        print("✅ .env file already exists")

def run_system_options():
    """Present different options for running the system"""
    print("\n🚀 CYBER CRACK PRO - SYSTEM RUN OPTIONS")
    print("=" * 50)
    
    print("\n1. Core Engine Only (No Docker required)")
    print("   • Runs main engine analysis")
    print("   • Tests pattern matching")
    print("   • Verifies basic functionality")
    print("   • Command: python3 run_engine.py")
    
    print("\n2. Full Docker System (Requires Docker)")
    print("   • Starts all services in containers")
    print("   • Includes Go, Rust, C++, Java engines")
    print("   • Runs Telegram bot and web dashboard")
    print("   • Command: docker-compose up -d")
    
    print("\n3. Demo Mode")
    print("   • Runs simplified demo")
    print("   • Shows system capabilities")
    print("   • Command: python3 run_core.py")
    
    print("\n4. Check Dependencies")
    print("   • Verify required components")
    print("   • Docker, Python packages, etc.")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        print("\n🔧 Running Core Engine...")
        os.system("python3 run_engine.py")
        
    elif choice == "2":
        print("\n🐳 Running Full Docker System...")
        if check_docker() and check_docker_compose():
            print("💡 Creating .env file if needed...")
            create_env_file()
            
            print("\n⚠️  Warning: This will start all Docker containers")
            print("   This may take several minutes and requires significant resources")
            confirm = input("   Continue? (y/N): ").lower()
            
            if confirm == 'y':
                print("\n🔄 Building and starting Docker containers...")
                os.system("docker-compose up -d --build")
                
                print("\n📊 Checking container status...")
                os.system("docker-compose ps")
                
                print("\n💡 Access the system at:")
                print("   • Web Dashboard: http://localhost:8000")
                print("   • API: http://localhost:5000")
                print("   • Monitoring: http://localhost:3001")
                print("   • Check logs: docker-compose logs")
            else:
                print("❌ Operation cancelled")
        else:
            print("❌ Docker or Docker Compose not available, cannot run full system")
    
    elif choice == "3":
        print("\n🎯 Running Demo Mode...")
        os.system("python3 run_core.py")
        
    elif choice == "4":
        print("\n🔍 Checking System Dependencies...")
        docker_ok = check_docker()
        compose_ok = check_docker_compose()
        
        # Check Python packages
        required_packages = [
            'aiohttp', 'aiogram', 'redis', 'fastapi', 
            'pydantic', 'sqlalchemy', 'docker', 'numpy'
        ]
        
        print("\n📋 Python packages:")
        for pkg in required_packages:
            try:
                __import__(pkg)
                print(f"   ✅ {pkg}")
            except ImportError:
                print(f"   ❌ {pkg}")
        
        print(f"\n🐳 Docker: {'✅ Available' if docker_ok else '❌ Not available'}")
        print(f"🐳 Docker Compose: {'✅ Available' if compose_ok else '❌ Not available'}")
        
        # Check for essential files
        essential_files = ['main.py', 'master_coordinator.py', 'README.md']
        print("\n📄 Essential files:")
        for f in essential_files:
            exists = Path(f).exists()
            print(f"   {'✅' if exists else '❌'} {f}")
    
    else:
        print("❌ Invalid choice")

def main():
    """Main function"""
    print("🌟 CYBER CRACK PRO v3.0 - SYSTEM RUNNER")
    print("=" * 50)
    
    print("\n🤖 Advanced APK Cracking System")
    print("⚡ Multi-language processing (Go/Rust/C++/Java/Python)")
    print("🧠 Dual AI integration (DeepSeek + WormGPT)")
    print("🔐 100+ security bypass methods")
    
    # Show project directory
    project_dir = Path.cwd()
    print(f"\n📂 Current directory: {project_dir}")
    
    # Check if we're in the right directory
    if not Path('README.md').exists():
        print("⚠️  Warning: README.md not found in current directory")
        print("   Make sure you're running this from the project root")
    
    run_system_options()
    
    print("\n" + "=" * 50)
    print("💡 TIPS:")
    print("   • Use option 1 for quick testing")
    print("   • Use option 2 for full production system")
    print("   • Get API keys for DeepSeek and WormGPT for AI features")
    print("   • Ensure Docker has enough resources (8GB+ RAM recommended)")
    print("=" * 50)

if __name__ == "__main__":
    main()