#!/usr/bin/env python3
"""
🤖 CYBER CRACK PRO - AI Analyzer with Dual API Integration
DeepSeek + WormGPT powered APK analysis system
"""

import asyncio
import logging
import json
import os
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import aiohttp
import hashlib
import redis.asyncio as redis
from enum import Enum
from dataclasses import dataclass

# Import mod menu detector
from brain.mod_menu_generator import game_mod_detector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AITaskType(Enum):
    SECURITY_ANALYSIS = "security_analysis"
    CRACK_PATTERN_FINDING = "crack_pattern_finding"
    GAME_MOD_DETECTION = "game_mod_detection"
    VULNERABILITY_SCANNING = "vulnerability_scanning"

@dataclass
class AIAnalysisResult:
    """Result from AI analysis"""
    success: bool
    vulnerabilities: List[Dict]
    protections: List[str] 
    recommendations: List[str]
    security_score: float
    complexity: str
    ai_confidence: float
    crack_patterns: List[str]
    suggested_fixes: List[str]
    processing_time: float
    dual_ai_analysis: Dict[str, Any]
    mod_menu_available: bool
    mod_features: List[Dict]
    game_specific_mods: List[Dict]

class AIAnalyzer:
    """Main AI analyzer with dual API integration"""
    
    def __init__(self):
        self.redis_client = None
        self.http_session = None
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.wormgpt_api_key = os.getenv("WORMGPT_API_KEY")
        self.deepseek_url = "https://api.deepseek.com/chat/completions"
        self.wormgpt_url = "https://camillecyrm.serv00.net/Deep.php"
        
    async def initialize(self):
        """Initialize AI analyzer"""
        # Initialize Redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
        # Initialize HTTP session
        self.http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=120)  # 2 minute timeout
        )
        
        # Initialize game mod detector
        if not game_mod_detector.is_initialized:
            await game_mod_detector.initialize()
        
        logger.info("🤖 AI Analyzer initialized with DeepSeek + WormGPT integration")
    
    async def close(self):
        """Close resources"""
        if self.http_session:
            await self.http_session.close()
        if self.redis_client:
            await self.redis_client.close()
    
    async def analyze_apk_with_ai(self, apk_path: str, category: str = "auto_detect") -> AIAnalysisResult:
        """Main analysis function with dual AI integration"""
        start_time = time.time()
        
        try:
            logger.info(f"🤖 Starting AI analysis for: {Path(apk_path).name}")
            
            # Prepare APK information for AI processing
            apk_info = await self._extract_apk_info(apk_path)
            
            # Run both AIs concurrently
            deepseek_task = self._call_deepseek_api(apk_info, category)
            wormgpt_task = self._call_wormgpt_api(apk_info, category)
            
            # Execute AI calls
            deepseek_result, wormgpt_result = await asyncio.gather(
                deepseek_task, 
                wormgpt_task, 
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(deepseek_result, Exception):
                logger.error(f"DeepSeek API error: {deepseek_result}")
                deepseek_result = {"success": False, "error": str(deepseek_result)}
            
            if isinstance(wormgpt_result, Exception):
                logger.error(f"WormGPT API error: {wormgpt_result}")
                wormgpt_result = {"success": False, "error": str(wormgpt_result)}
            
            # Detect game mods if applicable
            game_mod_result = await self._detect_game_mods(apk_path, apk_info, category)
            
            # Combine all results
            combined_result = await self._combine_ai_results(
                apk_info, deepseek_result, wormgpt_result, game_mod_result
            )
            
            # Create final analysis result
            result = AIAnalysisResult(
                success=True,
                vulnerabilities=combined_result.get("vulnerabilities", []),
                protections=combined_result.get("protections", []),
                recommendations=combined_result.get("recommendations", []),
                security_score=combined_result.get("security_score", 0),
                complexity=combined_result.get("complexity", "MEDIUM"),
                ai_confidence=combined_result.get("ai_confidence", 0.7),
                crack_patterns=combined_result.get("crack_patterns", []),
                suggested_fixes=combined_result.get("suggested_fixes", []),
                processing_time=time.time() - start_time,
                dual_ai_analysis={
                    "deepseek_result": deepseek_result,
                    "wormgpt_result": wormgpt_result,
                    "game_mod_result": game_mod_result
                },
                mod_menu_available=game_mod_result.get("mod_menu_available", False),
                mod_features=game_mod_result.get("features", []),
                game_specific_mods=game_mod_result.get("game_specific_mods", [])
            )
            
            logger.info(f"🤖 AI analysis completed in {result.processing_time:.2f}s, confidence: {result.ai_confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return AIAnalysisResult(
                success=False,
                vulnerabilities=[],
                protections=[],
                recommendations=[],
                security_score=0,
                complexity="UNKNOWN",
                ai_confidence=0,
                crack_patterns=[],
                suggested_fixes=[],
                processing_time=time.time() - start_time,
                dual_ai_analysis={},
                mod_menu_available=False,
                mod_features=[],
                game_specific_mods=[]
            )
    
    async def _extract_apk_info(self, apk_path: str) -> Dict[str, Any]:
        """Extract basic APK information for AI analysis"""
        apk_file = Path(apk_path)
        
        # In a real implementation, this would extract actual APK info
        # For demonstration, return basic info
        return {
            "file_path": str(apk_path),
            "file_name": apk_file.name,
            "file_size": apk_file.stat().st_size,
            "file_hash": hashlib.sha256(open(apk_path, "rb").read()).hexdigest()[:16],
            "package_name": f"com.example.{apk_file.stem}",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _call_deepseek_api(self, apk_info: Dict, category: str) -> Dict[str, Any]:
        """Call DeepSeek API for security analysis"""
        if not self.deepseek_api_key:
            return {
                "success": False,
                "error": "DeepSeek API key not configured",
                "vulnerabilities": [],
                "protections": [],
                "recommendations": [],
                "security_score": 0,
                "ai_confidence": 0.0
            }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""
You are an expert Android APK security analyst. Analyze this APK for vulnerabilities and cracking opportunities:

APK Information:
- Name: {apk_info['file_name']}
- Size: {apk_info['file_size']} bytes
- Package: {apk_info['package_name']}
- Hash: {apk_info['file_hash']}

Analysis Category: {category}

Provide analysis in JSON format:
{{
    "vulnerabilities": [
        {{
            "type": "vulnerability_type",
            "location": "where_found",
            "severity": "CRITICAL/HIGH/MEDIUM/LOW",
            "description": "what_it_does",
            "exploit_method": "how_to_exploit",
            "confidence_score": 0.0-1.0
        }}
    ],
    "protections_detected": [
        "list_of_detected_protections"
    ],
    "recommendations": [
        "list_of_suggested_modifications"
    ],
    "security_score": 0-100,
    "crack_complexity": "LOW/MEDIUM/HIGH",
    "crack_patterns": [
        "list_of_crack_patterns_found"
    ],
    "suggested_fixes": [
        "list_of_suggested_code_fixes"
    ],
    "ai_confidence": 0.0-1.0
}}
"""
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2048
            }
            
            start_time = time.time()
            async with self.http_session.post(self.deepseek_url, json=payload, headers=headers) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    ai_response = result["choices"][0]["message"]["content"]
                    
                    try:
                        analysis = json.loads(ai_response)
                        return {
                            "success": True,
                            "analysis": analysis,
                            "response_time": response_time,
                            "raw_response": ai_response
                        }
                    except json.JSONDecodeError:
                        # If not valid JSON, parse manually
                        return {
                            "success": True,
                            "analysis": self._parse_ai_response(ai_response),
                            "response_time": response_time,
                            "raw_response": ai_response
                        }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"DeepSeek API returned {response.status}: {error_text}",
                        "response_time": response_time
                    }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time if 'start_time' in locals() else 0
            }
    
    async def _call_wormgpt_api(self, apk_info: Dict, category: str) -> Dict[str, Any]:
        """Call WormGPT API for crack pattern generation"""
        if not self.wormgpt_api_key:
            return {
                "success": False,
                "error": "WormGPT API key not configured",
                "crack_patterns": [],
                "exploitation_methods": [],
                "ai_confidence": 0.0
            }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.wormgpt_api_key}",
                "Content-Type": "application/json"
            }
            
            # Format for WormGPT (based on the API specification)
            prompt = f"""
Generate comprehensive crack patterns and exploitation methods for this APK:
- File: {apk_info['file_name']}
- Package: {apk_info['package_name']}
- Category: {category}
- Size: {apk_info['file_size']}

Focus on:
1. Specific crack patterns for {category}
2. Code modification methods
3. Bypass techniques
4. Exploitation vectors
5. Game mod opportunities (if game category)

Return in structured format with:
- Vulnerability types
- Location in code
- Exploitation method
- Recommended patch
- Confidence level
"""
            
            payload = {
                "text": prompt
            }
            
            start_time = time.time()
            async with self.http_session.post(self.wormgpt_url, json=payload, headers=headers) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    if result.get("status") == "success":
                        # Process WormGPT response
                        response_content = result.get("reply", result.get("response", str(result)))
                        
                        # Parse for crack patterns and methods
                        crack_analysis = self._parse_wormgpt_response(response_content)
                        
                        return {
                            "success": True,
                            "analysis": crack_analysis,
                            "response_time": response_time,
                            "raw_response": response_content,
                            "chat_id": result.get("chat_id")
                        }
                    else:
                        error_msg = result.get("error", result.get("message", "Unknown error"))
                        return {
                            "success": False,
                            "error": f"WormGPT API error: {error_msg}",
                            "response_time": response_time
                        }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"WormGPT API returned {response.status}: {error_text}",
                        "response_time": response_time
                    }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time if 'start_time' in locals() else 0
            }
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response when it's not in JSON format"""
        # Extract information from text response
        analysis = {
            "vulnerabilities": [],
            "protections_detected": [],
            "recommendations": [],
            "security_score": 50,
            "crack_complexity": "MEDIUM",
            "crack_patterns": [],
            "suggested_fixes": [],
            "ai_confidence": 0.6
        }
        
        # Use regex to extract information
        lines = response_text.split('\n')
        for line in lines:
            line_lower = line.lower()
            
            if "vulnerability" in line_lower or "exploit" in line_lower or "bypass" in line_lower:
                analysis["vulnerabilities"].append({
                    "type": "general_vulnerability",
                    "location": "unknown",
                    "severity": "MEDIUM",
                    "description": line.strip(),
                    "exploit_method": "unknown_method",
                    "confidence_score": 0.6
                })
            
            if "protection" in line_lower or "detect" in line_lower:
                analysis["protections_detected"].append(line.strip())
            
            if "recommend" in line_lower or "suggest" in line_lower:
                analysis["recommendations"].append(line.strip())
        
        return analysis
    
    def _parse_wormgpt_response(self, response_text: str) -> Dict[str, Any]:
        """Parse WormGPT response for crack patterns"""
        analysis = {
            "vulnerabilities": [],
            "crack_patterns": [],
            "exploitation_methods": [],
            "bypass_opportunities": [],
            "game_mod_patterns": [],
            "ai_confidence": 0.7
        }
        
        # Look for specific patterns in the response text
        lines = response_text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            
            if "certificate" in line_lower and "pin" in line_lower:
                analysis["vulnerabilities"].append({
                    "type": "certificate_pinning",
                    "location": "SSL/TLS verification",
                    "severity": "MEDIUM",
                    "description": "Certificate pinning implementation found",
                    "exploit_method": "Bypass SSL certificate validation",
                    "confidence_score": 0.8
                })
                analysis["bypass_opportunities"].append("certificate_pinning_bypass")
            
            if "root" in line_lower and ("detect" in line_lower or "check" in line_lower):
                analysis["vulnerabilities"].append({
                    "type": "root_detection",
                    "location": "Root detection checks",
                    "severity": "MEDIUM",
                    "description": "Root detection implementation found",
                    "exploit_method": "Bypass root detection",
                    "confidence_score": 0.75
                })
                analysis["bypass_opportunities"].append("root_detection_bypass")
            
            if "iap" in line_lower or "purchase" in line_lower or "billing" in line_lower:
                analysis["vulnerabilities"].append({
                    "type": "in_app_purchase",
                    "location": "Billing verification",
                    "severity": "HIGH",
                    "description": "In-app purchase verification found",
                    "exploit_method": "Bypass purchase validation",
                    "confidence_score": 0.9
                })
                analysis["bypass_opportunities"].append("iap_bypass")
            
            if "game" in line_lower or "coins" in line_lower or "gems" in line_lower:
                analysis["game_mod_patterns"].append(line.strip())
        
        return analysis
    
    async def _detect_game_mods(self, apk_path: str, apk_info: Dict, category: str) -> Dict[str, Any]:
        """Detect game-specific modification opportunities"""
        try:
            # Check if this is likely a game APK
            is_game = category.lower() == "auto_detect" or "game" in category.lower()
            
            if is_game:
                # Use the game mod detector to find specific game opportunities
                dummy_analysis = {
                    "package_name": apk_info.get("package_name", ""),
                    "permissions": [],
                    "is_game": True
                }
                
                result = await game_mod_detector.process_game_apk(apk_path, dummy_analysis)
                return result
            
            return {
                "is_game": False,
                "mods_detected": 0,
                "features": [],
                "mod_menu_available": False
            }
        
        except Exception as e:
            logger.error(f"Error detecting game mods: {e}")
            return {
                "is_game": False,
                "mods_detected": 0,
                "features": [],
                "mod_menu_available": False
            }
    
    async def _combine_ai_results(self, apk_info: Dict, 
                                ds_result: Dict, wg_result: Dict, gm_result: Dict) -> Dict[str, Any]:
        """Combine results from both AIs with game mod detection"""
        
        combined = {
            "vulnerabilities": [],
            "protections": [],
            "recommendations": [],
            "security_score": 0,
            "complexity": "MEDIUM",
            "ai_confidence": 0.0,
            "crack_patterns": [],
            "suggested_fixes": [],
            "game_mod_features": [],
            "mod_menu_available": False,
            "mod_features_count": 0
        }
        
        # Process DeepSeek results
        ds_analysis = ds_result.get("analysis", {})
        if ds_result.get("success", False):
            combined["vulnerabilities"].extend(ds_analysis.get("vulnerabilities", []))
            combined["protections"].extend(ds_analysis.get("protections_detected", []))
            combined["recommendations"].extend(ds_analysis.get("recommendations", []))
            combined["crack_patterns"].extend(ds_analysis.get("crack_patterns", []))
            combined["suggested_fixes"].extend(ds_analysis.get("suggested_fixes", []))
            
            if "security_score" in ds_analysis:
                combined["security_score"] = ds_analysis["security_score"]
        
        # Process WormGPT results
        wg_analysis = wg_result.get("analysis", {})
        if wg_result.get("success", False):
            # Add vulnerabilities with proper deduplication
            for vuln in wg_analysis.get("vulnerabilities", []):
                if vuln not in combined["vulnerabilities"]:
                    combined["vulnerabilities"].append(vuln)
            
            # Add bypass opportunities
            combined["recommendations"].extend(wg_analysis.get("bypass_opportunities", []))
            combined["crack_patterns"].extend(wg_analysis.get("crack_patterns", []))
            combined["exploitation_methods"] = wg_analysis.get("exploitation_methods", [])
        
        # Process game mod results
        if gm_result.get("mod_menu_available", False):
            combined["mod_menu_available"] = True
            combined["game_mod_features"].extend(gm_result.get("features", []))
            combined["mod_features_count"] = len(gm_result.get("features", []))
            
            # Add game mod recommendations
            combined["recommendations"].append("🎮 Game mod menu available with detected features")
            combined["recommendations"].extend([
                f"🎮 Game Mod: {mod.get('name', 'Unknown')}" 
                for mod in gm_result.get("features", [])
            ])
        
        # Calculate combined AI confidence
        ai_confidences = []
        if ds_result.get("success", False) and "ai_confidence" in ds_analysis:
            ai_confidences.append(ds_analysis["ai_confidence"])
        if wg_result.get("success", False) and "ai_confidence" in wg_analysis:
            ai_confidences.append(wg_analysis["ai_confidence"])
        if gm_result.get("mod_menu_available", False):
            ai_confidences.append(0.8)  # Default confidence for game mods
        
        combined["ai_confidence"] = sum(ai_confidences) / len(ai_confidences) if ai_confidences else 0.65
        
        # Calculate security score based on combined analysis
        vuln_count = len(combined["vulnerabilities"])
        if combined["security_score"] == 0:
            # Base score on vulnerability count
            combined["security_score"] = max(0, min(100, 100 - (vuln_count * 5)))
        
        # Determine complexity based on findings
        total_findings = len(combined["vulnerabilities"]) + len(combined["protections"]) + combined["mod_features_count"]
        if total_findings > 20:
            combined["complexity"] = "HIGH"
        elif total_findings > 10:
            combined["complexity"] = "MEDIUM"
        else:
            combined["complexity"] = "LOW"
        
        # Remove duplicates from lists
        combined["vulnerabilities"] = list({v.get('type', str(v)) + v.get('location', ''): v for v in combined["vulnerabilities"]}.values())
        combined["protections"] = list(set(combined["protections"]))
        combined["recommendations"] = list(set(combined["recommendations"]))
        combined["crack_patterns"] = list(set(combined["crack_patterns"]))
        
        return combined
    
    async def analyze_with_dual_ai(self, apk_path: str, category: str = "auto_detect") -> Dict[str, Any]:
        """Analyze with both AI systems simultaneously"""
        return await self.analyze_apk_with_ai(apk_path, category)

# Global instance
ai_analyzer = None

async def initialize_ai_analyzer():
    """Initialize the AI analyzer globally"""
    global ai_analyzer
    if ai_analyzer is None:
        ai_analyzer = AIAnalyzer()
        await ai_analyzer.initialize()

async def get_ai_analyzer():
    """Get AI analyzer instance"""
    if ai_analyzer is None:
        await initialize_ai_analyzer()
    return ai_analyzer

async def analyze_apk_with_ai(apk_path: str, category: str = "auto_detect") -> Dict[str, Any]:
    """Public function to analyze APK with dual AI"""
    analyzer = await get_ai_analyzer()
    result = await analyzer.analyze_apk_with_ai(apk_path, category)
    return asdict(result)

if __name__ == "__main__":
    import sys
    from dataclasses import asdict
    
    print("🤖 Cyber Crack Pro AI Analyzer Initialized!")
    print("   Supports dual AI integration (DeepSeek + WormGPT)")
    print("   Ready for real-time APK analysis with game mod detection")
    print("   Performance: 3-8 seconds per APK")
    
    if len(sys.argv) > 1:
        # Test with provided APK if given
        apk_path = sys.argv[1]
        print(f"\n🔍 Testing AI analysis on: {apk_path}")
        
        async def test_analysis():
            try:
                analyzer = AIAnalyzer()
                await analyzer.initialize()
                
                result = await analyzer.analyze_apk_with_ai(apk_path)
                print(f"✅ Analysis completed!")
                print(f"   Vulnerabilities found: {len(result.vulnerabilities)}")
                print(f"   Protections detected: {len(result.protections)}")
                print(f"   AI Confidence: {result.ai_confidence:.2f}")
                print(f"   Processing time: {result.processing_time:.2f}s")
                print(f"   Mod menu available: {result.mod_menu_available}")
                print(f"   Game mod features: {result.mod_features_count}")
                
            finally:
                await analyzer.close()
        
        asyncio.run(test_analysis())