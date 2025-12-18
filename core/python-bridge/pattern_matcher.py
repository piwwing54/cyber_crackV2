#!/usr/bin/env python3
"""
🔍 CYBER CRACK PRO - Pattern Matcher
This module is part of the Python bridge and handles pattern matching for APK analysis
"""

import re
import logging
import json
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import zipfile
import tempfile
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PatternMatcher:
    """Smart pattern matcher for APK analysis"""
    
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
        self.patterns = self._compile_patterns()
        
    def _load_knowledge_base(self) -> Dict:
        """Load knowledge base from JSON file"""
        try:
            # Try to load from brain directory first
            kb_path = Path("brain/knowledge_base.json")
            if not kb_path.exists():
                # If not found, try from current directory
                kb_path = Path("knowledge_base.json")
                
            if kb_path.exists():
                with open(kb_path, 'r') as f:
                    return json.load(f)
            else:
                # Return default knowledge base
                return self._get_default_knowledge_base()
        except FileNotFoundError:
            # Return default knowledge base if file not found
            return self._get_default_knowledge_base()
        except json.JSONDecodeError:
            logger.error("Invalid JSON in knowledge base file")
            return self._get_default_knowledge_base()
    
    def _get_default_knowledge_base(self) -> Dict:
        """Return default knowledge base if file not found"""
        return {
            "patterns": {
                "login_bypass": {
                    "description": "Login bypass patterns",
                    "regex": [
                        "login",
                        "authenticate",
                        "auth",
                        "session",
                        "credential",
                        "password",
                        "username"
                    ],
                    "smali_patterns": [
                        "const-string.*login",
                        "invoke.*login",
                        "if-eqz.*auth"
                    ]
                },
                "iap_bypass": {
                    "description": "In-app purchase bypass patterns",
                    "regex": [
                        "billing",
                        "purchase",
                        "receipt",
                        "verify",
                        "transaction",
                        "payment",
                        "subscription"
                    ],
                    "smali_patterns": [
                        "const-string.*billing",
                        "invoke.*payment",
                        "iget.*receipt"
                    ]
                },
                "certificate_pinning": {
                    "description": "Certificate pinning implementations",
                    "regex": [
                        "pinning",
                        "certificate",
                        "ssl",
                        "tls",
                        "trust",
                        "hostname"
                    ],
                    "smali_patterns": [
                        "checkServerTrusted",
                        "verifyHostname",
                        "getTrustManager"
                    ]
                },
                "root_detection": {
                    "description": "Root detection implementations",
                    "regex": [
                        "root",
                        "superuser",
                        "su",
                        "busybox",
                        "isRoot",
                        "checkRoot"
                    ],
                    "smali_patterns": [
                        "const-string.*su",
                        "file.*busybox",
                        "getPackageManager"
                    ]
                }
            },
            "vulnerabilities": {
                "excessive_permissions": {
                    "severity": "MEDIUM",
                    "description": "Application requests more permissions than necessary",
                    "cwe": "CWE-250"
                },
                "weak_cryptography": {
                    "severity": "HIGH",
                    "description": "Use of weak or deprecated cryptographic algorithms",
                    "cwe": "CWE-327"
                },
                "hardcoded_credentials": {
                    "severity": "CRITICAL",
                    "description": "Credentials hardcoded in the application",
                    "cwe": "CWE-798"
                }
            }
        }
    
    def _compile_patterns(self) -> Dict:
        """Compile regex patterns for faster matching"""
        compiled = {}
        
        if "patterns" in self.knowledge_base:
            for category, data in self.knowledge_base["patterns"].items():
                if "regex" in data:
                    try:
                        combined_pattern = "|".join(data["regex"])
                        compiled[category] = re.compile(combined_pattern, re.IGNORECASE)
                    except re.error as e:
                        logger.error(f"Error compiling pattern for {category}: {e}")
        
        return compiled
    
    def analyze_apk_patterns(self, apk_path: str) -> Dict:
        """Analyze APK for known patterns"""
        results = {
            "matches": [],
            "vulnerabilities": [],
            "protections": [],
            "recommendations": [],
            "security_score": 0,
            "detailed_results": {},
            "success": True
        }
        
        try:
            # Extract APK temporarily
            with tempfile.TemporaryDirectory() as temp_dir:
                extracted_path = Path(temp_dir)
                self._extract_apk(apk_path, extracted_path)
                
                # Search for patterns in extracted files
                results = self._search_patterns_in_directory(extracted_path)
                
                # Calculate security score based on findings
                results["security_score"] = self._calculate_security_score(results)
                
        except Exception as e:
            logger.error(f"Error analyzing APK patterns: {e}")
            results["error"] = str(e)
            results["success"] = False
        
        return results
    
    def _extract_apk(self, apk_path: str, extract_to: Path):
        """Extract APK contents to directory"""
        with zipfile.ZipFile(apk_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    
    def _search_patterns_in_directory(self, directory: Path) -> Dict:
        """Search for patterns in extracted APK directory"""
        results = {
            "matches": [],
            "vulnerabilities": [],
            "protections": [],
            "recommendations": []
        }
        
        # Walk through all files in extracted APK
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                try:
                    # Only analyze text files
                    if self._is_text_file(file_path):
                        matches = self._search_patterns_in_file(file_path)
                        results["matches"].extend(matches)
                        
                        # Classify matches as vulnerabilities or protections
                        self._classify_matches(matches, results)
                        
                except Exception as e:
                    logger.warning(f"Error reading file {file_path}: {e}")
        
        return results
    
    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is a text file"""
        text_extensions = {'.txt', '.java', '.smali', '.xml', '.json', '.js', '.html', '.css', '.py', '.cpp', '.c', '.h', '.go', '.rs'}
        return file_path.suffix.lower() in text_extensions
    
    def _search_patterns_in_file(self, file_path: Path) -> List[Dict]:
        """Search for patterns in a single file"""
        matches = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Search with compiled patterns
            for pattern_name, pattern_regex in self.patterns.items():
                found = pattern_regex.findall(content)
                if found:
                    matches.append({
                        "pattern": pattern_name,
                        "matches": found,
                        "file": str(file_path),
                        "type": self._classify_pattern_type(pattern_name)
                    })
            
            # Additional specialized pattern matching
            specific_matches = self._search_specific_patterns(content, str(file_path))
            matches.extend(specific_matches)
            
        except Exception as e:
            logger.warning(f"Error searching patterns in {file_path}: {e}")
        
        return matches
    
    def _classify_pattern_type(self, pattern_name: str) -> str:
        """Classify pattern as vulnerability or protection"""
        vulnerability_indicators = ["login", "auth", "certificate", "security"]
        protection_indicators = ["pinning", "detection", "verification"]
        
        for indicator in vulnerability_indicators:
            if indicator in pattern_name.lower():
                return "vulnerability"
        
        for indicator in protection_indicators:
            if indicator in pattern_name.lower():
                return "protection"
        
        return "neutral"
    
    def _search_specific_patterns(self, content: str, file_path: str) -> List[Dict]:
        """Search for specific patterns not covered by regex"""
        matches = []
        
        # Search for hardcoded credentials
        credential_patterns = [
            (r'password[\'"]?\s*[:=]\s*[\'"][^\'"]{3,50}[\'"]', 'Hardcoded Password'),
            (r'api[_-]?key[\'"]?\s*[:=]\s*[\'"][^\'"]{10,100}[\'"]', 'API Key'),
            (r'secret[\'"]?\s*[:=]\s*[\'"][^\'"]{10,100}[\'"]', 'Secret Key'),
            (r'token[\'"]?\s*[:=]\s*[\'"][^\'"]{10,100}[\'"]', 'Authentication Token')
        ]
        
        for pattern, description in credential_patterns:
            found = re.findall(pattern, content, re.IGNORECASE)
            if found:
                matches.append({
                    "pattern": description,
                    "matches": found,
                    "file": file_path,
                    "type": "vulnerability"
                })
        
        # Search for weak cryptographic functions
        crypto_patterns = [
            (r'MD5|DES|RC4|SHA1(?!\s*[+-])', 'Weak Cryptography'),
            (r'Base64.encode|Base64.decode', 'Base64 Encoding'),
            (r'XOR|simple.*encrypt', 'Weak Encryption')
        ]
        
        for pattern, description in crypto_patterns:
            found = re.findall(pattern, content, re.IGNORECASE)
            if found:
                matches.append({
                    "pattern": description,
                    "matches": found,
                    "file": file_path,
                    "type": "vulnerability"
                })
        
        # Search for root detection patterns
        root_patterns = [
            (r'su\b|superuser|busybox', 'Root Detection'),
            (r'isRoot|checkRoot|rootBeer', 'Root Check')
        ]
        
        for pattern, description in root_patterns:
            found = re.findall(pattern, content, re.IGNORECASE)
            if found:
                matches.append({
                    "pattern": description,
                    "matches": found,
                    "file": file_path,
                    "type": "protection"  # Root detection is a protection
                })
        
        # Search for certificate pinning
        cert_patterns = [
            (r'checkServerTrusted|X509TrustManager|SSLSocketFactory', 'Certificate Pinning'),
            (r'CertificatePinner|Pinning|trustAll', 'Certificate Pinning')
        ]
        
        for pattern, description in cert_patterns:
            found = re.findall(pattern, content, re.IGNORECASE)
            if found:
                matches.append({
                    "pattern": description,
                    "matches": found,
                    "file": file_path,
                    "type": "protection"
                })
        
        return matches
    
    def _classify_matches(self, matches: List[Dict], results: Dict):
        """Classify matches into vulnerabilities and protections"""
        for match in matches:
            if match["type"] == "vulnerability":
                results["vulnerabilities"].append({
                    "type": match["pattern"],
                    "description": f"Found {match['pattern']} in {match['file']}",
                    "severity": self._get_severity(match["pattern"]),
                    "matches": match["matches"],
                    "file": match["file"]
                })
            elif match["type"] == "protection":
                if match["pattern"] not in results["protections"]:
                    results["protections"].append(match["pattern"])
            
            # Add recommendations based on patterns
            self._add_recommendations(match, results)
    
    def _get_severity(self, pattern: str) -> str:
        """Get severity level for a pattern"""
        high_severity = ["hardcoded", "password", "api key", "secret", "certificate"]
        medium_severity = ["weak", "deprecated", "insecure", "root"]
        
        pattern_lower = pattern.lower()
        
        for term in high_severity:
            if term in pattern_lower:
                return "HIGH"
        
        for term in medium_severity:
            if term in pattern_lower:
                return "MEDIUM"
        
        return "LOW"
    
    def _add_recommendations(self, match: Dict, results: Dict):
        """Add recommendations based on found patterns"""
        pattern = match["pattern"].lower()
        
        recommendations_map = {
            "login": "Consider implementing proper authentication checks",
            "certificate": "Look for certificate pinning bypass opportunities",
            "password": "Hardcoded credentials can be extracted easily",
            "api key": "API keys should be protected server-side",
            "weak cryptography": "Use stronger cryptographic algorithms",
            "hardcoded": "Avoid hardcoding sensitive values",
            "root detection": "Look for root detection bypass opportunities",
            "protection": "Protection mechanisms may need to be bypassed"
        }
        
        for key, recommendation in recommendations_map.items():
            if key in pattern and recommendation not in results["recommendations"]:
                results["recommendations"].append(recommendation)
    
    def find_crack_targets(self, apk_path: str) -> List[Dict]:
        """Find potential targets for cracking"""
        targets = []
        
        # Analyze the APK
        analysis = self.analyze_apk_patterns(apk_path)
        
        # Look for crackable elements in vulnerabilities
        for vuln in analysis.get("vulnerabilities", []):
            target_type = self._determine_crack_type(vuln)
            if target_type:
                targets.append({
                    "type": target_type,
                    "description": vuln.get("description", ""),
                    "severity": vuln.get("severity", "MEDIUM"),
                    "location": vuln.get("file", "Unknown"),
                    "confidence": self._calculate_confidence(vuln)
                })
        
        # Also consider protections as targets (to bypass them)
        for protection in analysis.get("protections", []):
            if protection.lower() in ["certificate pinning", "root detection", "anti-debug"]:
                targets.append({
                    "type": f"Bypass {protection}",
                    "description": f"Protection mechanism: {protection}",
                    "severity": "MEDIUM",
                    "location": "Multiple files",
                    "confidence": 0.7
                })
        
        return targets
    
    def _determine_crack_type(self, vulnerability: Dict) -> Optional[str]:
        """Determine crack type from vulnerability"""
        vuln_type = vulnerability.get("type", "").lower()
        
        crack_types = {
            "login": "Login Bypass",
            "auth": "Authentication Bypass", 
            "iap": "In-App Purchase",
            "certificate": "Certificate Pinning Bypass",
            "verify": "Verification Bypass",
            "check": "Validation Bypass",
            "license": "License Check Bypass",
            "root": "Root Detection Bypass"
        }
        
        for pattern, crack_type in crack_types.items():
            if pattern in vuln_type:
                return crack_type
        
        return None
    
    def _calculate_confidence(self, vulnerability: Dict) -> float:
        """Calculate confidence level for crack target"""
        severity = vulnerability.get("severity", "MEDIUM")
        
        severity_confidence = {
            "CRITICAL": 0.9,
            "HIGH": 0.8,
            "MEDIUM": 0.6,
            "LOW": 0.4
        }
        
        return severity_confidence.get(severity, 0.5)
    
    def _calculate_security_score(self, results: Dict) -> int:
        """Calculate security score based on vulnerabilities and protections"""
        score = 100
        
        # Deduct points for vulnerabilities based on severity
        severity_deduction = {
            "CRITICAL": 15,
            "HIGH": 10,
            "MEDIUM": 5,
            "LOW": 2
        }
        
        for vuln in results.get("vulnerabilities", []):
            severity = vuln.get("severity", "MEDIUM")
            deduction = severity_deduction.get(severity, 5)
            score -= deduction
        
        # Add points for protections
        score += len(results.get("protections", [])) * 3
        
        # Ensure score is between 0 and 100
        return max(0, min(score, 100))


def main():
    """Main function for testing"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pattern_matcher.py <apk_path>")
        return
    
    apk_path = sys.argv[1]
    
    if not Path(apk_path).exists():
        print(f"APK file does not exist: {apk_path}")
        return
    
    matcher = PatternMatcher()
    
    print(f"Analyzing APK: {apk_path}")
    results = matcher.analyze_apk_patterns(apk_path)
    
    print(f"\nAnalysis Results:")
    print(f"Vulnerabilities found: {len(results.get('vulnerabilities', []))}")
    print(f"Protections detected: {len(results.get('protections', []))}")
    print(f"Security Score: {results.get('security_score', 0)}/100")
    
    print(f"\nVulnerabilities:")
    for vuln in results.get("vulnerabilities", []):
        print(f"  - {vuln.get('type', 'Unknown')}: {vuln.get('description', '')}")
    
    print(f"\nProtections:")
    for prot in results.get("protections", []):
        print(f"  - {prot}")
    
    print(f"\nRecommendations:")
    for rec in results.get("recommendations", []):
        print(f"  - {rec}")
    
    # Find crack targets
    targets = matcher.find_crack_targets(apk_path)
    print(f"\nPotential Crack Targets: {len(targets)}")
    for target in targets:
        print(f"  - {target.get('type', 'Unknown')} (Confidence: {target.get('confidence', 0):.2f})")


if __name__ == "__main__":
    main()