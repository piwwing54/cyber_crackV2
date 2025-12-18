#!/usr/bin/env python3
"""
CYBER CRACK PRO v3.0 - SIMPLE START SCRIPT
Single command to start the system with NVIDIA CUDA conditional support
"""

import subprocess
import json
import os
import sys
import time
from pathlib import Path
import asyncio

def check_nvidia_support():
    """Check if system supports NVIDIA CUDA"""
    try:
        # Check if nvidia-smi command is available
        result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and "NVIDIA" in result.stdout:
            print("✅ NVIDIA GPU detected - CUDA support available")
            return True
        else:
            print("⚠️  No NVIDIA GPU detected - using CPU-only services")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  nvidia-smi not found - using CPU-only services")
        return False

def create_conditional_docker_compose():
    """Create docker-compose with conditional NVIDIA services"""
    has_cuda = check_nvidia_support()
    
    # Define basic services that always run
    services = {
        "redis": {
            "image": "redis:7-alpine",
            "container_name": "cyber-crack-redis",
            "command": "redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-defaultpassword}",
            "ports": ["6379:6379"],
            "volumes": ["redis_data:/data"],
            "restart": "unless-stopped",
            "healthcheck": {
                "test": ["CMD", "redis-cli", "ping"],
                "interval": "10s",
                "timeout": "5s",
                "retries": 3
            }
        },
        "postgres": {
            "image": "postgres:15-alpine",
            "container_name": "cyber-crack-postgres",
            "ports": ["5432:5432"],
            "environment": {
                "POSTGRES_DB": "cybercrackpro",
                "POSTGRES_USER": "cracker",
                "POSTGRES_PASSWORD": "${POSTGRES_PASSWORD:-password}",
                "PGDATA": "/var/lib/postgresql/data/pgdata"
            },
            "volumes": [
                "postgres_data:/var/lib/postgresql/data",
                "./database/init.sql:/docker-entrypoint-initdb.d/01-init.sql",
                "./database/migrations:/docker-entrypoint-initdb.d/migrations/"
            ],
            "restart": "unless-stopped",
            "healthcheck": {
                "test": ["CMD-SHELL", "pg_isready -U cracker"],
                "interval": "10s",
                "timeout": "5s",
                "retries": 3
            }
        },
        "python-bridge": {
            "build": {
                "context": "./core/python-bridge",
                "dockerfile": "Dockerfile"
            },
            "container_name": "cyber-crack-python-bridge", 
            "ports": ["8084:8084"],
            "environment": {
                "REDIS_URL": "redis://redis:6379",
                "DEEPSEEK_API_KEY": "${DEEPSEEK_API_KEY}",
                "WORMGPT_API_KEY": "${WORMGPT_API_KEY}",
                "PYTHONUNBUFFERED": "1",
                "PYTORCH_CUDA_ALLOC_CONF": "max_split_size_mb:128"
            },
            "volumes": [
                "./uploads:/uploads",
                "./models:/app/models",
                "./datasets:/app/datasets"
            ],
            "depends_on": ["redis"],
            "restart": "unless-stopped"
        },
        "prometheus": {
            "image": "prom/prometheus",
            "container_name": "cyber-crack-prometheus",
            "ports": ["9090:9090"],
            "volumes": [
                "./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml",
                "prometheus_data:/prometheus"
            ],
            "command": [
                "--config.file=/etc/prometheus/prometheus.yml",
                "--storage.tsdb.path=/prometheus",
                "--web.console.libraries=/etc/prometheus/console_libraries",
                "--web.console.templates=/etc/prometheus/consoles",
                "--storage.tsdb.retention.time=200h",
                "--web.enable-lifecycle"
            ],
            "restart": "unless-stopped"
        },
        "grafana": {
            "image": "grafana/grafana",
            "container_name": "cyber-crack-grafana",
            "ports": ["3001:3000"],
            "environment": {
                "GF_SECURITY_ADMIN_PASSWORD": "${GRAFANA_ADMIN_PASSWORD:-admin}",
                "GF_USERS_ALLOW_SIGN_UP": "false",
                "GF_INSTALL_PLUGINS": "grafana-piechart-panel,grafana-worldmap-panel"
            },
            "volumes": [
                "grafana_data:/var/lib/grafana",
                "./monitoring/dashboards:/etc/grafana/provisioning/dashboards",
                "./monitoring/datasources:/etc/grafana/provisioning/datasources"
            ],
            "depends_on": ["prometheus"],
            "restart": "unless-stopped"
        }
    }
    
    # Add orchestrator service
    services["orchestrator"] = {
        "build": {
            "context": ".",
            "dockerfile": "Dockerfile.orchestrator"
        },
        "container_name": "cyber-crack-orchestrator",
        "ports": ["5000:5000"],  
        "environment": {
            "REDIS_URL": "redis://redis:6379",
            "POSTGRES_URL": "postgresql://cracker:${POSTGRES_PASSWORD:-password}@postgres:5432/cybercrackpro",
            "DEEPSEEK_API_KEY": "${DEEPSEEK_API_KEY}",
            "WORMGPT_API_KEY": "${WORMGPT_API_KEY}",
            "GO_ENGINE_URL": "http://go-analyzer:8080",
            "RUST_ENGINE_URL": "http://rust-cracker:8081", 
            "CPP_ENGINE_URL": "http://cpp-breaker:8082" if has_cuda else "http://localhost:8082", # For reference only
            "JAVA_ENGINE_URL": "http://java-dex:8083",
            "PYTHON_ENGINE_URL": "http://python-bridge:8084",
            "MAX_CONCURRENT_JOBS": 20,
            "ENABLE_AI_ANALYSIS": "true"
        },
        "volumes": [
            "./uploads:/app/uploads",
            "./results:/app/results",
            "./patterns:/app/patterns",
            "./models:/app/models"
        ],
        "depends_on": {
            "redis": {"condition": "service_healthy"},
            "postgres": {"condition": "service_healthy"},
            "python-bridge": {"condition": "service_started"}
        },
        "restart": "unless-stopped",
        "healthcheck": {
            "test": ["CMD", "curl", "-f", "http://localhost:5000/health"],
            "interval": "30s",
            "timeout": "10s", 
            "retries": 3,
            "start_period": "60s"
        }
    }
    
    # Add optional CUDA-dependent service if GPU available
    if has_cuda:
        services["cpp-breaker"] = {
            "build": {
                "context": "./core/cpp-breaker", 
                "dockerfile": "Dockerfile.gpu"  # Use GPU Dockerfile
            },
            "container_name": "cyber-crack-cpp-breaker",
            "ports": ["8082:8082"],
            "environment": {
                "REDIS_URL": "redis://redis:6379",
                "NVIDIA_VISIBLE_DEVICES": "all",
                "CUDA_DEVICE_ORDER": "PCI_BUS_ID"
            },
            "volumes": ["./uploads:/uploads"],
            "depends_on": ["redis"],
            "restart": "unless-stopped",
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "8.0",
                        "memory": "8G",
                        "nvidia.com/gpu": "1"
                    },
                    "reservations": {
                        "cpus": "4.0",
                        "memory": "4G",
                        "nvidia.com/gpu": "1"
                    }
                }
            }
        }
        print("🎨 GPU-accelerated C++ engine will be included")
    else:
        # Add CPU-only service instead
        services["cpp-breaker"] = {
            "build": {
                "context": "./core/cpp-breaker", 
                "dockerfile": "Dockerfile.cpu"  # Use CPU-optimized Dockerfile
            },
            "container_name": "cyber-crack-cpp-breaker",
            "ports": ["8082:8082"],
            "environment": {
                "REDIS_URL": "redis://redis:6379"
            },
            "volumes": ["./uploads:/uploads"],
            "depends_on": ["redis"],
            "restart": "unless-stopped"
        }
        print("💻 CPU-only C++ engine will be used (no GPU)")
    
    # Add additional services
    services.update({
        "go-analyzer": {
            "build": {
                "context": "./core/go-analyzer",
                "dockerfile": "Dockerfile"
            },
            "container_name": "cyber-crack-go-analyzer",
            "ports": ["8080:8080"],
            "environment": {
                "REDIS_URL": "redis://redis:6379",
                "GIN_MODE": "release",
                "GOMAXPROCS": "4",
                "GOMEMLIMIT": "4GiB"
            },
            "volumes": [
                "./uploads:/uploads",
                "./tools:/tools"
            ],
            "depends_on": ["redis"],
            "restart": "unless-stopped"
        },
        "rust-cracker": {
            "build": {
                "context": "./core/rust-cracker",
                "dockerfile": "Dockerfile"
            },
            "container_name": "cyber-crack-rust-cracker",
            "ports": ["8081:8081"],
            "environment": {
                "REDIS_URL": "redis://redis:6379",
                "RUST_LOG": "info",
                "RUST_BACKTRACE": "1"
            },
            "volumes": ["./uploads:/uploads"],
            "depends_on": ["redis"],
            "restart": "unless-stopped"
        },
        "java-dex": {
            "build": {
                "context": "./core/java-dex",
                "dockerfile": "Dockerfile"
            },
            "container_name": "cyber-crack-java-dex",
            "ports": ["8083:8083"],
            "environment": {
                "REDIS_URL": "redis://redis:6379",
                "JAVA_OPTS": "-Xmx4g -Xms2g -XX:+UseG1GC",
                "ANDROID_HOME": "/opt/android-sdk"
            },
            "volumes": [
                "./uploads:/uploads",
                "./tools:/tools"
            ],
            "depends_on": ["redis"],
            "restart": "unless-stopped"
        },
        "telegram-bot": {
            "build": {
                "context": "./frontend",
                "dockerfile": "Dockerfile.telegram"
            },
            "container_name": "cyber-crack-telegram-bot",
            "environment": {
                "TELEGRAM_BOT_TOKEN": "${TELEGRAM_BOT_TOKEN}",
                "ORCHESTRATOR_URL": "http://orchestrator:5000",
                "REDIS_URL": "redis://redis:6379",
                "DEEPSEEK_API_KEY": "${DEEPSEEK_API_KEY}",
                "WORMGPT_API_KEY": "${WORMGPT_API_KEY}",
                "MAX_UPLOAD_SIZE": 524288000,
                "ENABLE_AI_FEATURES": "true"
            },
            "volumes": ["./uploads:/app/uploads"],
            "depends_on": ["orchestrator"],
            "restart": "unless-stopped"
        },
        "web-dashboard": {
            "build": {
                "context": "./frontend",
                "dockerfile": "Dockerfile.web"
            },
            "container_name": "cyber-crack-web-dashboard",
            "ports": ["8000:8000"],
            "environment": {
                "ORCHESTRATOR_URL": "http://orchestrator:5000",
                "REDIS_URL": "redis://redis:6379",
                "PYTHONPATH": "/app",
                "MAX_UPLOAD_SIZE": 524288000,
                "ENABLE_AI_FEATURES": "true"
            },
            "volumes": ["./uploads:/app/uploads"],
            "depends_on": ["orchestrator"],
            "restart": "unless-stopped"
        }
    })
    
    compose_config = {
        "version": "3.8",
        "services": services,
        "volumes": {
            "redis_data": {"driver": "local"},
            "postgres_data": {"driver": "local"},
            "prometheus_data": {"driver": "local"},
            "grafana_data": {"driver": "local"},
            "uploads": {
                "driver": "local",
                "driver_opts": {"type": "none", "o": "bind", "device": "./uploads"}
            },
            "results": {
                "driver": "local", 
                "driver_opts": {"type": "none", "o": "bind", "device": "./results"}
            }
        }
    }
    
    # Write conditional docker-compose file
    with open("docker-compose-full.yml", "w") as f:
        import yaml
        yaml.dump(compose_config, f, default_flow_style=False, sort_keys=False)
    
    return has_cuda

def main():
    print("🚀 CYBER CRACK PRO v3.0 - CONDITIONAL START SCRIPT")
    print("=" * 60)
    
    print("🔍 Checking system capabilities...")
    has_cuda = check_nvidia_support()
    
    print("📄 Creating conditional docker-compose configuration...")
    create_conditional_docker_compose()
    
    print("\n⚙️  STARTING CYBER CRACK PRO SYSTEM...")
    print("-" * 40)
    
    # Run docker-compose up in background
    try:
        result = subprocess.run([
            "docker-compose", "-f", "docker-compose-full.yml", "up", "-d", "--build"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ System started successfully in background!")
            print("   All services are launching...")
            print(f"   NVIDIA CUDA Support: {'✅ YES' if has_cuda else '💻 NO (CPU-only)'}")
            
            print("\n🌐 ACCESS POINTS:")
            print("   • Web Dashboard: http://localhost:8000")
            print("   • Orchestrator API: http://localhost:5000")  
            print("   • Python Bridge: http://localhost:8084")
            print("   • Monitoring: http://localhost:3001 (admin/admin)")
            print("   • Telegram Bot: @Yancumintybot")
            
            print("\n📋 TO CHECK STATUS:")
            print("   • Run: docker-compose -f docker-compose-full.yml ps")
            print("   • Check logs: docker-compose -f docker-compose-full.yml logs")
            
            print(f"\n🎯 SYSTEM IS NOW RUNNING IN BACKGROUND!")
            print(f"   • All services launched with {'GPU' if has_cuda else 'CPU'} optimization")
            print(f"   • Ready to process YOUR OWN applications")
            
        else:
            print("❌ Error starting system:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error running docker-compose: {e}")

if __name__ == "__main__":
    main()