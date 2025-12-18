#!/usr/bin/env python3
"""
🧠 AI Integration Module for Cyber Crack Pro
Handles integration with external AI services like WormGPT, DeepSeek, etc.
"""

import asyncio
import logging
import os
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import aiohttp
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class AIProviderConfig(BaseModel):
    name: str
    api_key: str
    base_url: str
    model: str
    enabled: bool = False
    max_tokens: int = 4096
    temperature: float = 0.7

class AIIntegrationManager:
    """Manages integration with external AI providers"""
    
    def __init__(self):
        self.providers = {}
        self.active_provider = "cyber_crack_internal"
        self.is_initialized = False
        self.http_session = None
        self.load_ai_configs()
    
    def load_ai_configs(self):
        """Load AI provider configurations from environment"""
        self.providers = {
            "wormgpt": AIProviderConfig(
                name="WormGPT",
                api_key=os.getenv("WORMGPT_API_KEY", ""),
                base_url=os.getenv("WORMGPT_BASE_URL", "https://api.wormgpt.com/v1"),
                model=os.getenv("WORMGPT_MODEL", "wormgpt-v4"),
                enabled=os.getenv("WORMGPT_ENABLED", "false").lower() == "true",
                max_tokens=8192,
                temperature=0.5
            ),
            "deepseek": AIProviderConfig(
                name="DeepSeek",
                api_key=os.getenv("DEEPSEEK_API_KEY", ""),
                base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
                model=os.getenv("DEEPSEEK_MODEL", "deepseek-coder"),
                enabled=os.getenv("DEEPSEEK_ENABLED", "false").lower() == "true",
                max_tokens=4096,
                temperature=0.7
            ),
            "openai": AIProviderConfig(
                name="OpenAI",
                api_key=os.getenv("OPENAI_API_KEY", ""),
                base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                enabled=os.getenv("OPENAI_ENABLED", "false").lower() == "true",
                max_tokens=4096,
                temperature=0.3
            ),
            "anthropic": AIProviderConfig(
                name="Anthropic Claude",
                api_key=os.getenv("ANTHROPIC_API_KEY", ""),
                base_url=os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1"),
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-opus"),
                enabled=os.getenv("ANTHROPIC_ENABLED", "false").lower() == "true",
                max_tokens=4096,
                temperature=0.5
            ),
            "cyber_crack_internal": AIProviderConfig(
                name="Cyber Crack Internal AI",
                api_key="",  # No API key needed
                base_url="",  # No external API call
                model="custom-internal",
                enabled=True,  # Always enabled
                max_tokens=2048,
                temperature=0.8
            )
        }
    
    async def initialize(self):
        """Initialize AI integration manager"""
        self.http_session = aiohttp.ClientSession()
        self.is_initialized = True
        logger.info("AI Integration Manager initialized")
    
    async def get_analysis_with_external_ai(self, provider_name: str, 
                                          code_snippet: str, 
                                          analysis_type: str) -> Optional[Dict[str, Any]]:
        """Get analysis from external AI provider"""
        if not self.is_initialized:
            await self.initialize()
        
        provider = self.providers.get(provider_name)
        if not provider or not provider.enabled or not provider.api_key:
            logger.warning(f"Provider {provider_name} not available or not enabled")
            return None
        
        try:
            # Construct prompt based on analysis type
            prompt = self.construct_prompt(analysis_type, code_snippet)
            
            # Prepare payload
            payload = {
                "model": provider.model,
                "messages": [
                    {"role": "system", "content": "You are an expert Android security researcher and reverse engineer."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": provider.max_tokens,
                "temperature": provider.temperature
            }
            
            # Make API call to external provider
            headers = {
                "Authorization": f"Bearer {provider.api_key}",
                "Content-Type": "application/json"
            }
            
            async with self.http_session.post(
                f"{provider.base_url}/chat/completions", 
                json=payload, 
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "provider": provider.name,
                        "analysis": result["choices"][0]["message"]["content"],
                        "model": result["model"],
                        "usage": result.get("usage", {}),
                        "timestamp": __import__('datetime').datetime.now().isoformat()
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"AI provider {provider_name} returned error: {response.status} - {error_text}")
                    return {
                        "success": False,
                        "provider": provider.name,
                        "error": f"HTTP {response.status}: {error_text}",
                        "timestamp": __import__('datetime').datetime.now().isoformat()
                    }
        
        except Exception as e:
            logger.error(f"Error calling AI provider {provider_name}: {e}")
            return {
                "success": False,
                "provider": provider.name,
                "error": str(e),
                "timestamp": __import__('datetime').datetime.now().isoformat()
            }
    
    def construct_prompt(self, analysis_type: str, code_snippet: str) -> str:
        """Construct appropriate prompt based on analysis type"""
        if analysis_type == "vulnerability_detection":
            return f"""
Analyze the following Android/Java/Smali code snippet for security vulnerabilities:

Code Snippet:
{code_snippet}

Look for:
1. Authentication bypass opportunities
2. In-app purchase validation weaknesses
3. Certificate pinning implementations
4. Root detection mechanisms
5. Debug detection implementations
6. Hardcoded credentials or secrets
7. Insecure storage of sensitive data
8. Insecure network communication
9. Any other security issues

For each vulnerability found, provide:
- Type of vulnerability
- Severity (Critical, High, Medium, Low)
- Exact location in code
- Recommended fix
"""
        elif analysis_type == "crack_recommendation":
            return f"""
Provide detailed recommendations for cracking the following Android/Java/Smali code:

Code Snippet:
{code_snippet}

Recommendations should include:
1. Specific modification instructions
2. Bytecode/hex changes needed
3. Potential bypass techniques
4. Stability considerations
5. Alternative approaches if primary method fails
"""
        elif analysis_type == "obfuscation_analysis":
            return f"""
Analyze the following Android/Java/Smali code for obfuscation techniques:

Code Snippet:
{code_snippet}

Identify:
1. Type of obfuscation used
2. Techniques employed
3. Methods to deobfuscate
4. Patterns to look for
"""
        else:
            return f"Analyze the following code for security implications: {code_snippet}"
    
    async def analyze_with_all_providers(self, code_snippet: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze using all available AI providers"""
        results = {}
        
        for provider_name, provider in self.providers.items():
            if provider.enabled and provider.api_key:  # For external providers, require API key
                result = await self.get_analysis_with_external_ai(provider_name, code_snippet, analysis_type)
                if result:
                    results[provider_name] = result
            elif provider_name == "cyber_crack_internal":
                # Internal AI doesn't need API key
                result = await self.internal_analysis(code_snippet, analysis_type)
                results[provider_name] = result
        
        return results
    
    async def internal_analysis(self, code_snippet: str, analysis_type: str) -> Dict[str, Any]:
        """Perform internal AI analysis using Cyber Crack's own models"""
        # This would use the internal AI models and algorithms
        # For now, return a simulated response
        
        # In a real implementation, this would call the internal AI model
        # loaded from the models directory
        
        if analysis_type == "vulnerability_detection":
            # Simulate finding common vulnerabilities
            vulnerabilities = ["authentication_bypass", "insecure_storage"] if "login" in code_snippet.lower() else []
            
            return {
                "success": True,
                "provider": "cyber_crack_internal",
                "analysis": f"Internal analysis found {len(vulnerabilities)} potential vulnerabilities",
                "vulnerabilities": vulnerabilities,
                "recommendations": ["implement_proper_validation", "secure_storage_implementation"],
                "confidence": 0.85,
                "timestamp": __import__('datetime').datetime.now().isoformat()
            }
        elif analysis_type == "crack_recommendation":
            return {
                "success": True,
                "provider": "cyber_crack_internal",
                "analysis": "Recommended crack approach: Modify authentication return value",
                "crack_method": "hook_authentication_function",
                "implementation": "Change return value from false to true in method",
                "confidence": 0.92,
                "timestamp": __import__('datetime').datetime.now().isoformat()
            }
        else:
            return {
                "success": True,
                "provider": "cyber_crack_internal",
                "analysis": "No specific analysis available for this type",
                "timestamp": __import__('datetime').datetime.now().isoformat()
            }
    
    def get_available_providers(self) -> List[str]:
        """Get list of available AI providers"""
        available = []
        for name, provider in self.providers.items():
            if provider.enabled or name == "cyber_crack_internal":
                available.append(name)
        return available
    
    async def close(self):
        """Close the AI integration manager"""
        if self.http_session:
            await self.http_session.close()

# Singleton instance
ai_manager = None

async def get_ai_manager() -> AIIntegrationManager:
    """Get the AI manager instance"""
    global ai_manager
    if ai_manager is None:
        ai_manager = AIIntegrationManager()
        await ai_manager.initialize()
    return ai_manager

# Example usage
async def main():
    manager = AIIntegrationManager()
    await manager.initialize()
    
    print(f"Available AI providers: {manager.get_available_providers()}")
    
    # Example code snippet for analysis
    sample_code = """
    public boolean authenticateUser(String password) {
        if (password.equals("hardcoded_password_123")) {
            return true;
        }
        return false;
    }
    """
    
    # Perform analysis with internal AI
    result = await manager.get_analysis_with_external_ai("cyber_crack_internal", sample_code, "vulnerability_detection")
    print(f"Internal AI analysis: {result}")
    
    # Get analysis from all providers
    all_results = await manager.analyze_with_all_providers(sample_code, "vulnerability_detection")
    print(f"All provider results: {list(all_results.keys())}")
    
    await manager.close()

if __name__ == "__main__":
    asyncio.run(main())