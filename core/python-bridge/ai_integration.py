#!/usr/bin/env python3
"""
🤖 AI Integration Module for Cyber Crack Pro
Integrates with WormGPT and DeepSeek APIs for enhanced analysis
"""

import asyncio
import json
import logging
import os
import re
from typing import Dict, List, Optional, Any
from pathlib import Path
import aiohttp
from pydantic import BaseModel
import time

logger = logging.getLogger(__name__)

class AIIntegration:
    """Manages integration with external AI services"""
    
    def __init__(self):
        self.wormgpt_api_key = os.getenv("WORMGPT_API_KEY", "")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.wormgpt_base_url = "https://camillecyrm.serv00.net/Deep.php"
        self.deepseek_base_url = "https://chat-deep.ai/wp-admin/admin-ajax.php"
        self.ai_sessions = {}  # Store chat sessions
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize AI integration"""
        logger.info("AI Integration initialized")
        self.is_initialized = True
        
    async def analyze_with_wormgpt(self, code_content: str, analysis_type: str = "security") -> Dict[str, Any]:
        """Analyze code content using WormGPT API"""
        try:
            # Prepare analysis request
            prompt = f"""
Analyze this Android APK code for {analysis_type} issues:
{code_content[:2000]}  # Limit content to prevent API issues

Identify:
1. Security vulnerabilities
2. Protection mechanisms to bypass
3. Potential crack points
4. Recommended bypass methods
5. Stability concerns
"""
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.wormgpt_base_url,
                    params={"text": prompt}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("status") == "success":
                            return {
                                "success": True,
                                "response": result.get("reply", ""),
                                "chat_id": result.get("chat_id"),
                                "confidence": 0.85,
                                "provider": "wormgpt",
                                "analysis_type": analysis_type,
                                "timestamp": time.time()
                            }
                        else:
                            return {
                                "success": False,
                                "error": f"API returned: {result}",
                                "provider": "wormgpt",
                                "analysis_type": analysis_type
                            }
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "provider": "wormgpt",
                            "analysis_type": analysis_type
                        }
        except Exception as e:
            logger.error(f"Error calling WormGPT API: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "wormgpt",
                "analysis_type": analysis_type
            }
    
    async def analyze_with_deepseek(self, code_content: str) -> Dict[str, Any]:
        """Analyze code content using DeepSeek API"""
        try:
            # First, get nonce from the DeepSeek website
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                # Get the website content to extract nonce
                async with session.get("https://chat-deep.ai/", headers=headers) as html_response:
                    if html_response.status != 200:
                        return {
                            "success": False,
                            "error": f"Could not access DeepSeek website: HTTP {html_response.status}",
                            "provider": "deepseek"
                        }
                    
                    html_content = await html_response.text()
                    
                    # Extract nonce using regex
                    nonce_match = re.search(r'"nonce":"([a-f0-9]+)"', html_content)
                    if not nonce_match:
                        return {
                            "success": False,
                            "error": "Could not find nonce in DeepSeek website",
                            "provider": "deepseek"
                        }
                    
                    nonce = nonce_match.group(1)
                    
                    # Prepare the analysis request
                    analysis_prompt = f"""
Analyze this Android APK code for security issues:
{code_content[:2000]}  # Limit content to prevent API issues

Identify:
1. Security vulnerabilities
2. Protection mechanisms to bypass
3. Potential crack points
4. Recommended bypass methods
5. Stability concerns
"""
                    
                    # Make the analysis request
                    data = {
                        'action': 'deepseek_chat',
                        'message': analysis_prompt,
                        'model': 'deepseek-chat',
                        'nonce': nonce,
                        'save_conversation': '0',
                        'session_only': '1'
                    }
                    
                    response = await session.post(
                        self.deepseek_base_url,
                        data=data,
                        headers={
                            'User-Agent': "Mozilla/5.0",
                            'Origin': "https://chat-deep.ai",
                            'Referer': "https://chat-deep.ai/",
                            'Content-Type': "application/x-www-form-urlencoded"
                        }
                    )
                    
                    if response.status == 200:
                        result = await response.json()
                        if result.get("success"):
                            return {
                                "success": True,
                                "response": result.get("data", {}).get("response", ""),
                                "confidence": 0.80,
                                "provider": "deepseek",
                                "timestamp": time.time()
                            }
                        else:
                            return {
                                "success": False,
                                "error": f"DeepSeek API returned: {result}",
                                "provider": "deepseek"
                            }
                    else:
                        return {
                            "success": False,
                            "error": f"DeepSeek HTTP {response.status}",
                            "provider": "deepseek"
                        }
        except Exception as e:
            logger.error(f"Error calling DeepSeek API: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "deepseek"
            }
    
    async def get_analysis_recommendations(self, analysis_text: str) -> List[str]:
        """Extract recommendations from AI analysis text"""
        recommendations = []
        
        # Look for common recommendation patterns in the analysis
        rec_patterns = [
            r"(?i)recommend(ed|ation).*?:\s*(.+?)(?=\n|$)",
            r"(?i)suggestion.*?:\s*(.+?)(?=\n|$)",
            r"(?i)bypass.*?:\s*(.+?)(?=\n|$)",
            r"(?i)fix.*?:\s*(.+?)(?=\n|$)",
            r"(?i)tamper.*?:\s*(.+?)(?=\n|$)",
            r"(?i)modify.*?:\s*(.+?)(?=\n|$)",
            r"(?i)patch.*?:\s*(.+?)(?=\n|$)",
            r"(?i)hook.*?:\s*(.+?)(?=\n|$)",
        ]
        
        for pattern in rec_patterns:
            matches = re.findall(pattern, analysis_text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Extract the actual recommendation from tuple
                    text = match[1] if len(match) > 1 else match[0]
                else:
                    text = str(match)
                
                text = text.strip()
                if len(text) > 10:  # Filter out very short matches
                    recommendations.append(text)
        
        return list(set(recommendations))  # Remove duplicates
    
    async def extract_vulnerabilities(self, analysis_text: str) -> List[Dict[str, str]]:
        """Extract vulnerabilities from AI analysis text"""
        vulnerabilities = []
        
        # Look for vulnerability patterns in the analysis
        vuln_patterns = [
            r"(?i)vulnerabilit(y|ies).*?:\s*(.+?)(?=\n|$)",
            r"(?i)insecure.*?(storag(e|ing)|cod(e|ing)|transmission).*?:\s*(.+?)(?=\n|$)",
            r"(?i)hardcoded.*?(cred|key|token|password).*?:\s*(.+?)(?=\n|$)",
            r"(?i)root.*?detection.*?:\s*(.+?)(?=\n|$)",
            r"(?i)certificat(e|es).*?pinn(ing|ed).*?:\s*(.+?)(?=\n|$)",
            r"(?i)debug.*?detection.*?:\s*(.+?)(?=\n|$)",
            r"(?i)anti.*?tamp(er|ering).*?:\s*(.+?)(?=\n|$)",
            r"(?i)auth.*?bypass.*?:\s*(.+?)(?=\n|$)",
        ]
        
        for pattern in vuln_patterns:
            matches = re.findall(pattern, analysis_text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    text = match[1] if len(match) > 1 else match[0]
                else:
                    text = str(match)
                
                text = text.strip()
                if len(text) > 5:  # Filter out very short matches
                    vuln = {
                        "type": "extracted_vulnerability",
                        "description": text,
                        "severity": "UNKNOWN",
                        "confidence": "MEDIUM"
                    }
                    vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    async def combine_analyses(self, local_analysis: Dict[str, Any], 
                            wormgpt_analysis: Dict[str, Any], 
                            deepseek_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Combine local analysis with AI analyses"""
        combined = local_analysis.copy()
        
        # Extract and add AI recommendations
        ai_recommendations = []
        
        if wormgpt_analysis.get("success") and "response" in wormgpt_analysis:
            wormgpt_recs = await self.get_analysis_recommendations(wormgpt_analysis["response"])
            ai_recommendations.extend(wormgpt_recs)
            
            # Add WormGPT-specific insights
            combined["wormgpt_insights"] = wormgpt_analysis["response"]
        
        if deepseek_analysis.get("success") and "response" in deepseek_analysis:
            deepseek_recs = await self.get_analysis_recommendations(deepseek_analysis["response"])
            ai_recommendations.extend(deepseek_recs)
            
            # Add DeepSeek-specific insights
            combined["deepseek_insights"] = deepseek_analysis["response"]
        
        # Remove duplicates and add to recommendations
        unique_recs = list(set(local_analysis.get("recommendations", []) + ai_recommendations))
        combined["recommendations"] = unique_recs
        
        # Extract AI-detected vulnerabilities and merge with local ones
        ai_vulnerabilities = []
        if wormgpt_analysis.get("success"):
            ai_vulns = await self.extract_vulnerabilities(wormgpt_analysis.get("response", ""))
            ai_vulnerabilities.extend(ai_vulns)
        
        if deepseek_analysis.get("success"):
            ai_vulns = await self.extract_vulnerabilities(deepseek_analysis.get("response", ""))
            ai_vulnerabilities.extend(ai_vulns)
        
        # Combine vulnerabilities
        local_vulns = local_analysis.get("vulnerabilities", [])
        combined["vulnerabilities"] = local_vulns + ai_vulnerabilities
        
        # Update security score based on AI input
        # The AI might have found additional vulnerabilities
        if ai_vulnerabilities:
            current_score = local_analysis.get("security_score", 100)
            # Lower score based on additional AI-found vulnerabilities
            combined["security_score"] = max(0, current_score - len(ai_vulnerabilities) * 5)
        
        return combined

    async def perform_enhanced_analysis(self, apk_content: str, analysis_type: str = "security") -> Dict[str, Any]:
        """Perform enhanced analysis using both local and AI methods"""
        
        # Perform local analysis as base
        local_analysis = {
            "vulnerabilities": [],
            "protections": [],
            "recommendations": [],
            "security_score": 80,
            "complexity_level": "MEDIUM"
        }
        
        # Perform AI analysis with both providers
        wormgpt_task = self.analyze_with_wormgpt(apk_content, analysis_type)
        deepseek_task = self.analyze_with_deepseek(apk_content)
        
        # Run both AI analyses concurrently
        wormgpt_result, deepseek_result = await asyncio.gather(
            wormgpt_task,
            deepseek_task
        )
        
        # Combine all analyses
        enhanced_analysis = await self.combine_analyses(
            local_analysis,
            wormgpt_result,
            deepseek_result
        )
        
        # Add AI-specific metadata
        enhanced_analysis["ai_analysis_performed"] = {
            "wormgpt_success": wormgpt_result.get("success", False),
            "deepseek_success": deepseek_result.get("success", False),
            "ai_enhanced": True,
            "enhancement_timestamp": time.time()
        }
        
        return enhanced_analysis

    async def test_wormgpt_connection(self) -> bool:
        """Test connection to WormGPT API"""
        try:
            # Test with a simple connection request
            test_result = await self.analyze_with_wormgpt("test", "connection")
            return test_result.get("success", False)
        except:
            return False

    async def test_deepseek_connection(self) -> bool:
        """Test connection to DeepSeek API"""
        try:
            # Test with a simple connection request
            test_result = await self.analyze_with_deepseek("test")
            return test_result.get("success", False)
        except:
            return False

# Global AI integration instance
ai_integration = None

async def get_ai_integration() -> AIIntegration:
    """Get or create the global AI integration instance"""
    global ai_integration
    if ai_integration is None:
        ai_integration = AIIntegration()
        await ai_integration.initialize()
    return ai_integration

# Example usage
async def main():
    ai_integrator = AIIntegration()
    await ai_integrator.initialize()
    
    # Test AI connections
    wormgpt_ok = await ai_integrator.test_wormgpt_connection()
    deepseek_ok = await ai_integrator.test_deepseek_connection()
    
    print(f"WormGPT connection: {'✅' if wormgpt_ok else '❌'}")
    print(f"DeepSeek connection: {'✅' if deepseek_ok else '❌'}")
    
    # Example: Analyze sample code
    sample_code = """
    public boolean authenticateUser(String password) {
        return password.equals("hardcoded_secret_123");
    }
    
    public boolean isRooted() {
        return RootTools.isRooted();
    }
    """
    
    if wormgpt_ok or deepseek_ok:
        enhanced_results = await ai_integrator.perform_enhanced_analysis(sample_code)
        print("\nAI Enhanced Analysis Results:")
        print(json.dumps(enhanced_results, indent=2, ensure_ascii=False))
    
if __name__ == "__main__":
    asyncio.run(main())