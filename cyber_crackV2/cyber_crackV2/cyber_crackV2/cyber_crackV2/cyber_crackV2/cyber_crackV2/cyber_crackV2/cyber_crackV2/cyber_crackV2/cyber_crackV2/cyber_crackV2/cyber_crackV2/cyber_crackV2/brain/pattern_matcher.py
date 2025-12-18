#!/usr/bin/env python3
"""
🔍 Pattern Matcher for Cyber Crack Pro
Smart pattern matching and vulnerability detection system
"""

import re
import logging
import json
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import zipfile
import tempfile
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MatchType(Enum):
    LOGIN_BYPASS = "login_bypass"
    IAP_BYPASS = "iap_bypass"
    ROOT_BYPASS = "root_bypass"
    SSL_BYPASS = "ssl_bypass"
    DEBUG_BYPASS = "debug_bypass"
    LICENSE_BYPASS = "license_bypass"
    PREMIUM_UNLOCK = "premium_unlock"
    GAME_MOD = "game_mod"

class PatternMatcher:
    """Advanced pattern matching system"""
    
    def __init__(self, knowledge_base_path: str = "brain/knowledge_base.json"):
        self.knowledge_base = self._load_knowledge_base(knowledge_base_path)
        self.patterns = self._compile_patterns()
        self.cache = {}
    
    def _load_knowledge_base(self, kb_path: str) -> Dict:
        """Load knowledge base from JSON file"""
        try:
            with open(kb_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Knowledge base not found at {kb_path}, using defaults")
            return self._get_default_knowledge_base()
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in knowledge base: {kb_path}")
            return self._get_default_knowledge_base()
    
    def _get_default_knowledge_base(self) -> Dict:
        """Get default knowledge base if file is missing"""
        return {
            "crack_patterns": {
                "login_bypass": [
                    {
                        "name": "AUTO_LOGIN_BYPASS",
                        "pattern": "const\\/4 v0, 0x0",
                        "replacement": "const\\/4 v0, 0x1",
                        "description": "Force authenticate method to always return true",
                        "severity": "CRITICAL",
                        "category": "authentication"
                    }
                ],
                "iap_bypass": [
                    {
                        "name": "PURCHASE_VERIFICATION_BYPASS",
                        "pattern": "verifyPurchase.*Z",
                        "replacement": "const\\/4 v0, 0x1\\nreturn v0",
                        "description": "Bypass in-app purchase verification",
                        "severity": "CRITICAL", 
                        "category": "billing"
                    }
                ]
            }
        }
    
    def _compile_patterns(self) -> Dict:
        """Compile regex patterns for faster matching"""
        compiled = {}
        
        for category, patterns in self.knowledge_base.get("crack_patterns", {}).items():
            for pattern_info in patterns:
                try:
                    # Compile the pattern if it's a valid regex
                    compiled_pattern = re.compile(pattern_info["pattern"], re.IGNORECASE)
                    compiled[f"{category}:{pattern_info['name']}"] = {
                        "regex": compiled_pattern,
                        "info": pattern_info
                    }
                except re.error as e:
                    logger.warning(f"Invalid regex pattern {pattern_info['pattern']}: {e}")
        
        return compiled
    
    def analyze_apk_patterns(self, apk_path: str) -> Dict[str, Any]:
        """Analyze APK for known patterns"""
        results = {
            "matches": [],
            "vulnerabilities": [],
            "recommended_fixes": [],
            "security_score": 0,
            "analysis_time": 0
        }
        
        try:
            start_time = time.time()
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract APK
                extracted_path = Path(temp_dir)
                self._extract_apk(apk_path, extracted_path)
                
                # Search for patterns
                results["matches"] = self._search_patterns_in_directory(extracted_path)
                
                # Identify vulnerabilities
                results["vulnerabilities"] = self._identify_vulnerabilities(results["matches"])
                
                # Generate recommendations
                results["recommended_fixes"] = self._generate_recommendations(results["vulnerabilities"])
                
                # Calculate security score
                results["security_score"] = self._calculate_security_score(results["vulnerabilities"])
                results["analysis_time"] = time.time() - start_time
                
        except Exception as e:
            logger.error(f"Error analyzing APK patterns: {e}")
            results["error"] = str(e)
        
        return results
    
    def _extract_apk(self, apk_path: str, extract_to: Path):
        """Extract APK to directory"""
        with zipfile.ZipFile(apk_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    
    def _search_patterns_in_directory(self, directory: Path) -> List[Dict]:
        """Search for patterns in all files in directory"""
        matches = []
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and self._is_text_file(file_path):
                try:
                    file_matches = self._search_patterns_in_file(file_path)
                    matches.extend(file_matches)
                except Exception as e:
                    logger.warning(f"Error searching patterns in {file_path}: {e}")
        
        return matches
    
    def _search_patterns_in_file(self, file_path: Path) -> List[Dict]:
        """Search for patterns in a single file"""
        matches = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check against all compiled patterns
            for pattern_key, pattern_data in self.patterns.items():
                regex = pattern_data["regex"]
                info = pattern_data["info"]
                
                # Find all matches
                for match in regex.finditer(content):
                    match_entry = {
                        "pattern_name": info["name"],
                        "pattern_type": self._get_pattern_type(info["name"]),
                        "matched_text": match.group(),
                        "position": match.start(),
                        "severity": info.get("severity", "MEDIUM"),
                        "description": info.get("description", ""),
                        "category": info.get("category", "general"),
                        "file_path": str(file_path),
                        "suggested_replacement": info.get("replacement", "")
                    }
                    matches.append(match_entry)
        
        except Exception as e:
            logger.warning(f"Error reading file {file_path}: {e}")
        
        return matches
    
    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is a text file that should be analyzed"""
        text_extensions = {'.txt', '.smali', '.java', '.xml', '.json', '.js', '.html', '.css', '.py', '.cpp', '.c', '.h', '.go', '.rs', '.gradle', '.properties'}
        return file_path.suffix.lower() in text_extensions
    
    def _get_pattern_type(self, pattern_name: str) -> MatchType:
        """Get pattern type from pattern name"""
        pattern_lower = pattern_name.lower()
        
        if "login" in pattern_lower or "auth" in pattern_lower:
            return MatchType.LOGIN_BYPASS
        elif "purchase" in pattern_lower or "iap" in pattern_lower or "billing" in pattern_lower:
            return MatchType.IAP_BYPASS
        elif "root" in pattern_lower:
            return MatchType.ROOT_BYPASS
        elif "ssl" in pattern_lower or "certificate" in pattern_lower or "pinning" in pattern_lower:
            return MatchType.SSL_BYPASS
        elif "debug" in pattern_lower:
            return MatchType.DEBUG_BYPASS
        elif "license" in pattern_lower or "verify" in pattern_lower or "check" in pattern_lower:
            return MatchType.LICENSE_BYPASS
        elif "premium" in pattern_lower or "unlock" in pattern_lower:
            return MatchType.PREMIUM_UNLOCK
        elif "game" in pattern_lower or "coin" in pattern_lower or "level" in pattern_lower:
            return MatchType.GAME_MOD
        else:
            return MatchType.LOGIN_BYPASS  # Default category
    
    def _identify_vulnerabilities(self, matches: List[Dict]) -> List[Dict]:
        """Identify vulnerabilities from pattern matches"""
        vulnerabilities = []
        
        for match in matches:
            vulnerability = {
                "type": match["pattern_type"].value,
                "severity": match["severity"],
                "description": match["description"],
                "location": {
                    "file": match["file_path"],
                    "position": match["position"],
                    "matched_code": match["matched_text"]
                },
                "recommendation": f"Apply fix: {match['suggested_replacement']}",
                "confidence": self._calculate_match_confidence(match)
            }
            vulnerabilities.append(vulnerability)
        
        return vulnerabilities
    
    def _calculate_match_confidence(self, match: Dict) -> float:
        """Calculate confidence level for a match"""
        # Simple confidence calculation based on match quality
        base_score = 0.7  # Base confidence
        
        # Increase confidence for specific patterns
        if "critical" in match["severity"].lower():
            base_score += 0.2
        elif "high" in match["severity"].lower():
            base_score += 0.1
        
        # Adjust based on file type and location
        file_path_lower = match["file_path"].lower()
        if any(keyword in file_path_lower for keyword in ["auth", "login", "security", "billing"]):
            base_score += 0.1
        
        return min(base_score, 1.0)  # Cap at 1.0
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[Dict]:
        """Generate recommendations for fixing vulnerabilities"""
        recommendations = []
        
        for vuln in vulnerabilities:
            rec = {
                "vulnerability_type": vuln["type"],
                "description": vuln["description"],
                "location": vuln["location"],
                "fix_method": self._get_fix_method(vuln["type"]),
                "fix_code": self._get_fix_code(vuln["type"]),
                "complexity": "LOW" if vuln["severity"] in ["LOW", "MEDIUM"] else "MEDIUM"
            }
            recommendations.append(rec)
        
        return recommendations
    
    def _get_fix_method(self, vuln_type: str) -> str:
        """Get appropriate fix method for vulnerability type"""
        fix_methods = {
            "login_bypass": "Modify authentication method to return success",
            "iap_bypass": "Bypass in-app purchase validation",
            "root_bypass": "Disable root detection checks",
            "ssl_bypass": "Remove certificate pinning",
            "debug_bypass": "Remove anti-debug checks",
            "license_bypass": "Bypass license verification",
            "premium_unlock": "Unlock premium features",
            "game_mod": "Apply game modifications"
        }
        return fix_methods.get(vuln_type, "Apply generic patch")
    
    def _get_fix_code(self, vuln_type: str) -> str:
        """Get code snippet for fixing vulnerability"""
        fix_codes = {
            "login_bypass": "const/4 v0, 0x1\nreturn v0",
            "iap_bypass": "const/4 v0, 0x1\nreturn v0", 
            "root_bypass": "const/4 v0, 0x0\nreturn v0",
            "ssl_bypass": "return-void",
            "debug_bypass": "const/4 v0, 0x0\nreturn v0",
            "license_bypass": "const/4 v0, 0x1\nreturn v0",
            "premium_unlock": "const/4 v0, 0x1\nreturn v0",
            "game_mod": "const/16 v0, 0x2710\nreturn v0"  # Large number for coins
        }
        return fix_codes.get(vuln_type, "nop")
    
    def _calculate_security_score(self, vulnerabilities: List[Dict]) -> int:
        """Calculate security score based on vulnerabilities"""
        base_score = 100
        
        for vuln in vulnerabilities:
            severity = vuln["severity"].upper()
            if severity == "CRITICAL":
                base_score -= 25
            elif severity == "HIGH":
                base_score -= 15
            elif severity == "MEDIUM":
                base_score -= 8
            elif severity == "LOW":
                base_score -= 3
        
        return max(0, min(100, base_score))
    
    def get_crack_recommendations(self, analysis_results: Dict) -> List[Dict]:
        """Get recommendations for cracking based on analysis"""
        recommendations = []
        
        vulnerabilities = analysis_results.get("vulnerabilities", [])
        
        for vuln in vulnerabilities:
            crack_rec = {
                "target_type": vuln["type"],
                "severity": vuln["severity"],
                "description": vuln["description"],
                "location": vuln["location"],
                "crack_method": self._get_crack_method(vuln["type"]),
                "patch_code": self._get_fix_code(vuln["type"]),
                "confidence": vuln["confidence"],
                "difficulty": self._get_difficulty_score(vuln["severity"])
            }
            recommendations.append(crack_rec)
        
        # Sort by confidence and severity
        recommendations.sort(key=lambda x: (x["confidence"], x["severity"]), reverse=True)
        
        return recommendations
    
    def _get_crack_method(self, vuln_type: str) -> str:
        """Get appropriate crack method for vulnerability type"""
        crack_methods = {
            "login_bypass": "Authentication Bypass",
            "iap_bypass": "In-App Purchase Bypass", 
            "root_bypass": "Root Detection Bypass",
            "ssl_bypass": "Certificate Pinning Bypass",
            "debug_bypass": "Anti-Debug Bypass",
            "license_bypass": "License Check Bypass",
            "premium_unlock": "Premium Feature Unlock",
            "game_mod": "Game Modification"
        }
        return crack_methods.get(vuln_type, "Generic Bypass")
    
    def _get_difficulty_score(self, severity: str) -> str:
        """Get difficulty assessment based on severity"""
        difficulty_map = {
            "CRITICAL": "EASY",
            "HIGH": "EASY",
            "MEDIUM": "MEDIUM", 
            "LOW": "HARD"
        }
        return difficulty_map.get(severity, "MEDIUM")

# Global instance
pattern_matcher = PatternMatcher()

def main():
    """Main function for testing pattern matcher"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pattern_matcher.py <apk_path>")
        print("Usage: python pattern_matcher.py analyze <apk_path>")
        print("Usage: python pattern_matcher.py find-patterns <text_file>")
        return
    
    command = sys.argv[1]
    
    if command == "analyze":
        if len(sys.argv) < 3:
            print("Please provide APK path")
            return
        
        apk_path = sys.argv[2]
        print(f"Analyzing APK: {apk_path}")
        
        results = pattern_matcher.analyze_apk_patterns(apk_path)
        
        print(f"\nAnalysis Results:")
        print(f"Matches found: {len(results['matches'])}")
        print(f"Vulnerabilities: {len(results['vulnerabilities'])}")
        print(f"Security Score: {results['security_score']}/100")
        print(f"Analysis Time: {results['analysis_time']:.2f}s")
        
        print(f"\nTop 5 Vulnerabilities:")
        for i, vuln in enumerate(results['vulnerabilities'][:5], 1):
            print(f"  {i}. {vuln['type']} - {vuln['severity']} ({vuln['confidence']:.2f} confidence)")
        
        # Generate crack recommendations
        recommendations = pattern_matcher.get_crack_recommendations(results)
        print(f"\nCrack Recommendations (top 5):")
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"  {i}. {rec['crack_method']} ({rec['difficulty']}) - {rec['confidence']:.2f} confidence")
    
    elif command == "find-patterns":
        if len(sys.argv) < 3:
            print("Please provide text file path")
            return
        
        file_path = sys.argv[2]
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return
        
        print(f"Searching patterns in: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Direct pattern matching on content (simplified)
        matches = []
        for pattern_key, pattern_data in pattern_matcher.patterns.items():
            regex = pattern_data["regex"]
            for match in regex.finditer(content):
                matches.append({
                    "pattern": pattern_key,
                    "matched": match.group(),
                    "position": match.start()
                })
        
        print(f"Found {len(matches)} pattern matches:")
        for match in matches[:10]:  # Show first 10
            print(f"  - {match['pattern']}: {match['matched'][:50]}...")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()