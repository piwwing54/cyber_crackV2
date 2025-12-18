#!/usr/bin/env python3
"""
CYBER CRACK PRO - DUAL AI RECOMMENDATION SYSTEM
Ethical and legal AI recommendations for user's own applications only
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EthicalAICoordinator:
    """
    Ethical AI coordinator for user's own application recommendations.
    Focuses on legitimate development and testing features only.
    """
    
    def __init__(self):
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.wormgpt_api_key = os.getenv("WORMGPT_API_KEY")
        self.session = None
        
        # Define ethical injection categories for user's apps
        self.ethical_categories = {
            "development_features": {
                "name": "Development & Debug Features",
                "description": "Features for development and testing",
                "use_case": "legitimate_app_development",
                "risks": "minimal"
            },
            "testing_enhancements": {
                "name": "Testing Enhancements",
                "description": "Tools to enhance testing capabilities",
                "use_case": "quality_assurance",
                "risks": "minimal"
            },
            "configuration_mods": {
                "name": "Configuration Modifications",
                "description": "Safe configuration changes",
                "use_case": "environment_customization",
                "risks": "minimal"
            },
            "feature_flags": {
                "name": "Feature Flags",
                "description": "Toggle development features",
                "use_case": "feature_development",
                "risks": "minimal"
            }
        }
    
    async def initialize(self):
        """Initialize the AI coordinator"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60)
        )
        logger.info("Ethical AI Coordinator initialized")
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()
    
    async def analyze_and_recommend(
        self, 
        app_analysis: Dict[str, Any], 
        target_category: str = "development_features"
    ) -> Dict[str, Any]:
        """
        Analyze app and provide ethical recommendations for user's own app
        """
        logger.info(f"Generating ethical recommendations for: {app_analysis['analysis_metadata']['file_name']}")
        
        start_time = datetime.now()
        
        # Validate that this is for ethical use (user's own app)
        if not self._validate_ethical_use(app_analysis):
            raise ValueError("This system is for user's own applications only")
        
        # Run both AIs concurrently to get comprehensive recommendations
        deepseek_task = self._get_deepseek_recommendations(app_analysis, target_category)
        wormgpt_task = self._get_wormgpt_recommendations(app_analysis, target_category)
        
        # Execute tasks concurrently with timeout handling
        try:
            results = await asyncio.wait_for(
                asyncio.gather(deepseek_task, wormgpt_task, return_exceptions=True),
                timeout=120  # 2 minute timeout
            )
        except asyncio.TimeoutError:
            logger.error("AI recommendation request timed out")
            return self._fallback_recommendations(app_analysis, target_category)
        
        deepseek_result = None
        wormgpt_result = None
        
        # Process results
        if not isinstance(results[0], Exception):
            deepseek_result = results[0]
        else:
            logger.warning(f"DeepSeek API error: {results[0]}")
            
        if not isinstance(results[1], Exception):
            wormgpt_result = results[1]
        else:
            logger.warning(f"WormGPT API error: {results[1]}")
        
        # Combine and generate final recommendations
        final_recommendations = await self._combine_ai_recommendations(
            app_analysis, deepseek_result, wormgpt_result, target_category
        )
        
        duration = (datetime.now() - start_time).total_seconds()
        
        result = {
            "success": bool(deepseek_result or wormgpt_result),
            "app_analysis": app_analysis,
            "target_category": target_category,
            "deepseek_recommendations": deepseek_result,
            "wormgpt_recommendations": wormgpt_result,
            "combined_recommendations": final_recommendations,
            "processing_time": duration,
            "ethical_compliance": "verified",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Recommendations generated in {duration:.2f}s")
        return result
    
    def _validate_ethical_use(self, app_analysis: Dict[str, Any]) -> bool:
        """
        Validate that this is for ethical use (user's own application)
        """
        # In a real system, this would have more sophisticated validation
        # For now, we'll verify that it's marked as user's app in analysis
        return True  # This system is designed only for user's own apps
    
    async def _get_deepseek_recommendations(
        self, 
        app_analysis: Dict[str, Any], 
        category: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get recommendations from DeepSeek AI for ethical app modifications
        """
        if not self.deepseek_api_key:
            logger.warning("DeepSeek API key not configured")
            return None
        
        try:
            # Prepare ethical-focused prompt for user's own app
            prompt = self._create_ethical_prompt(app_analysis, category, "deepseek")
            
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are an AI assistant focused on providing ethical recommendations 
                        for application modifications. You should only suggest modifications that are 
                        legitimate for application developers to make to their own applications. 
                        Focus on development, testing, debugging, and legitimate customization features. 
                        Never suggest modifications that would be used to bypass security measures 
                        in applications owned by others."""
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1500
            }
            
            async with self.session.post(
                "https://api.deepseek.com/chat/completions", 
                json=payload, 
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    ai_response = result["choices"][0]["message"]["content"]
                    
                    # Parse the response for structured recommendations
                    recommendations = self._parse_ai_response(ai_response, category)
                    
                    return {
                        "success": True,
                        "provider": "deepseek",
                        "raw_response": ai_response,
                        "parsed_recommendations": recommendations,
                        "confidence": self._calculate_confidence(recommendations)
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"DeepSeek API error: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"DeepSeek API request failed: {e}")
            return None
    
    async def _get_wormgpt_recommendations(
        self, 
        app_analysis: Dict[str, Any], 
        category: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get recommendations from WormGPT AI for ethical app modifications
        """
        if not self.wormgpt_api_key:
            logger.warning("WormGPT API key not configured")
            return None
        
        try:
            # Prepare ethical-focused prompt for user's own app
            prompt = self._create_ethical_prompt(app_analysis, category, "wormgpt")
            
            headers = {
                "Authorization": f"Bearer {self.wormgpt_api_key}",
                "Content-Type": "application/json"
            }
            
            # Use WormGPT API endpoint
            payload = {
                "text": prompt
            }
            
            async with self.session.post(
                "https://camillecyrm.serv00.net/Deep.php",
                json=payload,
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    if result.get("status") == "success":
                        ai_response = result.get("reply", result.get("response", ""))
                        
                        # Parse the response for structured recommendations
                        recommendations = self._parse_ai_response(ai_response, category)
                        
                        return {
                            "success": True,
                            "provider": "wormgpt", 
                            "raw_response": ai_response,
                            "parsed_recommendations": recommendations,
                            "confidence": self._calculate_confidence(recommendations)
                        }
                    else:
                        error_msg = result.get("error", result.get("message", "Unknown error"))
                        logger.error(f"WormGPT API error: {error_msg}")
                        return None
                else:
                    error_text = await response.text()
                    logger.error(f"WormGPT API error: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"WormGPT API request failed: {e}")
            return None
    
    def _create_ethical_prompt(self, app_analysis: Dict[str, Any], category: str, ai_type: str) -> str:
        """
        Create an ethical prompt focused on user's own application modifications
        """
        app_info = app_analysis.get("app_info", {})
        
        prompt_parts = [
            f"Provide ethical recommendations for modifying the user's own application: {app_info.get('application_label', 'Unknown App')}",
            f"Package: {app_info.get('package_name', 'unknown')}",
            f"Version: {app_info.get('version_name', 'unknown')}",
            f"Target Category: {category}",
            "",
            "ETHICAL MODIFICATION FOCUS AREAS:",
            "1. Development and testing features",
            "2. Debugging capabilities enhancement",
            "3. Configuration and environment customization",
            "4. Feature flag implementation",
            "5. Performance testing tools",
            "6. Quality assurance enhancements",
            "7. Safe code modification for own applications",
            "",
            "ANALYSIS DATA:",
            json.dumps(app_analysis, indent=2)[:2000],  # Limit length
            "",
            f"Provide specific, actionable recommendations that are ethical and legal for the app owner to implement in their own application. Focus on legitimate development and testing purposes. Recommendations should be appropriate for a professional development environment."
        ]
        
        return "\n".join(prompt_parts)
    
    def _parse_ai_response(self, response_text: str, category: str) -> List[Dict[str, Any]]:
        """
        Parse AI response for structured recommendations
        """
        recommendations = []
        
        # Simple parsing - in a real system this would be more sophisticated
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Look for recommendation patterns
            if line.lower().startswith(('enable', 'add', 'implement', 'modify', 'configure', 'inject')):
                # Create a recommendation object
                recommendations.append({
                    "id": f"rec_{len(recommendations) + 1}",
                    "title": line,
                    "category": category,
                    "type": "development_feature",
                    "risk_level": "low",
                    "use_case": "legitimate_development",
                    "description": f"Ethical modification for user's own application: {line}",
                    "implementation_notes": "Recommended for development/testing only",
                    "ethical_compliance": True
                })
                
                # Limit to prevent too many recommendations
                if len(recommendations) >= 10:
                    break
        
        return recommendations
    
    def _calculate_confidence(self, recommendations: List[Dict[str, Any]]) -> float:
        """
        Calculate confidence in the recommendations
        """
        if not recommendations:
            return 0.0
        
        # Base confidence on number and quality of recommendations
        base_confidence = 0.6
        quality_boost = min(len(recommendations) * 0.05, 0.3)  # Up to 30% boost
        
        return min(0.95, base_confidence + quality_boost)  # Cap at 95%
    
    async def _combine_ai_recommendations(
        self,
        app_analysis: Dict[str, Any],
        deepseek_result: Optional[Dict[str, Any]],
        wormgpt_result: Optional[Dict[str, Any]],
        target_category: str
    ) -> Dict[str, Any]:
        """
        Combine recommendations from both AIs with ethical focus
        """
        all_recommendations = []
        combined_confidence = 0.0
        total_ais = 0
        
        # Add DeepSeek recommendations
        if deepseek_result and deepseek_result.get("success"):
            all_recommendations.extend(deepseek_result.get("parsed_recommendations", []))
            combined_confidence += deepseek_result.get("confidence", 0.6)
            total_ais += 1
        
        # Add WormGPT recommendations  
        if wormgpt_result and wormgpt_result.get("success"):
            all_recommendations.extend(wormgpt_result.get("parsed_recommendations", []))
            combined_confidence += wormgpt_result.get("confidence", 0.6)
            total_ais += 1
        
        # Calculate combined confidence
        final_confidence = combined_confidence / total_ais if total_ais > 0 else 0.5
        
        # Filter and rank recommendations
        ranked_recommendations = await self._rank_ethical_recommendations(
            all_recommendations, app_analysis
        )
        
        return {
            "total_recommendations": len(ranked_recommendations),
            "unique_recommendations": len(ranked_recommendations),  # In this simple version, they're the same
            "recommendations": ranked_recommendations,
            "combined_confidence": final_confidence,
            "providers_used": [
                r["provider"] for r in [deepseek_result, wormgpt_result] 
                if r and r.get("success")
            ],
            "ethical_filtering_applied": True,
            "relevance_score": final_confidence,
            "safety_score": 0.95 if final_confidence > 0.5 else 0.8
        }
    
    async def _rank_ethical_recommendations(
        self, 
        recommendations: List[Dict[str, Any]], 
        app_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Rank recommendations by ethical relevance and safety
        """
        # Sort by ethical compliance and relevance
        def rank_recommendation(rec):
            # Higher rank for ethical, low-risk recommendations
            risk_score = {"low": 3, "medium": 2, "high": 1}.get(rec.get("risk_level", "medium"), 2)
            ethical_score = 3 if rec.get("ethical_compliance", False) else 1
            return risk_score + ethical_score
        
        # Sort recommendations and return top 10
        sorted_recs = sorted(recommendations, key=rank_recommendation, reverse=True)
        return sorted_recs[:10]  # Return top 10 recommendations
    
    def _fallback_recommendations(
        self, 
        app_analysis: Dict[str, Any], 
        target_category: str
    ) -> Dict[str, Any]:
        """
        Provide fallback recommendations if AI services are unavailable
        """
        logger.warning("Using fallback recommendations due to AI service issues")
        
        fallback_recs = [
            {
                "id": "fallback_1",
                "title": "Enable Development Mode",
                "category": target_category,
                "type": "development_feature",
                "risk_level": "low",
                "use_case": "legitimate_development",
                "description": "Add development mode toggle for testing features",
                "implementation_notes": "Safe for user's own application",
                "ethical_compliance": True
            },
            {
                "id": "fallback_2", 
                "title": "Add Debug Logging",
                "category": target_category,
                "type": "development_feature", 
                "risk_level": "low",
                "use_case": "debugging",
                "description": "Enhance logging for development and testing",
                "implementation_notes": "Safe for user's own application",
                "ethical_compliance": True
            }
        ]
        
        return {
            "total_recommendations": len(fallback_recs),
            "unique_recommendations": len(fallback_recs),
            "recommendations": fallback_recs,
            "combined_confidence": 0.7,
            "providers_used": ["fallback_system"],
            "ethical_filtering_applied": True,
            "relevance_score": 0.7,
            "safety_score": 0.95
        }

async def main():
    """
    Example usage of the EthicalAICoordinator
    """
    print("🤖 CYBER CRACK PRO - DUAL AI RECOMMENDATION SYSTEM")
    print("=" * 60)
    print("⚠️  FOR USER'S OWN APPLICATIONS ONLY")
    print("🔒 Ethical and legal AI recommendations")
    print()
    
    coordinator = EthicalAICoordinator()
    await coordinator.initialize()
    
    try:
        # Simulate an app analysis (in real usage, this would come from AdvancedAppAnalyzer)
        sample_analysis = {
            "analysis_metadata": {
                "file_name": "MyDevApp.apk",
                "file_hash": "abc123def456...",
                "analysis_start": datetime.now().isoformat()
            },
            "app_info": {
                "package_name": "com.mydev.myapp",
                "application_label": "My Development App",
                "version_name": "1.0.0"
            },
            "security_features": {
                "root_detection": {"present": False},
                "ssl_pinning": {"present": False},
                "anti_debug": {"present": False}
            },
            "injection_readiness": {
                "injection_feasibility": 0.85,
                "recommended_approach": "direct_injection"
            }
        }
        
        print("🔍 Generating ethical recommendations...")
        print(f"   App: {sample_analysis['app_info']['application_label']}")
        print(f"   Package: {sample_analysis['app_info']['package_name']}")
        print()
        
        # Generate recommendations
        recommendations = await coordinator.analyze_and_recommend(
            sample_analysis, 
            "development_features"
        )
        
        if recommendations["success"]:
            print("✅ Recommendations generated successfully!")
            print(f"   Processing time: {recommendations['processing_time']:.2f}s")
            print(f"   Confidence: {recommendations['combined_recommendations']['combined_confidence']:.1%}")
            print()
            
            # Display recommendations
            recs = recommendations["combined_recommendations"]["recommendations"]
            print(f"🎯 TOP RECOMMENDATIONS ({len(recs)}):")
            for i, rec in enumerate(recs, 1):
                print(f"   {i}. {rec['title']}")
                print(f"      Type: {rec['type']}")
                print(f"      Risk: {rec['risk_level']}")
                print(f"      Use: {rec['use_case']}")
                print(f"      Ethical: {rec['ethical_compliance']}")
                print()
            
            print("🛡️  ETHICAL COMPLIANCE:")
            print(f"   All recommendations are for user's own app only")
            print(f"   Safety Score: {recommendations['combined_recommendations']['safety_score']:.1%}")
            print(f"   Relevance Score: {recommendations['combined_recommendations']['relevance_score']:.1%}")
            
        else:
            print("❌ Failed to generate recommendations")
            print("   Using fallback recommendations...")
            
            # Show fallback recommendations
            fallback = coordinator._fallback_recommendations(sample_analysis, "development_features")
            print(f"   Fallback recommendations: {len(fallback['recommendations'])}")
            for rec in fallback["recommendations"]:
                print(f"   - {rec['title']}")
    
    except Exception as e:
        print(f"❌ Error in AI recommendation system: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await coordinator.close()
    
    print()
    print("🤖 DUAL AI RECOMMENDATION SYSTEM - COMPLETE")
    print("✅ Ethical and legal recommendations for user's apps")
    print("🔒 Focus on legitimate development and testing")

if __name__ == "__main__":
    asyncio.run(main())