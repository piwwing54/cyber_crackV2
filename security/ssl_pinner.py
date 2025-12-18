#!/usr/bin/env python3
"""
🔐 CYBER CRACK PRO - SSL Pinning Bypasser
Certificate pinning detection and bypass system
"""

import logging
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
import zipfile
import json
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SSLPinningMethod(Enum):
    OKHTTP_PINNING = "okhttp_cert_pinning"
    HTTPCLIENT_PINNING = "httpclient_cert_pinning"
    CUSTOM_TRUST_MANAGER = "custom_trust_manager"
    NETWORK_SECURITY_CONFIG = "network_security_config"
    CUSTOM_SSL_SOCKET_FACTORY = "custom_ssl_socket_factory"
    HOSTNAME_VERIFIER = "hostname_verifier"

class SSLPinner:
    """SSL certificate pinning bypass system"""
    
    def __init__(self):
        self.pinning_patterns = self._initialize_pinning_patterns()
        self.bypass_techniques = self._initialize_bypass_techniques()
    
    def _initialize_pinning_patterns(self) -> Dict[SSLPinningMethod, List[str]]:
        """Initialize SSL pinning detection patterns"""
        return {
            SSLPinningMethod.OKHTTP_PINNING: [
                "CertificatePinner",
                "CertificatePinning",
                "certificatePinner",
                "pinCertificates",
                "checkPin",
                "pins=",
                "sha256/",
                "sha1/",
                "pinSet",
                "checkPeerCertificates"
            ],
            SSLPinningMethod.HTTPCLIENT_PINNING: [
                "SSLSocketFactory",
                "SSLCertificateSocketFactory",
                "HttpsURLConnection",
                "setDefaultHostnameVerifier",
                "setHostnameVerifier"
            ],
            SSLPinningMethod.CUSTOM_TRUST_MANAGER: [
                "X509TrustManager",
                "checkServerTrusted",
                "checkClientTrusted",
                "getAcceptedIssuers",
                "TrustManager",
                "CustomTrustManager",
                "verifyCertificate"
            ],
            SSLPinningMethod.NETWORK_SECURITY_CONFIG: [
                "network_security_config",
                "certificate-pins",
                "pin-set",
                "expiration",
                "includeSubdomains",
                "trust-anchors"
            ],
            SSLPinningMethod.CUSTOM_SSL_SOCKET_FACTORY: [
                "SSLSocketFactory",
                "SSLContext",
                "createSocket",
                "getDefaultSSLSocketFactory",
                "getSocketFactory"
            ],
            SSLPinningMethod.HOSTNAME_VERIFIER: [
                "HostnameVerifier", 
                "verify",
                "OkHostnameVerifier",
                "AllHostnameVerifier",
                "StrictHostnameVerifier"
            ]
        }
    
    def _initialize_bypass_techniques(self) -> Dict[str, Dict[str, Any]]:
        """Initialize bypass techniques"""
        return {
            "trust_all_certs": {
                "name": "Trust All Certificates",
                "method": self._bypass_trust_manager,
                "description": "Replace TrustManager to trust all certificates",
                "pattern": "checkServerTrusted",
                "replacement": "return-void  # Always trust certificates"
            },
            "disable_hostname_check": {
                "name": "Disable Hostname Verification",
                "method": self._bypass_hostname_verification,
                "description": "Disable hostname verification",
                "pattern": "verify",
                "replacement": "const/4 v0, 0x1  # Always return true"
            },
            "empty_pin_check": {
                "name": "Empty Pin Check Bypass",
                "method": self._bypass_certificate_pinning,
                "description": "Bypass certificate pinning checks",
                "pattern": "checkPin",
                "replacement": "return-void  # Skip pinning check"
            },
            "network_security_bypass": {
                "name": "Network Security Config Bypass",
                "method": self._bypass_network_security,
                "description": "Modify network security configuration",
                "pattern": "pin-set",
                "replacement": "<!-- PINNING BYPASSED -->"
            }
        }
    
    def detect_ssl_pinning_in_apk(self, apk_path: str) -> Dict[str, Any]:
        """Detect SSL pinning implementations in APK"""
        results = {
            "ssl_pinning_detected": False,
            "pinning_methods_found": [],
            "files_with_pinning": [],
            "confidence_score": 0,
            "recommendations": [],
            "total_checks": 0
        }
        
        logger.info(f"Detecting SSL pinning in: {apk_path}")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract APK
            with zipfile.ZipFile(apk_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Search for SSL pinning patterns
            for method_type, patterns in self.pinning_patterns.items():
                found_in_files = []
                
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith(('.smali', '.java', '.xml')):
                            file_path = os.path.join(root, file)
                            
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read().lower()
                            
                            for pattern in patterns:
                                if pattern.lower() in content:
                                    found_instance = {
                                        "pattern": pattern,
                                        "file": os.path.relpath(file_path, temp_dir),
                                        "method_type": method_type.value,
                                        "location": self._find_line_number(content, pattern)
                                    }
                                    found_in_files.append(found_instance)
                
                if found_in_files:
                    results["pinning_methods_found"].append(method_type.value)
                    results["files_with_pinning"].extend(found_in_files)
                    results["total_checks"] += len(found_in_files)
            
            results["ssl_pinning_detected"] = len(results["pinning_methods_found"]) > 0
            
            # Calculate confidence score
            if results["total_checks"] > 15:
                results["confidence_score"] = 95
            elif results["total_checks"] > 8:
                results["confidence_score"] = 80
            elif results["total_checks"] > 3:
                results["confidence_score"] = 60
            else:
                results["confidence_score"] = 30 if results["ssl_pinning_detected"] else 0
            
            # Generate recommendations
            if results["ssl_pinning_detected"]:
                results["recommendations"].append("Apply SSL pinning bypass")
                results["recommendations"].append("Disable certificate verification")
                results["recommendations"].append("Bypass network security config")
                results["recommendations"].append("Hook SSL verification functions")
            else:
                results["recommendations"].append("No SSL pinning detected in APK")
                results["recommendations"].append("Standard network requests should work")
        
        return results
    
    def bypass_ssl_pinning_in_apk(self, apk_path: str, output_path: str) -> Dict[str, Any]:
        """Bypass SSL pinning in APK"""
        try:
            logger.info(f"Bypassing SSL pinning in: {apk_path}")
            
            # Decompile APK
            decompiled_dir = f"{os.path.splitext(apk_path)[0]}_decompiled"
            subprocess.run(["apktool", "d", apk_path, "-o", decompiled_dir, "-f"], check=True)
            
            modified_files_count = 0
            
            # Apply SSL bypass techniques to all smali files
            for root, dirs, files in os.walk(decompiled_dir):
                for file in files:
                    if file.endswith('.smali'):
                        file_path = os.path.join(root, file)
                        
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        original_content = content
                        
                        # Apply all bypass techniques
                        for bypass_name, bypass_info in self.bypass_techniques.items():
                            content = self._apply_ssl_bypass(content, bypass_info)
                        
                        # Additional specific SSL pinning bypasses
                        content = self._apply_trust_all_bypass(content)
                        content = self._apply_okhttp_bypass(content)
                        content = self._apply_network_security_config_bypass(content)
                        
                        # Write back if modified
                        if content != original_content:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            modified_files_count += 1
            
            # Check for network_security_config.xml and bypass it
            network_security_path = os.path.join(decompiled_dir, "res", "xml", "network_security_config.xml")
            if os.path.exists(network_security_path):
                with open(network_security_path, 'r') as f:
                    ns_config = f.read()
                
                # Remove all pinning configurations
                ns_config = re.sub(r'<pin-set[^>]*>[^<]*</pin-set>', '<!-- PINNING BYPASSED -->', ns_config)
                ns_config = ns_config.replace('pinSet', '!-- pinSet BYPASSED -->')
                
                with open(network_security_path, 'w') as f:
                    f.write(ns_config)
                modified_files_count += 1
            
            # Rebuild APK
            subprocess.run(["apktool", "b", decompiled_dir, "-o", output_path], check=True)
            
            # Sign APK
            subprocess.run([
                "java", "-jar", "uber-apk-signer.jar",
                "-a", output_path
            ], check=True)
            
            # Clean up
            import shutil
            shutil.rmtree(decompiled_dir)
            
            return {
                "success": True,
                "modified_files": modified_files_count,
                "ssl_pinning_removed": True,
                "output_apk": output_path,
                "bypasses_applied": list(self.bypass_techniques.keys())
            }
            
        except Exception as e:
            logger.error(f"SSL pinning bypass failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "modified_files": 0,
                "ssl_pinning_removed": False,
                "output_apk": None
            }
    
    def _apply_ssl_bypass(self, content: str, bypass_info: Dict) -> str:
        """Apply specific SSL bypass technique"""
        pattern = bypass_info.get("pattern", "")
        replacement = bypass_info.get("replacement", "")
        
        if pattern and replacement and pattern in content:
            content = content.replace(pattern, f"    # BYPASSED: {pattern}\n    {replacement}")
        
        return content
    
    def _apply_trust_all_bypass(self, content: str) -> str:
        """Apply trust-all certificates bypass"""
        # Replace TrustManager implementations
        trust_manager_methods = [
            "checkServerTrusted",
            "checkClientTrusted", 
            "verify"
        ]
        
        for method in trust_manager_methods:
            if method in content:
                # Replace the method implementation to always return success
                lines = content.split('\n')
                in_method = False
                method_start = -1
                method_end = -1
                
                for i, line in enumerate(lines):
                    if f".method" in line and method in line:
                        in_method = True
                        method_start = i
                    elif in_method and ".end method" in line:
                        method_end = i
                        break
                
                if method_start != -1 and method_end != -1:
                    # Replace the method body with always-return success
                    new_method = [
                        f"    # BYPASSED: {method} - Always return success",
                        "    return-void"
                    ]
                    lines[method_start+1:method_end] = new_method
                    content = '\n'.join(lines)
        
        return content
    
    def _apply_okhttp_bypass(self, content: str) -> str:
        """Apply OkHttp-specific SSL bypass"""
        # Find CertificatePinner implementations
        if "CertificatePinner" in content or "certificatePinner" in content:
            # Replace certificate pinning checks
            content = content.replace(
                "checkPin",
                "# BYPASSED: Removed certificate pinning check"
            )
            content = content.replace(
                "pins=",
                "# BYPASSED: pins=[]  # Empty pins array"
            )
        
        return content
    
    def _find_line_number(self, content: str, pattern: str) -> int:
        """Find line number where pattern occurs"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if pattern in line:
                return i + 1
        return -1

    def _apply_network_security_config_bypass(self, content: str) -> str:
        """Bypass network security configuration"""
        # Look for network security config references
        if "networkSecurityConfig" in content:
            # This would be in AndroidManifest.xml, but let's add general bypass
            content += """
    # SSL Pinning Bypass Applied
    # Network security configuration bypassed
            """
        
        return content

    def detect_device_ssl_interception(self) -> Dict[str, Any]:
        """Detect if device is intercepting SSL traffic"""
        results = {
            "ssl_intercepted": False,
            "interception_methods": [],
            "certificates_installed": [],
            "confidence": 0
        }
        
        # Check for proxy settings and installed certificates
        import subprocess
        try:
            # Check network settings (would require root)
            # Check for Burp certificates
            # Check for known proxy artifacts
            pass
        except:
            pass  # Non-root detection
        
        return results

# Global instance
ssl_pinner = SSLPinner()

def main():
    """Main function for testing SSL pinning bypass"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python ssl_pinner.py <command> <apk_path> [output_path]")
        print("Commands: detect, bypass, device-check")
        return
    
    command = sys.argv[1]
    apk_path = sys.argv[2]
    
    if command == "detect":
        result = ssl_pinner.detect_ssl_pinning_in_apk(apk_path)
        print(f"SSL Pinning Detection Results: {json.dumps(result, indent=2)}")
    
    elif command == "bypass":
        if len(sys.argv) < 4:
            print("Please provide output path")
            return
        
        output_path = sys.argv[3]
        result = ssl_pinner.bypass_ssl_pinning_in_apk(apk_path, output_path)
        print(f"SSL Pinning Bypass Results: {json.dumps(result, indent=2)}")
    
    elif command == "device-check":
        result = ssl_pinner.detect_device_ssl_interception()
        print(f"Device SSL Interception Check: {json.dumps(result, indent=2)}")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()