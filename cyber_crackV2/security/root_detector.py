#!/usr/bin/env python3
"""
🛡️ CYBER CRACK PRO - Root Detector
Advanced root/jailbreak detection and bypass system
"""

import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import zipfile
import tempfile
import asyncio
import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RootDetectionMethod(Enum):
    FILE_CHECKS = "file_checks"
    BINARY_CHECKS = "binary_checks"
    API_CHECKS = "api_checks"
    PERMISSION_CHECKS = "permission_checks"
    HARDWARE_CHECKS = "hardware_checks"
    PROC_CHECKS = "proc_checks"

class RootDetector:
    """Advanced root detection and bypass system"""
    
    def __init__(self):
        self.detection_patterns = self._initialize_detection_patterns()
        self.bypass_techniques = self._initialize_bypass_techniques()
    
    def _initialize_detection_patterns(self) -> Dict[RootDetectionMethod, List[str]]:
        """Initialize root detection patterns"""
        return {
            RootDetectionMethod.FILE_CHECKS: [
                "/system/app/Superuser.apk",
                "/sbin/su",
                "/system/bin/su",
                "/system/xbin/su",
                "/data/local/xbin/su",
                "/data/local/bin/su",
                "/system/sd/xbin/su",
                "/system/bin/failsafe/su",
                "/data/local/su",
                "/su/bin/su",
                "/system/etc/init.d/99SuperSUDaemon",
                "/system/bin/.ext/.su",
                "/system/usr/we-need-root/",
                "/system/app/Kinguser.apk",
                "/system/app/kingroot.apk",
                "/system/app/SuperRoot.apk",
                "/system/app/RootBrowser.apk",
                "/system/app/RootEssential.apk",
                "/system/app/RootExplorer.apk",
                "/system/app/RootPA.apk",
                "/system/app/RootTools.apk",
                "/system/app/RootBox.apk",
                "/system/app/DroidSheep.apk",
                "/system/app/DSHelper.apk",
                "/system/app/DSServiceApp.apk",
                "/system/app/RO.otk",
                "/system/app/eoe.apk",
                "/system/app/RROot.apk",
                "/system/app/RootCheck.apk",
                "/system/app/Rootkilla.apk",
                "/system/app/RootUninstall.apk",
                "/system/app/Superuser/",
                "/system/app/eoe/",
                "/system/app/Rootcloak/",
                "/system/app/Rootcloak2/",
                "/system/app/Rootcloak3/",
                "/system/app/Rootcloak4/",
                "/system/app/Rootcloak5/",
                "/system/app/Rootcloak6/",
                "/system/app/Rootcloak7/",
                "/system/app/Rootcloak8/",
                "/system/app/Rootcloak9/",
                "/system/app/Rootcloak10/",
                "/system/app/XPrivacy/",
                "/system/app/XPrivacy2/",
                "/system/app/XPrivacy3/",
                "/system/app/XPrivacy4/",
                "/system/app/XPrivacy5/",
                "/system/app/XPrivacy6/",
                "/system/app/XPrivacy7/",
                "/system/app/XPrivacy8/",
                "/system/app/XPrivacy9/",
                "/system/app/XPrivacy10/",
            ],
            RootDetectionMethod.BINARY_CHECKS: [
                "su",
                "busybox",
                "Superuser",
                "RootTools",
                "isRooted",
                "RootBeer",
                "checkRoot",
                "Superuser",
                "Magisk",
                "Xposed",
                "Substrate",
                "Cydia",
                "Sileo",
                "Zebra",
                "Frida",
                "objection",
                "inspeckage",
            ],
            RootDetectionMethod.API_CHECKS: [
                "RootTools.isRooted",
                "RootBeer.isRooted",
                "checkRoot",
                "isRooted",
                "hasSuperuser",
                "Superuser detected",
                "checkSuExists",
                "checkForRoot",
                "checkForBinary",
                "RootBeer.checkForRoot",
                "RootTools.checkForRoot",
                "isDeviceRooted",
                "checkRootMethod",
            ],
            RootDetectionMethod.PERMISSION_CHECKS: [
                "android.permission.ACCESS_SUPERUSER",
                "REQUEST_IGNORE_BATTERY_OPTIMIZATIONS",
                "SYSTEM_ALERT_WINDOW",
            ],
            RootDetectionMethod.HARDWARE_CHECKS: [
                "ro.product.manufacturer: unknown",
                "ro.product.brand: generic",
                "ro.hardware: goldfish",
                "ro.kernel.qemu: 1",
                "ro.crypto.state: encrypted",
            ],
            RootDetectionMethod.PROC_CHECKS: [
                "TracerPid",
                "/proc/self/status",
                "/proc/self/maps",
                "/proc/self/mem",
                "/proc/mounts",
                "/proc/version",
            ]
        }
    
    def _initialize_bypass_techniques(self) -> Dict[str, Dict[str, Any]]:
        """Initialize bypass techniques"""
        return {
            "file_checks_bypass": {
                "name": "File Checks Bypass",
                "method": self._bypass_file_checks,
                "description": "Hide root files by returning false for file existence checks",
                "smali_pattern": "Ljava/io/File;->exists()Z",
                "replacement": "const/4 v0, 0x0  # Always return false"
            },
            "api_checks_bypass": {
                "name": "API Checks Bypass",
                "method": self._bypass_api_checks,
                "description": "Bypass API-based root detection calls",
                "smali_pattern": "invoke-static {}, LRootTools;->isRooted()Z",
                "replacement": "const/4 v0, 0x0  # Always return false"
            },
            "binary_checks_bypass": {
                "name": "Binary Checks Bypass",
                "method": self._bypass_binary_checks,
                "description": "Bypass binary existence checks",
                "smali_pattern": "invoke-static {p0}, Ljava/lang/Runtime;->exec(Ljava/lang/String;)Ljava/lang/Process;",
                "replacement": "const/4 v0, 0x0  # Always return false"
            },
            "permission_checks_bypass": {
                "name": "Permission Checks Bypass",
                "method": self._bypass_permission_checks,
                "description": "Bypass permission-based checks",
                "smali_pattern": "checkCallingPermission",
                "replacement": "const/4 v0, 0x0  # Always return false"
            }
        }
    
    async def detect_root_in_apk(self, apk_path: str) -> Dict[str, Any]:
        """Detect root detection mechanisms in APK"""
        results = {
            "root_detection_found": False,
            "detection_types_found": [],
            "specific_checks_found": [],
            "confidence_score": 0,
            "recommendations": [],
            "total_checks": 0
        }
        
        logger.info(f"Detecting root checks in: {apk_path}")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract APK
            with zipfile.ZipFile(apk_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Search for root detection patterns
            for detection_type, patterns in self.detection_patterns.items():
                found_in_files = []
                
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith('.smali'):
                            file_path = os.path.join(root, file)
                            
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read().lower()
                            
                            for pattern in patterns:
                                if pattern.lower() in content:
                                    found_instance = {
                                        "pattern": pattern,
                                        "file": os.path.relpath(file_path, temp_dir),
                                        "type": detection_type.value
                                    }
                                    found_in_files.append(found_instance)
                
                if found_in_files:
                    results["detection_types_found"].append(detection_type.value)
                    results["specific_checks_found"].extend(found_in_files)
                    results["total_checks"] += len(found_in_files)
            
            results["root_detection_found"] = len(results["detection_types_found"]) > 0
            
            # Calculate confidence score
            if results["total_checks"] > 10:
                results["confidence_score"] = 95
            elif results["total_checks"] > 5:
                results["confidence_score"] = 80
            elif results["total_checks"] > 0:
                results["confidence_score"] = 60
            else:
                results["confidence_score"] = 0
            
            # Generate recommendations
            if results["root_detection_found"]:
                results["recommendations"].append("Apply root detection bypasses")
                results["recommendations"].append("Hide root artifacts and binaries")
                results["recommendations"].append("Modify file access patterns")
                results["recommendations"].append("Hook system API calls")
            else:
                results["recommendations"].append("APK has no apparent root detection")
                results["recommendations"].append("May not need root bypass")
        
        return results
    
    def bypass_root_detection_in_apk(self, apk_path: str, output_path: str) -> Dict[str, Any]:
        """Bypass all root detection in APK"""
        try:
            logger.info(f"Bypassing root detection in: {apk_path}")
            
            # Decompile APK
            decompiled_dir = f"{os.path.splitext(apk_path)[0]}_decompiled"
            subprocess.run(["apktool", "d", apk_path, "-o", decompiled_dir, "-f"], check=True)
            
            modified_files_count = 0
            
            # Apply bypasses to all smali files
            for root, dirs, files in os.walk(decompiled_dir):
                for file in files:
                    if file.endswith('.smali'):
                        file_path = os.path.join(root, file)
                        
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        original_content = content
                        
                        # Apply all bypass techniques
                        for bypass_name, bypass_info in self.bypass_techniques.items():
                            content = self._apply_bypass_to_content(content, bypass_info)
                        
                        # Write back if modified
                        if content != original_content:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            modified_files_count += 1
            
            # Rebuild APK
            subprocess.run(["apktool", "b", decompiled_dir, "-o", output_path], check=True)
            
            # Sign APK  
            subprocess.run([
                "java", "-jar", "uber-apk-signer.jar",
                "-a", output_path
            ], check=True)
            
            return {
                "success": True,
                "modified_files": modified_files_count,
                "root_detection_removed": True,
                "output_apk": output_path,
                "bypasses_applied": list(self.bypass_techniques.keys())
            }
            
        except Exception as e:
            logger.error(f"Root detection bypass failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "modified_files": 0,
                "root_detection_removed": False,
                "output_apk": None
            }
    
    def _apply_bypass_to_content(self, content: str, bypass_info: Dict) -> str:
        """Apply a specific bypass technique to content"""
        # Apply the bypass pattern replacement
        pattern = bypass_info.get("smali_pattern", "")
        replacement = bypass_info.get("replacement", "")
        
        if pattern and replacement:
            content = content.replace(pattern, f"    # BYPASSED: {pattern}\n    {replacement}")
        
        return content
    
    def _bypass_file_checks(self, smali_content: str) -> str:
        """Bypass file existence checks"""
        for pattern in self.detection_patterns[RootDetectionMethod.FILE_CHECKS]:
            if pattern in smali_content:
                # Replace File.exists() calls with constant false
                lines = smali_content.split('\n')
                for i, line in enumerate(lines):
                    if pattern in line and "File;" in line and "exists()" in line:
                        # Find the return statement that follows and replace with false
                        for j in range(i, min(i+5, len(lines))):
                            if "return" in lines[j]:
                                lines[j] = "    const/4 v0, 0x0  # Always return false\n    return v0"
                                break
                smali_content = '\n'.join(lines)
        
        return smali_content
    
    def _bypass_api_checks(self, smali_content: str) -> str:
        """Bypass API-based root checks"""
        for pattern in self.detection_patterns[RootDetectionMethod.API_CHECKS]:
            if pattern in smali_content:
                # Replace API call with constant false return
                smali_content = smali_content.replace(
                    f"invoke-static {{}}, L{pattern}",
                    "# BYPASSED API CHECK\n    const/4 v0, 0x0  # Always return false"
                )
        
        return smali_content
    
    def _bypass_binary_checks(self, smali_content: str) -> str:
        """Bypass binary existence checks"""
        for binary_name in self.detection_patterns[RootDetectionMethod.BINARY_CHECKS]:
            if binary_name in smali_content:
                # Replace Runtime.exec calls for root binaries with success indicators
                lines = smali_content.split('\n')
                for i, line in enumerate(lines):
                    if binary_name in line and "exec" in line:
                        # Replace with successful execution
                        lines[i] = f"    # BYPASSED: {binary_name} check\n    const/4 v0, 0x0  # Process exits with success"
                smali_content = '\n'.join(lines)
        
        return smali_content
    
    def _bypass_permission_checks(self, smali_content: str) -> str:
        """Bypass permission checks"""
        for permission in self.detection_patterns[RootDetectionMethod.PERMISSION_CHECKS]:
            if permission in smali_content:
                # Replace permission check with granted
                smali_content = smali_content.replace(
                    "checkCallingPermission",
                    "const/4 v0, 0x0  # Permission granted"
                )
        
        return smali_content
    
    def detect_device_root_status(self) -> Dict[str, Any]:
        """Detect if the current device is rooted"""
        results = {
            "is_rooted": False,
            "root_artifacts_found": [],
            "confidence": 0,
            "checks_performed": 0
        }
        
        # Check for common root artifacts
        artifacts_to_check = [
            ("/system/app/Superuser.apk", "Superuser app"),
            ("/system/bin/su", "su binary in /system/bin"),
            ("/system/xbin/su", "su binary in /system/xbin"),
            ("/system/sbin/su", "su binary in /system/sbin"),
            ("/data/local/su", "su binary in /data/local"),
            ("/data/local/bin/su", "su binary in /data/local/bin"),
            ("/data/local/xbin/su", "su binary in /data/local/xbin"),
            ("/system/xbin/busybox", "busybox binary"),
            ("/system/bin/busybox", "busybox binary"),
        ]
        
        for artifact_path, artifact_desc in artifacts_to_check:
            if os.path.exists(artifact_path):
                results["root_artifacts_found"].append(artifact_path)
                results["is_rooted"] = True
        
        # Check for Magisk (newer root solution)
        magisk_check = [
            "/sbin/.magisk",
            "/data/adb/magisk",
            "/system/bin/magisk"
        ]
        
        for magisk_path in magisk_check:
            if os.path.exists(magisk_path):
                results["root_artifacts_found"].append(magisk_path)
                results["is_rooted"] = True
        
        # Check for root management apps
        system_apps = "/system/app"
        if os.path.exists(system_apps):
            for root_app in ["Kinguser", "Root", "Xposed"]:
                for root, dirs, files in os.walk(system_apps):
                    for dir_name in dirs:
                        if root_app.lower() in dir_name.lower():
                            results["root_artifacts_found"].append(f"{root}/{dir_name}")
                            results["is_rooted"] = True
        
        # Calculate confidence
        results["confidence"] = min(len(results["root_artifacts_found"]) * 20, 100)
        results["checks_performed"] = len(artifacts_to_check) + len(magisk_check)
        
        return results

# Global instance
root_detector = RootDetector()

def main():
    """Main function for testing root detection"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python root_detector.py <command> <apk_path> [output_path]")
        print("Commands: detect, bypass, device-check")
        return
    
    command = sys.argv[1]
    apk_path = sys.argv[2]
    
    if command == "detect":
        result = root_detector.detect_root_in_apk(apk_path)
        print(f"Root Detection Results: {json.dumps(result, indent=2)}")
    
    elif command == "bypass":
        if len(sys.argv) < 4:
            print("Please provide output path")
            return
        
        output_path = sys.argv[3]
        result = root_detector.bypass_root_detection_in_apk(apk_path, output_path)
        print(f"Root Bypass Results: {json.dumps(result, indent=2)}")
    
    elif command == "device-check":
        result = root_detector.detect_device_root_status()
        print(f"Device Root Status: {json.dumps(result, indent=2)}")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()