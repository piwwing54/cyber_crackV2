"""
⚙️ Configuration Module for Cyber Crack Pro
Handles application configuration including AI integration settings
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass
class AIConfig:
    """Configuration for AI integration"""
    wormgpt_enabled: bool = True
    wormgpt_api_url: str = "https://camillecyrm.serv00.net/Deep.php"
    deepseek_enabled: bool = True
    deepseek_api_url: str = "https://chat-deep.ai/wp-admin/admin-ajax.php"
    openai_enabled: bool = False
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    anthropic_enabled: bool = False
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-opus"
    timeout_seconds: int = 60
    max_retries: int = 3

@dataclass
class EngineConfig:
    """Configuration for core engines"""
    go_analyzer_url: str = "http://go-analyzer:8080"
    rust_cracker_url: str = "http://rust-cracker:8081"
    cpp_breaker_url: str = "http://cpp-breaker:8082"
    java_dex_url: str = "http://java-dex:8083"
    python_bridge_url: str = "http://python-bridge:8084"
    max_concurrent_jobs: int = 20
    job_timeout_seconds: int = 600
    enable_gpu_acceleration: bool = True
    enable_parallel_processing: bool = True

@dataclass
class SecurityConfig:
    """Configuration for security features"""
    enable_root_detection_bypass: bool = True
    enable_certificate_pinning_bypass: bool = True
    enable_debug_detection_bypass: bool = True
    enable_antitempering: bool = True
    enable_obfuscation: bool = True
    preserve_app_functionality: bool = True
    stability_check_enabled: bool = True
    stability_threshold: float = 75.0

class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/app_config.json"
        self.ai_config = self.load_ai_config()
        self.engine_config = self.load_engine_config()
        self.security_config = self.load_security_config()
    
    def load_ai_config(self) -> AIConfig:
        """Load AI configuration from file or environment"""
        config_data = self.load_config_file()
        
        return AIConfig(
            wormgpt_enabled=config_data.get("wormgpt_enabled", True),
            wormgpt_api_url=config_data.get("wormgpt_api_url", "https://camillecyrm.serv00.net/Deep.php"),
            deepseek_enabled=config_data.get("deepseek_enabled", True),
            deepseek_api_url=config_data.get("deepseek_api_url", "https://chat-deep.ai/wp-admin/admin-ajax.php"),
            openai_api_key=os.getenv("OPENAI_API_KEY", config_data.get("openai_api_key", "")),
            openai_model=config_data.get("openai_model", "gpt-4"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", config_data.get("anthropic_api_key", "")),
            anthropic_model=config_data.get("anthropic_model", "claude-3-opus"),
            timeout_seconds=config_data.get("timeout_seconds", 60),
            max_retries=config_data.get("max_retries", 3)
        )
    
    def load_engine_config(self) -> EngineConfig:
        """Load engine configuration from file or environment"""
        config_data = self.load_config_file()
        
        return EngineConfig(
            go_analyzer_url=os.getenv("GO_ANALYZER_URL", config_data.get("go_analyzer_url", "http://localhost:8080")),
            rust_cracker_url=os.getenv("RUST_CRACKER_URL", config_data.get("rust_cracker_url", "http://localhost:8081")),
            cpp_breaker_url=os.getenv("CPP_BREAKER_URL", config_data.get("cpp_breaker_url", "http://localhost:8082")),
            java_dex_url=os.getenv("JAVA_DEX_URL", config_data.get("java_dex_url", "http://localhost:8083")),
            python_bridge_url=os.getenv("PYTHON_BRIDGE_URL", config_data.get("python_bridge_url", "http://localhost:8084")),
            max_concurrent_jobs=config_data.get("max_concurrent_jobs", 20),
            job_timeout_seconds=config_data.get("job_timeout_seconds", 600),
            enable_gpu_acceleration=config_data.get("enable_gpu_acceleration", True),
            enable_parallel_processing=config_data.get("enable_parallel_processing", True)
        )
    
    def load_security_config(self) -> SecurityConfig:
        """Load security configuration from file or environment"""
        config_data = self.load_config_file()
        
        return SecurityConfig(
            enable_root_detection_bypass=config_data.get("enable_root_detection_bypass", True),
            enable_certificate_pinning_bypass=config_data.get("enable_certificate_pinning_bypass", True),
            enable_debug_detection_bypass=config_data.get("enable_debug_detection_bypass", True),
            enable_antitempering=config_data.get("enable_antitempering", True),
            enable_obfuscation=config_data.get("enable_obfuscation", True),
            preserve_app_functionality=config_data.get("preserve_app_functionality", True),
            stability_check_enabled=config_data.get("stability_check_enabled", True),
            stability_threshold=config_data.get("stability_threshold", 75.0)
        )
    
    def load_config_file(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading config file: {e}")
        
        # Return default config if file doesn't exist or fails to load
        return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values"""
        return {
            "wormgpt_enabled": True,
            "wormgpt_api_url": "https://camillecyrm.serv00.net/Deep.php",
            "deepseek_enabled": True,
            "deepseek_api_url": "https://chat-deep.ai/wp-admin/admin-ajax.php",
            "openai_enabled": False,
            "openai_model": "gpt-4",
            "anthropic_enabled": False,
            "anthropic_model": "claude-3-opus",
            "timeout_seconds": 60,
            "max_retries": 3,
            "go_analyzer_url": "http://go-analyzer:8080",
            "rust_cracker_url": "http://rust-cracker:8081",
            "cpp_breaker_url": "http://cpp-breaker:8082",
            "java_dex_url": "http://java-dex:8083",
            "python_bridge_url": "http://python-bridge:8084",
            "max_concurrent_jobs": 20,
            "job_timeout_seconds": 600,
            "enable_gpu_acceleration": True,
            "enable_parallel_processing": True,
            "enable_root_detection_bypass": True,
            "enable_certificate_pinning_bypass": True,
            "enable_debug_detection_bypass": True,
            "enable_antitempering": True,
            "enable_obfuscation": True,
            "preserve_app_functionality": True,
            "stability_check_enabled": True,
            "stability_threshold": 75.0
        }
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            config_file = Path(self.config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            config_data = {
                "wormgpt_enabled": self.ai_config.wormgpt_enabled,
                "wormgpt_api_url": self.ai_config.wormgpt_api_url,
                "deepseek_enabled": self.ai_config.deepseek_enabled,
                "deepseek_api_url": self.ai_config.deepseek_api_url,
                "openai_enabled": self.ai_config.openai_enabled,
                "openai_model": self.ai_config.openai_model,
                "anthropic_enabled": self.ai_config.anthropic_enabled,
                "anthropic_model": self.ai_config.anthropic_model,
                "timeout_seconds": self.ai_config.timeout_seconds,
                "max_retries": self.ai_config.max_retries,
                "go_analyzer_url": self.engine_config.go_analyzer_url,
                "rust_cracker_url": self.engine_config.rust_cracker_url,
                "cpp_breaker_url": self.engine_config.cpp_breaker_url,
                "java_dex_url": self.engine_config.java_dex_url,
                "python_bridge_url": self.engine_config.python_bridge_url,
                "max_concurrent_jobs": self.engine_config.max_concurrent_jobs,
                "job_timeout_seconds": self.engine_config.job_timeout_seconds,
                "enable_gpu_acceleration": self.engine_config.enable_gpu_acceleration,
                "enable_parallel_processing": self.engine_config.enable_parallel_processing,
                "enable_root_detection_bypass": self.security_config.enable_root_detection_bypass,
                "enable_certificate_pinning_bypass": self.security_config.enable_certificate_pinning_bypass,
                "enable_debug_detection_bypass": self.security_config.enable_debug_detection_bypass,
                "enable_antitempering": self.security_config.enable_antitempering,
                "enable_obfuscation": self.security_config.enable_obfuscation,
                "preserve_app_functionality": self.security_config.preserve_app_functionality,
                "stability_check_enabled": self.security_config.stability_check_enabled,
                "stability_threshold": self.security_config.stability_threshold
            }
            
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def update_ai_config(self, new_config: Dict[str, Any]):
        """Update AI configuration"""
        for key, value in new_config.items():
            if hasattr(self.ai_config, key):
                setattr(self.ai_config, key, value)
    
    def update_engine_config(self, new_config: Dict[str, Any]):
        """Update engine configuration"""
        for key, value in new_config.items():
            if hasattr(self.engine_config, key):
                setattr(self.engine_config, key, value)
    
    def update_security_config(self, new_config: Dict[str, Any]):
        """Update security configuration"""
        for key, value in new_config.items():
            if hasattr(self.security_config, key):
                setattr(self.security_config, key, value)

# Global configuration instance
config_manager = ConfigManager()

def get_config() -> ConfigManager:
    """Get the global configuration instance"""
    return config_manager