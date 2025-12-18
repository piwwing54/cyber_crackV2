#!/usr/bin/env python3
"""
🛡️ Protection Detector for Cyber Crack Pro
Detects various protection mechanisms in APKs
"""

import asyncio
import logging
import re
import json
import os
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import zipfile
import subprocess

logger = logging.getLogger(__name__)

class ProtectionDetector:
    """Detects protection mechanisms in APKs"""
    
    def __init__(self):
        self.protection_patterns = self._initialize_protection_patterns()
        self.is_initialized = True
    
    def _initialize_protection_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize known protection patterns"""
        return {
            "root_detection": [
                {
                    "id": "root_001",
                    "name": "RootBeer Root Detection",
                    "patterns": [
                        r"RootBeer",
                        r"isRooted",
                        r"checkRoot",
                        r"RootTools",
                        r"checkForRoot",
                        r"su.*path",
                        r"/su",
                        r"/busybox",
                        r"test-keys",
                        r"ro\.secure.*0",
                        r"ro\.debuggable.*1"
                    ],
                    "severity": "high",
                    "confidence": 0.95,
                    "bypass_method": "Hook root detection functions to return false"
                },
                {
                    "id": "root_002",
                    "name": "Magisk Root Detection",
                    "patterns": [
                        r"magisk",
                        r"zygisk",
                        r"magiskhide",
                        r"magiskmanager"
                    ],
                    "severity": "high",
                    "confidence": 0.92,
                    "bypass_method": "Hide Magisk files and processes"
                }
            ],
            "certificate_pinning": [
                {
                    "id": "cert_001",
                    "name": "OkHttp Certificate Pinning",
                    "patterns": [
                        r"CertificatePinner",
                        r"pin\(",
                        r"pinRecord",
                        r"checkServerTrusted",
                        r"X509TrustManager"
                    ],
                    "severity": "high",
                    "confidence": 0.98,
                    "bypass_method": "Replace TrustManager with permissive implementation"
                },
                {
                    "id": "cert_002",
                    "name": "Network Security Config",
                    "patterns": [
                        r"networkSecurityConfig",
                        r"pin-set",
                        r"domain-config",
                        r"certificates",
                        r"src.*system",
                        r"src.*user",
                        r"overridePins"
                    ],
                    "severity": "high",
                    "confidence": 0.95,
                    "bypass_method": "Modify network security configuration"
                }
            ],
            "debug_detection": [
                {
                    "id": "debug_001",
                    "name": "Debugger Detection",
                    "patterns": [
                        r"isDebuggerConnected",
                        r"waitUntilDebuggerAttached",
                        r"android:debuggable",
                        r"BuildConfig\.DEBUG"
                    ],
                    "severity": "medium",
                    "confidence": 0.88,
                    "bypass_method": "Hook debugger detection to return false"
                },
                {
                    "id": "debug_002",
                    "name": "Ptrace Anti-Debug",
                    "patterns": [
                        r"ptrace",
                        r"PTRACE_ATTACH",
                        r"trace"
                    ],
                    "severity": "high",
                    "confidence": 0.90,
                    "bypass_method": "Disable ptrace protection"
                }
            ],
            "anti_emulation": [
                {
                    "id": "emu_001",
                    "name": "Emulator Detection",
                    "patterns": [
                        r"ro\.product\.model.*sdk",
                        r"ro\.product\.manufacturer.*unknown",
                        r"ro\.hardware.*goldfish",
                        r"ro\.kernel\.qemu",
                        r"Genymotion",
                        r"bluestacks",
                        r"x86.*emulator"
                    ],
                    "severity": "medium",
                    "confidence": 0.85,
                    "bypass_method": "Spoof device properties to appear as real device"
                }
            ],
            "obfuscation": [
                {
                    "id": "obf_001",
                    "name": "ProGuard Obfuscation",
                    "patterns": [
                        r"proguard",
                        r"a\.b\.c",
                        r"method\d+",
                        r"class\d+",
                        r"field\d+"
                    ],
                    "severity": "medium",
                    "confidence": 0.75,
                    "bypass_method": "Apply deobfuscation techniques"
                },
                {
                    "id": "obf_002",
                    "name": "String Encryption",
                    "patterns": [
                        r"decryptString",
                        r"encodeString",
                        r"obfuscate",
                        r"rot13",
                        r"base64.*decode"
                    ],
                    "severity": "high",
                    "confidence": 0.82,
                    "bypass_method": "Decrypt obfuscated strings at runtime"
                }
            ],
            "integrity_check": [
                {
                    "id": "int_001",
                    "name": "Signature Validation",
                    "patterns": [
                        r"getSignatures",
                        r"PackageManager.*SIGNATURE",
                        r"signature.*verify",
                        r"checkSignature",
                        r"authenticity"
                    ],
                    "severity": "high",
                    "confidence": 0.90,
                    "bypass_method": "Bypass signature validation checks"
                },
                {
                    "id": "int_002",
                    "name": "Checksum Validation",
                    "patterns": [
                        r"checksum",
                        r"hash.*check",
                        r"md5.*compare",
                        r"sha.*validate",
                        r"integrity.*check"
                    ],
                    "severity": "high",
                    "confidence": 0.88,
                    "bypass_method": "Modify or bypass checksum verification"
                }
            ],
            "anti_tamper": [
                {
                    "id": "tamper_001",
                    "name": "APK Tamper Detection",
                    "patterns": [
                        r"tamper",
                        r"modification.*detect",
                        r"hasBeenModified",
                        r"verifyApkIntegrity",
                        r"checkApkSignature"
                    ],
                    "severity": "high",
                    "confidence": 0.95,
                    "bypass_method": "Bypass APK integrity checks"
                }
            ],
            "packer_protection": [
                {
                    "id": "packer_001",
                    "name": "Bangcle Protection",
                    "patterns": [
                        r"com\.secneo\.apkwrapper",
                        r"Bangcle",
                        r"app-wrapper",
                        r"stub.*applcation"
                    ],
                    "severity": "critical",
                    "confidence": 0.98,
                    "bypass_method": "Unpack protected APK layers"
                },
                {
                    "id": "packer_002",
                    "name": "Qihoo Protection",
                    "patterns": [
                        r"com\.qihoo360\.stub\.StubApplication",
                        r"com\.qihoo360\.loader\.Launcher",
                        r"qihoo.*protect"
                    ],
                    "severity": "critical",
                    "confidence": 0.97,
                    "bypass_method": "Bypass Qihoo protection layers"
                }
            ]
        }
    
    async def detect_protections_in_apk(self, apk_path: str) -> Dict[str, Any]:
        """Detect all protections in an APK"""
        results = {
            "apk_path": apk_path,
            "protections_found": [],
            "protection_categories": {},
            "security_score": 0,
            "complexity_level": "MEDIUM",
            "recommendations": [],
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        try:
            # Extract APK temporarily for analysis
            temp_dir = await self._extract_apk(apk_path)
            
            # Analyze different components of the APK
            protection_results = []
            
            # Check AndroidManifest.xml for debuggable flags
            manifest_path = Path(temp_dir) / "AndroidManifest.xml"
            if manifest_path.exists():
                manifest_protections = await self._detect_protections_in_manifest(str(manifest_path))
                protection_results.extend(manifest_protections)
            
            # Check for native libraries that may contain protections
            native_libs = await self._find_native_libraries(temp_dir)
            for lib_path in native_libs:
                native_protections = await self._detect_protections_in_native_lib(lib_path)
                protection_results.extend(native_protections)
            
            # Check Smali code for protection implementations
            smali_files = await self._find_smali_files(temp_dir)
            for smali_path in smali_files:
                smali_protections = await self._detect_protections_in_smali(smali_path)
                protection_results.extend(smali_protections)
            
            # Organize results
            categorized_protections = {}
            for prot in protection_results:
                category = prot.get("category", "unknown")
                if category not in categorized_protections:
                    categorized_protections[category] = []
                categorized_protections[category].append(prot)
            
            results["protections_found"] = protection_results
            results["protection_categories"] = categorized_protections
            results["security_score"] = self._calculate_security_score(protection_results)
            results["complexity_level"] = self._determine_complexity_level(protection_results)
            results["recommendations"] = self._generate_recommendations(protection_results)
            
            # Clean up
            await self._cleanup_temp_dir(temp_dir)
            
        except Exception as e:
            logger.error(f"Error detecting protections in {apk_path}: {e}")
            results["error"] = str(e)
        
        return results
    
    async def _detect_protections_in_manifest(self, manifest_path: str) -> List[Dict[str, Any]]:
        """Detect protections in AndroidManifest.xml"""
        protections = []
        
        try:
            with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check for debuggable flag
            if "android:debuggable=\"true\"" in content:
                protections.append({
                    "id": "debug_003",
                    "name": "Debug Enabled",
                    "category": "debug_detection",
                    "severity": "medium",
                    "confidence": 0.95,
                    "location": "AndroidManifest.xml",
                    "matched_text": "android:debuggable=\"true\"",
                    "bypass_method": "Set android:debuggable to false"
                })
            
            # Check for backup enabled
            if "android:allowBackup=\"true\"" in content:
                protections.append({
                    "id": "backup_001",
                    "name": "Backup Enabled",
                    "category": "data_extraction",
                    "severity": "low",
                    "confidence": 0.70,
                    "location": "AndroidManifest.xml",
                    "matched_text": "android:allowBackup=\"true\"",
                    "bypass_method": "Set android:allowBackup to false"
                })
            
            # Check for network security config
            if "networkSecurityConfig" in content:
                protections.append({
                    "id": "cert_003",
                    "name": "Network Security Config",
                    "category": "certificate_pinning",
                    "severity": "high",
                    "confidence": 0.85,
                    "location": "AndroidManifest.xml",
                    "matched_text": "networkSecurityConfig",
                    "bypass_method": "Analyze and bypass network security configuration"
                })
                
        except Exception as e:
            logger.error(f"Error analyzing manifest {manifest_path}: {e}")
        
        return protections
    
    async def _detect_protections_in_native_lib(self, lib_path: str) -> List[Dict[str, Any]]:
        """Detect protections in native library (SO) files"""
        protections = []
        
        try:
            # For .so files, we'll use binary analysis techniques
            # This is a simplified approach - real implementation would be more complex
            with open(lib_path, 'rb') as f:
                content = f.read()
            
            # Convert to hex for pattern matching
            hex_content = content.hex()
            
            # Look for protection patterns in binary
            for category, category_patterns in self.protection_patterns.items():
                for pattern_data in category_patterns:
                    for pattern in pattern_data.get("patterns", []):
                        # Convert to hex pattern for binary search
                        if pattern.lower() in hex_content.lower():
                            protections.append({
                                "id": pattern_data["id"],
                                "name": pattern_data["name"],
                                "category": category,
                                "severity": pattern_data["severity"],
                                "confidence": pattern_data["confidence"],
                                "location": f"lib: {lib_path}",
                                "matched_text": f"Binary match for: {pattern}",
                                "bypass_method": pattern_data["bypass_method"]
                            })
                            
        except Exception as e:
            logger.error(f"Error analyzing native library {lib_path}: {e}")
        
        return protections
    
    async def _detect_protections_in_smali(self, smali_path: str) -> List[Dict[str, Any]]:
        """Detect protections in Smali files"""
        protections = []
        
        try:
            with open(smali_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Create regex from patterns and search
            for category, category_patterns in self.protection_patterns.items():
                for pattern_data in category_patterns:
                    for pattern in pattern_data.get("patterns", []):
                        # Use a simple string search for now
                        # In a real implementation, we'd use more sophisticated regex
                        if re.search(pattern, content, re.IGNORECASE):
                            # Find line number of match
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if re.search(pattern, line, re.IGNORECASE):
                                    protections.append({
                                        "id": pattern_data["id"],
                                        "name": pattern_data["name"],
                                        "category": category,
                                        "severity": pattern_data["severity"],
                                        "confidence": pattern_data["confidence"],
                                        "location": f"{smali_path}:{i+1}",
                                        "matched_text": line.strip()[:100],  # First 100 chars
                                        "bypass_method": pattern_data["bypass_method"]
                                    })
                                    
                                    # Break after first match to avoid duplicates
                                    break
                            
        except Exception as e:
            logger.error(f"Error analyzing Smali file {smali_path}: {e}")
        
        return protections
    
    def _calculate_security_score(self, protections: List[Dict[str, Any]]) -> int:
        """Calculate security score based on protections found"""
        base_score = 100
        
        # Deduct points based on the number and severity of protections
        for prot in protections:
            severity = prot.get("severity", "medium").lower()
            
            if severity == "critical":
                base_score -= 15
            elif severity == "high":
                base_score -= 10
            elif severity == "medium":
                base_score -= 5
            elif severity == "low":
                base_score -= 2
        
        # Each protection adds to the security of the app
        # So we increase the score back up based on number of protections
        base_score += min(len(protections) * 2, 50)  # Cap at +50 for protections
        
        return max(0, min(100, base_score))
    
    def _determine_complexity_level(self, protections: List[Dict[str, Any]]) -> str:
        """Determine how complex the app is to crack based on protections"""
        protection_count = len(protections)
        
        # Count high severity protections
        high_severity_count = sum(1 for p in protections if p.get("severity", "").lower() in ["critical", "high"])
        
        if high_severity_count >= 5 or protection_count >= 15:
            return "EXTREME"
        elif high_severity_count >= 3 or protection_count >= 10:
            return "HIGH"
        elif high_severity_count >= 2 or protection_count >= 5:
            return "MEDIUM"
        elif protection_count > 0:
            return "LOW"
        else:
            return "TRIVIAL"
    
    def _generate_recommendations(self, protections: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on detected protections"""
        recommendations = []
        
        # Group protections by category
        by_category = {}
        for prot in protections:
            cat = prot.get("category", "unknown")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(prot)
        
        # Generate category-specific recommendations
        if "root_detection" in by_category:
            recommendations.append("Root detection detected - prepare root bypass techniques")
        
        if "certificate_pinning" in by_category:
            recommendations.append("Certificate pinning detected - implement SSL bypass methods")
        
        if "debug_detection" in by_category:
            recommendations.append("Debug detection found - disable or bypass debug checks")
        
        if "anti_emulation" in by_category:
            recommendations.append("Emulator detection detected - prepare anti-emulation bypass")
        
        if "integrity_check" in by_category:
            recommendations.append("Integrity checks found - bypass signature/validation checks")
        
        if "packer_protection" in by_category:
            recommendations.append("Packer protection detected - may need unpacking before analysis")
        
        if "obfuscation" in by_category:
            recommendations.append("Code obfuscation detected - apply deobfuscation techniques")
        
        if "anti_tamper" in by_category:
            recommendations.append("Anti-tampering protections found - prepare bypass methods")
        
        # Add general recommendations
        if len(protections) > 10:
            recommendations.append("App has many protections - consider layered bypass approach")
        
        if len(protections) > 5:
            recommendations.append("Moderate protection level - advanced techniques may be required")
        
        recommendations.append("Analyze in conjunction with vulnerability detection for best results")
        
        return recommendations
    
    async def _extract_apk(self, apk_path: str) -> str:
        """Extract APK for analysis"""
        import tempfile
        temp_dir = tempfile.mkdtemp(prefix="apk_protection_analysis_")
        
        # Use apktool or simple zip extraction
        try:
            # For now, we'll use simple extraction
            # In a real implementation, we'd use apktool
            import zipfile
            with zipfile.ZipFile(apk_path, 'r') as apk:
                apk.extractall(temp_dir)
        except:
            # Fallback if apktool is not available
            import zipfile
            with zipfile.ZipFile(apk_path, 'r') as apk:
                apk.extractall(temp_dir)
        
        return temp_dir
    
    async def _find_smali_files(self, extract_dir: str) -> List[str]:
        """Find all Smali files in extracted APK"""
        smali_files = []
        
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith('.smali'):
                    smali_files.append(os.path.join(root, file))
        
        return smali_files
    
    async def _find_native_libraries(self, extract_dir: str) -> List[str]:
        """Find all native library files in extracted APK"""
        native_libs = []
        
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith('.so'):
                    native_libs.append(os.path.join(root, file))
        
        return native_libs
    
    async def _cleanup_temp_dir(self, temp_dir: str):
        """Clean up temporary extraction directory"""
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            logger.error(f"Error cleaning up temp directory {temp_dir}: {e}")
    
    async def detect_specific_protection(self, apk_path: str, protection_type: str) -> List[Dict[str, Any]]:
        """Detect a specific type of protection"""
        if protection_type not in self.protection_patterns:
            return []
        
        all_results = await self.detect_protections_in_apk(apk_path)
        specific_results = []
        
        for prot in all_results.get("protections_found", []):
            if prot.get("category") == protection_type:
                specific_results.append(prot)
        
        return specific_results
    
    def get_protection_categories(self) -> List[str]:
        """Get all available protection categories"""
        return list(self.protection_patterns.keys())

class AdvancedProtectionDetector(ProtectionDetector):
    """Advanced protection detector with AI enhancements"""
    
    def __init__(self):
        super().__init__()
        self.ai_enhanced = True
        self.ai_model_path = Path("models/protection_classifier.pkl")
    
    async def ai_enhanced_detection(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Use AI to enhance protection detection"""
        # This would normally use a trained model for protection detection
        # For now, we'll return basic results with AI confidence adjustments
        ai_results = []
        
        # In a real implementation, this would:
        # 1. Load the AI model
        # 2. Preprocess the content
        # 3. Run inference
        # 4. Return AI-predicted protection types
        
        # For simulation, we'll just add AI confidence to existing results
        basic_results = await self._detect_protections_in_smali(file_path)
        
        for result in basic_results:
            # Increase confidence for AI-enhanced detection
            result["confidence"] = min(1.0, result["confidence"] + 0.1)
            result["ai_enhanced"] = True
            result["ai_score"] = result["confidence"]
            ai_results.append(result)
        
        return ai_results
    
    async def deep_analysis_protection(self, apk_path: str) -> Dict[str, Any]:
        """Perform deep analysis with advanced techniques"""
        basic_results = await self.detect_protections_in_apk(apk_path)
        
        # Add AI analysis results
        basic_results["ai_analysis"] = await self._perform_ai_analysis(apk_path)
        
        # Add behavioral analysis results
        basic_results["behavioral_analysis"] = await self._perform_behavioral_analysis(apk_path)
        
        # Add obfuscation analysis
        basic_results["obfuscation_analysis"] = await self._perform_obfuscation_analysis(apk_path)
        
        # Recalculate security score with AI insights
        ai_protections = basic_results["ai_analysis"].get("protections_found", [])
        all_protections = basic_results["protections_found"] + ai_protections
        basic_results["security_score"] = self._calculate_security_score(all_protections)
        
        # Update complexity level based on all findings
        basic_results["complexity_level"] = self._determine_complexity_level(all_protections)
        
        # Generate enhanced recommendations
        basic_results["enhanced_recommendations"] = self._generate_enhanced_recommendations(
            all_protections,
            basic_results["ai_analysis"],
            basic_results["behavioral_analysis"]
        )
        
        return basic_results
    
    async def _perform_ai_analysis(self, apk_path: str) -> Dict[str, Any]:
        """Perform AI-based protection analysis"""
        # Simulated AI analysis
        return {
            "enabled": self.ai_enhanced,
            "model_version": "protection_classifier_v3.0",
            "protections_found": [],
            "predictions": {
                "is_protected": True,
                "protection_complexity_score": 0.85,
                "recommended_bypass_difficulty": "MEDIUM"
            },
            "confidence": 0.9,
            "analysis_time_ms": 150
        }
    
    async def _perform_behavioral_analysis(self, apk_path: str) -> Dict[str, Any]:
        """Perform behavioral analysis of protections"""
        # Simulated behavioral analysis
        return {
            "protection_interaction": "protections work together to prevent unauthorized access",
            "bypass_difficulty": "MODERATE",
            "critical_points": ["certificate_pinning", "root_detection"],
            "attack_surface_assessment": "MEDIUM"
        }
    
    async def _perform_obfuscation_analysis(self, apk_path: str) -> Dict[str, Any]:
        """Analyze code obfuscation levels"""
        # Simulated obfuscation analysis
        return {
            "obfuscation_detected": True,
            "obfuscation_type": "proguard",
            "deobfuscation_complexity": "HIGH",
            "recommendations": ["apply_deobfuscation_tools", "use_ast_analysis"],
            "difficulty_score": 0.75
        }
    
    def _generate_enhanced_recommendations(self, protections: List[Dict[str, Any]], 
                                         ai_analysis: Dict[str, Any], 
                                         behavioral_analysis: Dict[str, Any]) -> List[str]:
        """Generate enhanced recommendations based on all analysis types"""
        recommendations = self._generate_recommendations(protections)
        
        # Add AI-specific recommendations
        ai_preds = ai_analysis.get("predictions", {})
        if ai_preds:
            if ai_preds.get("recommended_bypass_difficulty") == "HARD":
                recommendations.append("AI recommends using advanced multi-layer bypass techniques")
            elif ai_preds.get("recommended_bypass_difficulty") == "TRIVIAL":
                recommendations.append("AI suggests this app may have minimal actual protections")
        
        # Add behavioral recommendations
        behavior_recs = behavioral_analysis.get("recommendations", [])
        recommendations.extend(behavior_recs)
        
        # Add obfuscation-specific recommendations
        obfuscation_recs = behavioral_analysis.get("recommendations", [])
        recommendations.extend(obfuscation_recs)
        
        return list(set(recommendations))  # Remove duplicates

# Example usage
async def main():
    detector = AdvancedProtectionDetector()
    
    # Example: Detect protections in an APK
    # results = await detector.deep_analysis_protection("/path/to/app.apk")
    # print(f"Protections found: {len(results['protections_found'])}")
    
    print("Protection detectors initialized!")
    print(f"Available categories: {detector.get_protection_categories()}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())