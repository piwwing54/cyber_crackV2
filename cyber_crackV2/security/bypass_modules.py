#!/usr/bin/env python3
"""
🛡️ Cyber Crack Pro - Security Bypass Modules
Collection of security bypass mechanisms for various protections
"""

import logging
import os
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import asyncio
import aiohttp
import subprocess
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SecurityType(Enum):
    ROOT_DETECTION = "root_detection"
    SSL_PINNING = "ssl_pinning"
    ANTI_DEBUG = "anti_debug"
    ANTI_EMULATOR = "anti_emulator"
    ANTI_HOOKING = "anti_hooking"
    INTEGRITY_CHECK = "integrity_check"
    LICENSE_CHECK = "license_check"
    CERTIFICATE_CHECK = "certificate_check"
    OBFUSCATION = "obfuscation"
    PACKER = "packer"

class SecurityBypass:
    """Main security bypass class"""
    
    def __init__(self):
        self.bypass_patterns = self._load_bypass_patterns()
        self.protection_patterns = self._load_protection_patterns()
        
    def _load_bypass_patterns(self) -> Dict[SecurityType, Dict[str, str]]:
        """Load bypass patterns for different security types"""
        return {
            SecurityType.ROOT_DETECTION: {
                "RootTools.isRooted": "const/4 v0, 0x0",
                "isRooted": "const/4 v0, 0x0",
                "checkRoot": "const/4 v0, 0x0",
                "RootBeer.isRooted": "const/4 v0, 0x0",
                "isSuperuserInstalled": "const/4 v0, 0x0",
                "checkForRoot": "const/4 v0, 0x0",
                "checkSuExists": "const/4 v0, 0x0",
                "checkForBusyBox": "const/4 v0, 0x0",
                "checkForDangerousApps": "const/4 v0, 0x0",
                "checkForDangerousFiles": "const/4 v0, 0x0",
            },
            SecurityType.SSL_PINNING: {
                "checkServerTrusted": "return-void",
                "X509TrustManager.checkServerTrusted": "return-void",
                "SSLSocketFactory": "return-void",
                "CertificatePinner.check": "return-void",
                "verifyHostname": "const/4 v0, 0x1",
                "isTrusted": "const/4 v0, 0x1",
                "verifyCertificateChain": "return-void",
            },
            SecurityType.ANTI_DEBUG: {
                "isDebuggerConnected": "const/4 v0, 0x0",
                "Debug.isDebuggerConnected": "const/4 v0, 0x0",
                "isSecure": "const/4 v0, 0x0",
                "checkTracer": "return-void",
                "detectTracer": "const/4 v0, 0x0",
                "checkParent": "const/4 v0, 0x1",
                "isBeingDebugged": "const/4 v0, 0x0",
                "checkForDebugger": "const/4 v0, 0x0",
            },
            SecurityType.ANTI_EMULATOR: {
                "isRunningInEmulator": "const/4 v0, 0x0",
                "checkEmulator": "const/4 v0, 0x0",
                "checkForEmulator": "const/4 v0, 0x0",
                "isEmulator": "const/4 v0, 0x0",
                "isVirtualDevice": "const/4 v0, 0x0",
                "checkHardware": "const/4 v0, 0x0",
                "isGenymotion": "const/4 v0, 0x0",
                "checkQemu": "const/4 v0, 0x0",
            },
            SecurityType.LICENSE_CHECK: {
                "checkLicense": "const/4 v0, 0x1",
                "LicenseChecker.checkLicense": "const/4 v0, 0x1",
                "verifyLicense": "const/4 v0, 0x1",
                "isLicensed": "const/4 v0, 0x1",
                "validateLicense": "const/4 v0, 0x1",
                "verifySubscription": "const/4 v0, 0x1",
                "checkBilling": "const/4 v0, 0x1",
            },
            SecurityType.INTEGRITY_CHECK: {
                "verifySignature": "const/4 v0, 0x1",
                "checkIntegrity": "const/4 v0, 0x1",
                "validateChecksum": "const/4 v0, 0x1",
                "verifyApkSignature": "const/4 v0, 0x1",
                "isModified": "const/4 v0, 0x0",
                "checkTamper": "const/4 v0, 0x1",
            }
        }
    
    def _load_protection_patterns(self) -> Dict[SecurityType, List[str]]:
        """Load protection detection patterns"""
        return {
            SecurityType.ROOT_DETECTION: [
                "isRooted",
                "RootTools",
                "RootBeer",
                "checkRoot",
                "su",
                "Superuser",
                "SuperSU",
                "Xposed",
                "Magisk",
                "busybox"
            ],
            SecurityType.SSL_PINNING: [
                "CertificatePinner",
                "X509TrustManager",
                "SSLSocketFactory",
                "SSLContext",
                "HostnameVerifier",
                "checkServerTrusted",
                "pinning",
                "pinner",
                "cert"
            ],
            SecurityType.ANTI_DEBUG: [
                "isDebuggerConnected",
                "Debug.isDebuggerConnected",
                "isSecure",
                "checkTracer",
                "JDWP",
                "debugger",
                "ptrace"
            ],
            SecurityType.ANTI_EMULATOR: [
                "isRunningInEmulator",
                "isEmulator",
                "isVirtualDevice",
                "genymotion",
                "qemu",
                "emulator"
            ],
            SecurityType.LICENSE_CHECK: [
                "LicenseChecker",
                "checkLicense",
                "verifyLicense",
                "isLicensed",
                "billing",
                "inapp",
                "purchase"
            ],
            SecurityType.INTEGRITY_CHECK: [
                "verifySignature",
                "checkIntegrity",
                "validateChecksum",
                "tamper",
                "integrity",
                "checksum",
                "signature"
            ]
        }
    
    def bypass_security_in_smali(self, smali_code: str, security_type: SecurityType) -> str:
        """Apply bypass for specific security type to smali code"""
        if security_type not in self.bypass_patterns:
            return smali_code
        
        bypasses_applied = 0
        modified_code = smali_code
        
        for pattern, replacement in self.bypass_patterns[security_type].items():
            if pattern in modified_code:
                # For method calls that return boolean results
                if replacement == "const/4 v0, 0x0":  # Always return false (security check passes)
                    modified_code = modified_code.replace(
                        f"invoke-static {{}}, L{pattern}",
                        f"    # Bypassed: {pattern}\n    const/4 v0, 0x0  # Always return false"
                    )
                    modified_code = modified_code.replace(
                        f"invoke-virtual {{p0}}, L{pattern}",
                        f"    # Bypassed: {pattern}\n    const/4 v0, 0x0  # Always return false"
                    )
                
                # For methods that should be made to always return true
                elif replacement == "const/4 v0, 0x1":  # Always return true
                    modified_code = modified_code.replace(
                        f"invoke-static {{}}, L{pattern}",
                        f"    # Bypassed: {pattern}\n    const/4 v0, 0x1  # Always return true"
                    )
                    
                # For methods that should be made to return nothing
                elif replacement == "return-void":
                    lines = modified_code.split('\n')
                    for i, line in enumerate(lines):
                        if pattern in line and ("invoke" in line or "call" in line):
                            # Find the next return statement and bypass it
                            for j in range(i, min(i+10, len(lines))):
                                if "return" in lines[j]:
                                    lines[j] = "    # Bypassed return\n    return-void"
                                    break
                    modified_code = '\n'.join(lines)
                
                # General replacement
                else:
                    modified_code = modified_code.replace(pattern, replacement)
                
                bypasses_applied += 1
        
        if bypasses_applied > 0:
            logger.info(f"Applied {bypasses_applied} bypasses for {security_type.value}")
        
        return modified_code
    
    def detect_protections_in_smali(self, smali_code: str) -> Dict[SecurityType, List[str]]:
        """Detect security protections in smali code"""
        detected_protections = {}
        
        for security_type, patterns in self.protection_patterns.items():
            found_instances = []
            for pattern in patterns:
                if pattern.lower() in smali_code.lower():
                    # Find all occurrences with context
                    matches = re.findall(rf'.{{0,20}}{re.escape(pattern)}.{{0,20}}', smali_code, re.IGNORECASE)
                    found_instances.extend([match.strip() for match in matches])
            
            if found_instances:
                detected_protections[security_type] = list(set(found_instances))  # Remove duplicates
        
        return detected_protections
    
    def bypass_certificate_pinning(self, apk_path: str, output_path: str) -> Dict[str, Any]:
        """Complete certificate pinning bypass"""
        try:
            logger.info(f"Bypassing certificate pinning for: {apk_path}")
            
            # First decompile the APK
            decompiled_dir = f"{os.path.splitext(apk_path)[0]}_decompiled"
            subprocess.run(["apktool", "d", apk_path, "-o", decompiled_dir, "-f"], check=True)
            
            # Find and modify all smali files
            modified_count = 0
            for root, dirs, files in os.walk(decompiled_dir):
                for file in files:
                    if file.endswith('.smali'):
                        file_path = os.path.join(root, file)
                        
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Apply SSL pinning bypass
                        original_content = content
                        content = self.bypass_security_in_smali(content, SecurityType.SSL_PINNING)
                        
                        # Also look for specific SSL patterns
                        ssl_patterns = [
                            "checkServerTrusted",
                            "verifyHostname", 
                            "X509TrustManager",
                            "CertificatePinner",
                            "pinCertificate"
                        ]
                        
                        for pattern in ssl_patterns:
                            if pattern in content:
                                # Replace verification method to always return success
                                lines = content.split('\n')
                                for i, line in enumerate(lines):
                                    if f" {pattern}(" in line and ("Z" in line or "V" in line):
                                        # Find the return statement in this method
                                        start_idx = i
                                        end_idx = len(lines)
                                        
                                        # Find method boundaries
                                        for j in range(i, len(lines)):
                                            if ".method" in lines[j] and j > i:
                                                end_idx = j
                                                break
                                        
                                        # Find return and replace with success
                                        for k in range(start_idx, end_idx):
                                            if "return" in lines[k]:
                                                if "return-boolean" in lines[k] or "return v" in lines[k]:
                                                    lines[k] = "    const/4 v0, 0x1\n    return v0"
                                                elif "return-void" in lines[k]:
                                                    pass  # Already void return
                                                break
                                
                                content = '\n'.join(lines)
                        
                        # Write back if modified
                        if content != original_content:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            modified_count += 1
            
            # Rebuild the APK
            subprocess.run(["apktool", "b", decompiled_dir, "-o", output_path], check=True)
            
            # Sign the APK
            subprocess.run([
                "java", "-jar", "uber-apk-signer.jar", 
                "-a", output_path
            ], check=True)
            
            return {
                "success": True,
                "modified_files": modified_count,
                "output_apk": output_path,
                "bypasses_applied": ["certificate_pinning_bypass"]
            }
            
        except Exception as e:
            logger.error(f"Certificate pinning bypass failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "modified_files": 0,
                "output_apk": None
            }
    
    def bypass_root_detection(self, apk_path: str, output_path: str) -> Dict[str, Any]:
        """Complete root detection bypass"""
        try:
            logger.info(f"Bypassing root detection for: {apk_path}")
            
            # Decompile APK
            decompiled_dir = f"{os.path.splitext(apk_path)[0]}_decompiled"
            subprocess.run(["apktool", "d", apk_path, "-o", decompiled_dir, "-f"], check=True)
            
            # Modify smali files
            modified_count = 0
            for root, dirs, files in os.walk(decompiled_dir):
                for file in files:
                    if file.endswith('.smali'):
                        file_path = os.path.join(root, file)
                        
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Apply root detection bypass
                        original_content = content
                        content = self.bypass_security_in_smali(content, SecurityType.ROOT_DETECTION)
                        
                        # Write back if modified
                        if content != original_content:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            modified_count += 1
            
            # Rebuild APK
            subprocess.run(["apktool", "b", decompiled_dir, "-o", output_path], check=True)
            
            # Sign the APK
            subprocess.run([
                "java", "-jar", "uber-apk-signer.jar",
                "-a", output_path
            ], check=True)
            
            return {
                "success": True,
                "modified_files": modified_count,
                "output_apk": output_path,
                "bypasses_applied": ["root_detection_bypass"]
            }
            
        except Exception as e:
            logger.error(f"Root detection bypass failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "modified_files": 0,
                "output_apk": None
            }
    
    def bypass_anti_debug(self, apk_path: str, output_path: str) -> Dict[str, Any]:
        """Complete anti-debug bypass"""
        try:
            logger.info(f"Bypassing anti-debug for: {apk_path}")
            
            # Decompile APK
            decompiled_dir = f"{os.path.splitext(apk_path)[0]}_decompiled"
            subprocess.run(["apktool", "d", apk_path, "-o", decompiled_dir, "-f"], check=True)
            
            # Modify smali files
            modified_count = 0
            for root, dirs, files in os.walk(decompiled_dir):
                for file in files:
                    if file.endswith('.smali'):
                        file_path = os.path.join(root, file)
                        
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Apply anti-debug bypass
                        original_content = content
                        content = self.bypass_security_in_smali(content, SecurityType.ANTI_DEBUG)
                        
                        # Write back if modified
                        if content != original_content:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            modified_count += 1
            
            # Rebuild APK
            subprocess.run(["apktool", "b", decompiled_dir, "-o", output_path], check=True)
            
            # Sign the APK
            subprocess.run([
                "java", "-jar", "uber-apk-signer.jar",
                "-a", output_path
            ], check=True)
            
            return {
                "success": True,
                "modified_files": modified_count,
                "output_apk": output_path,
                "bypasses_applied": ["anti_debug_bypass"]
            }
            
        except Exception as e:
            logger.error(f"Anti-debug bypass failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "modified_files": 0,
                "output_apk": None
            }
    
    def bypass_license_check(self, apk_path: str, output_path: str) -> Dict[str, Any]:
        """Complete license check bypass"""
        try:
            logger.info(f"Bypassing license check for: {apk_path}")
            
            # Decompile APK
            decompiled_dir = f"{os.path.splitext(apk_path)[0]}_decompiled"
            subprocess.run(["apktool", "d", apk_path, "-o", decompiled_dir, "-f"], check=True)
            
            # Modify smali files
            modified_count = 0
            for root, dirs, files in os.walk(decompiled_dir):
                for file in files:
                    if file.endswith('.smali'):
                        file_path = os.path.join(root, file)
                        
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Apply license check bypass
                        original_content = content
                        content = self.bypass_security_in_smali(content, SecurityType.LICENSE_CHECK)
                        
                        # Write back if modified
                        if content != original_content:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            modified_count += 1
            
            # Rebuild APK
            subprocess.run(["apktool", "b", decompiled_dir, "-o", output_path], check=True)
            
            # Sign the APK
            subprocess.run([
                "java", "-jar", "uber-apk-signer.jar",
                "-a", output_path
            ], check=True)
            
            return {
                "success": True,
                "modified_files": modified_count,
                "output_apk": output_path,
                "bypasses_applied": ["license_check_bypass"]
            }
            
        except Exception as e:
            logger.error(f"License check bypass failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "modified_files": 0,
                "output_apk": None
            }

    def detect_all_protections(self, apk_path: str) -> Dict[str, Any]:
        """Detect all security protections in APK"""
        try:
            logger.info(f"Detecting all protections in: {apk_path}")
            
            # Decompile APK to analyze smali
            decompiled_dir = f"{os.path.splitext(apk_path)[0]}_decompiled_temp"
            subprocess.run(["apktool", "d", apk_path, "-o", decompiled_dir, "-f"], check=True)
            
            all_detections = {}
            
            # Walk through all smali files
            for root, dirs, files in os.walk(decompiled_dir):
                for file in files:
                    if file.endswith('.smali'):
                        file_path = os.path.join(root, file)
                        
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Detect protections in this file
                        detections = self.detect_protections_in_smali(content)
                        
                        for security_type, instances in detections.items():
                            if security_type.value not in all_detections:
                                all_detections[security_type.value] = []
                            all_detections[security_type.value].extend(instances)
            
            # Clean up temp directory
            import shutil
            shutil.rmtree(decompiled_dir)
            
            # Remove duplicates
            for key in all_detections:
                all_detections[key] = list(set(all_detections[key]))
            
            return {
                "success": True,
                "protections_detected": all_detections,
                "total_protections": sum(len(v) for v in all_detections.values())
            }
            
        except Exception as e:
            logger.error(f"Protection detection failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "protections_detected": {},
                "total_protections": 0
            }

# Global instance
bypass_modules = SecurityBypass()

def main():
    """Main function for testing security bypasses"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python bypass_modules.py <command> <apk_path> [output_path]")
        print("Commands: bypass-all, detect-all, bypass-ssl, bypass-root, bypass-debug, bypass-license")
        return
    
    command = sys.argv[1]
    apk_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else f"CRACKED_{os.path.basename(apk_path)}"
    
    if command == "bypass-all":
        print("Applying all security bypasses...")
        
        # Apply all bypasses sequentially
        results = {
            "ssl_pinning": bypass_modules.bypass_certificate_pinning(apk_path, output_path),
            "root_detection": bypass_modules.bypass_root_detection(output_path if os.path.exists(output_path) else apk_path, output_path),
            "anti_debug": bypass_modules.bypass_anti_debug(output_path if os.path.exists(output_path) else apk_path, output_path),
            "license_check": bypass_modules.bypass_license_check(output_path if os.path.exists(output_path) else apk_path, output_path)
        }
        
        print("Bypass results:")
        for bypass_type, result in results.items():
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {bypass_type}: {result}")
    
    elif command == "detect-all":
        result = bypass_modules.detect_all_protections(apk_path)
        print(f"Protection detection results: {json.dumps(result, indent=2)}")
    
    elif command == "bypass-ssl":
        result = bypass_modules.bypass_certificate_pinning(apk_path, output_path)
        print(f"SSL pinning bypass result: {json.dumps(result, indent=2)}")
    
    elif command == "bypass-root":
        result = bypass_modules.bypass_root_detection(apk_path, output_path)
        print(f"Root detection bypass result: {json.dumps(result, indent=2)}")
    
    elif command == "bypass-debug":
        result = bypass_modules.bypass_anti_debug(apk_path, output_path)
        print(f"Anti-debug bypass result: {json.dumps(result, indent=2)}")
    
    elif command == "bypass-license":
        result = bypass_modules.bypass_license_check(apk_path, output_path)
        print(f"License check bypass result: {json.dumps(result, indent=2)}")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()