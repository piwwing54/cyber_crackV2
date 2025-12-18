#!/usr/bin/env python3
"""
🛡️ CYBER CRACK PRO - Anti Debug Detector
Anti-debugging detection and bypass system
"""

import logging
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import zipfile
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AntiDebugMethod(Enum):
    DEBUGGER_CONN_CHECK = "debugger_connection_check"
    TRACER_ATTACH_CHECK = "tracer_attachment_check"
    DEBUG_FLAG_CHECK = "debug_flag_check"
    PTRACE_PROTECTION = "ptrace_protection"
    JDWP_CHECK = "jdwp_check"
    MEMORY_DUMP_PROTECTION = "memory_dump_protection"
    INTENT_FILTER_PROTECTION = "intent_filter_protection"
    BUILD_CONFIG_CHECK = "build_config_check"
    PROCESS_NAME_CHECK = "process_name_check"
    THREAD_COUNT_CHECK = "thread_count_check"

class AntiDebug:
    """Anti-debugging detection and bypass system"""
    
    def __init__(self):
        self.debug_patterns = self._initialize_debug_patterns()
        self.bypass_techniques = self._initialize_bypass_techniques()
    
    def _initialize_debug_patterns(self) -> Dict[AntiDebugMethod, List[str]]:
        """Initialize anti-debug detection patterns"""
        return {
            AntiDebugMethod.DEBUGGER_CONN_CHECK: [
                "isDebuggerConnected",
                "Debug.isDebuggerConnected",
                "isWaitingForDebugger",
                "Debug.isWaitingForDebugger",
                "waitingForDebugger",
                "debuggerConnected"
            ],
            AntiDebugMethod.TRACER_ATTACH_CHECK: [
                "TracerPid",
                "ptrace",
                "PTRACE",
                "attach",
                "PTRACE_ATTACH",
                "PTRACE_TRACEME"
            ],
            AntiDebugMethod.DEBUG_FLAG_CHECK: [
                "DEBUG",
                "BuildConfig.DEBUG",
                "getApplicationInfo.flags",
                "FLAG_DEBUGGABLE",
                "debuggable"
            ],
            AntiDebugMethod.JDWP_CHECK: [
                "JDWP",
                "jdwp",
                "Jdwp",
                "JDWPTransport",
                "transport",
                "dt_android"
            ],
            AntiDebugMethod.BUILD_CONFIG_CHECK: [
                "BuildConfig.DEBUG",
                "BuildConfig",
                "DEBUG=true",
                "DEBUG_MODE",
                "isDebug"
            ],
            AntiDebugMethod.PROCESS_NAME_CHECK: [
                "getProcessName",
                "processName",
                "gdb",
                "gdbserver",
                "strace",
                "ltrace"
            ],
            AntiDebugMethod.THREAD_COUNT_CHECK: [
                "Thread.activeCount",
                "thread count",
                "threads",
                "ThreadGroup"
            ],
            AntiDebugMethod.MEMORY_DUMP_PROTECTION: [
                "memory",
                "dump",
                "memoryDump",
                "procmem",
                "/proc/self/mem"
            ],
            AntiDebugMethod.INTENT_FILTER_PROTECTION: [
                "android.intent.action.DEBUG",
                "DEBUG_INTENT",
                "debugIntent"
            ]
        }
    
    def _initialize_bypass_techniques(self) -> Dict[str, Dict[str, Any]]:
        """Initialize bypass techniques"""
        return {
            "debugger_bypass": {
                "name": "Debugger Connection Bypass",
                "method": self._bypass_debugger_check,
                "description": "Always return false for debugger detection",
                "pattern": "invoke-static {}, Landroid/os/Debug;->isDebuggerConnected()Z",
                "replacement": "    const/4 v0, 0x0  # Always return false"
            },
            "tracer_bypass": {
                "name": "Tracer Attachment Bypass",
                "method": self._bypass_tracer_check,
                "description": "Bypass TracerPid checks",
                "pattern": "TracerPid",
                "replacement": "FakeTracerPid  # Bypassed"
            },
            "debug_flag_bypass": {
                "name": "Debug Flag Bypass",
                "method": self._bypass_debug_flag,
                "description": "Bypass debug flag checks",
                "pattern": "BuildConfig.DEBUG",
                "replacement": "    const/4 v0, 0x0  # Always false"
            },
            "ptrace_bypass": {
                "name": "Ptrace Protection Bypass",
                "method": self._bypass_ptrace,
                "description": "Bypass ptrace protections",
                "pattern": "ptrace",
                "replacement": "// Ptrace bypassed"
            },
            "jdwp_bypass": {
                "name": "JDWP Protection Bypass",
                "method": self._bypass_jdwp,
                "description": "Bypass JDWP transport checks",
                "pattern": "JDWP",
                "replacement": "# JDWP checks bypassed"
            }
        }
    
    def detect_anti_debug_in_apk(self, apk_path: str) -> Dict[str, Any]:
        """Detect anti-debug mechanisms in APK"""
        results = {
            "anti_debug_detected": False,
            "methods_found": [],
            "files_with_debug_protection": [],
            "confidence_score": 0,
            "recommendations": [],
            "total_checks": 0
        }
        
        logger.info(f"Detecting anti-debug protections in: {apk_path}")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract APK
            with zipfile.ZipFile(apk_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Search for anti-debug patterns
            for method_type, patterns in self.debug_patterns.items():
                found_in_files = []
                
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith(('.smali', '.java')):
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
                    results["methods_found"].append(method_type.value)
                    results["files_with_debug_protection"].extend(found_in_files)
                    results["total_checks"] += len(found_in_files)
            
            results["anti_debug_detected"] = len(results["methods_found"]) > 0
            
            # Calculate confidence score
            if results["total_checks"] > 10:
                results["confidence_score"] = 90
            elif results["total_checks"] > 5:
                results["confidence_score"] = 70
            elif results["total_checks"] > 2:
                results["confidence_score"] = 50
            else:
                results["confidence_score"] = 20 if results["anti_debug_detected"] else 0
            
            # Generate recommendations
            if results["anti_debug_detected"]:
                results["recommendations"].append("Apply anti-debug bypass techniques")
                results["recommendations"].append("Disable debugger connection checks")
                results["recommendations"].append("Bypass tracer attachment detection")
                results["recommendations"].append("Remove debug flag validations")
            else:
                results["recommendations"].append("No anti-debug protections detected")
                results["recommendations"].append("Standard debugging should work")
        
        return results
    
    def bypass_anti_debug_in_apk(self, apk_path: str, output_path: str) -> Dict[str, Any]:
        """Bypass anti-debug mechanisms in APK"""
        try:
            logger.info(f"Bypassing anti-debug in: {apk_path}")
            
            # Decompile APK
            decompiled_dir = f"{os.path.splitext(apk_path)[0]}_decompiled"
            subprocess.run(["apktool", "d", apk_path, "-o", decompiled_dir, "-f"], check=True)
            
            modified_files_count = 0
            
            # Apply anti-debug bypasses to all smali files
            for root, dirs, files in os.walk(decompiled_dir):
                for file in files:
                    if file.endswith('.smali'):
                        file_path = os.path.join(root, file)
                        
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        original_content = content
                        
                        # Apply all bypass techniques
                        for bypass_name, bypass_info in self.bypass_techniques.items():
                            content = self._apply_anti_debug_bypass(content, bypass_info)
                        
                        # Additional specific anti-debug bypasses
                        content = self._apply_debugger_detection_bypass(content)
                        content = self._apply_build_config_bypass(content)
                        content = self._apply_native_debug_bypass(content)
                        
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
            
            # Clean up
            import shutil
            shutil.rmtree(decompiled_dir)
            
            return {
                "success": True,
                "modified_files": modified_files_count,
                "anti_debug_removed": True,
                "output_apk": output_path,
                "bypasses_applied": list(self.bypass_techniques.keys())
            }
            
        except Exception as e:
            logger.error(f"Anti-debug bypass failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "modified_files": 0,
                "anti_debug_removed": False,
                "output_apk": None
            }
    
    def _apply_anti_debug_bypass(self, content: str, bypass_info: Dict) -> str:
        """Apply specific anti-debug bypass technique"""
        pattern = bypass_info.get("pattern", "")
        replacement = bypass_info.get("replacement", "")
        
        if pattern and replacement and pattern in content:
            # Apply the bypass by replacing patterns
            content = content.replace(pattern, f"    # BYPASSED: {pattern}\n{replacement}")
        
        return content
    
    def _apply_debugger_detection_bypass(self, content: str) -> str:
        """Apply debugger detection bypass specifically"""
        # Find method calls that check for debugger
        debugger_calls = [
            "isDebuggerConnected",
            "isWaitingForDebugger", 
            "Debug.isDebuggerConnected",
            "Debug.isWaitingForDebugger"
        ]
        
        for call in debugger_calls:
            if call in content:
                # Find the method that contains this call and modify return value
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if call in line and "invoke-static" in line:
                        # Find the next move-result or return instruction
                        for j in range(i, min(i+10, len(lines))):
                            if "move-result" in lines[j] or "return" in lines[j]:
                                # Change the return value to false (0x0)
                                lines[j] = f"    # BYPASSED: debugger check\n    const/4 v0, 0x0  # Always return false\n    return v0"
                                break
                content = '\n'.join(lines)
        
        return content
    
    def _apply_build_config_bypass(self, content: str) -> str:
        """Bypass BuildConfig.DEBUG checks"""
        if "BuildConfig.DEBUG" in content:
            # Replace BuildConfig.DEBUG checks with false
            content = content.replace(
                "BuildConfig.DEBUG",
                "# BYPASSED: BuildConfig.DEBUG\nconst/4 v0, 0x0  # Always return false"
            )
        
        # Also look for FLAG_DEBUGGABLE checks
        if "FLAG_DEBUGGABLE" in content:
            content = content.replace(
                "FLAG_DEBUGGABLE",
                "# BYPASSED: FLAG_DEBUGGABLE\nconst/16 v0, 0x0  # Always return false"
            )
        
        return content
    
    def _apply_native_debug_bypass(self, content: str) -> str:
        """Bypass native debugging protections"""
        # Look for ptrace calls in native code
        if "ptrace" in content:
            content = content.replace(
                "native ptrace",
                "// BYPASSED: native ptrace protection"
            )
        
        # Look for native debug functions
        native_debug_funcs = [
            "isDebugging",
            "checkDebug",
            "detectDebug",
            "verifyDebug"
        ]
        
        for func in native_debug_funcs:
            if func in content:
                # Replace function implementations that return boolean values
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if f"{func}()" in line and "Z" in line:  # Boolean return method
                        # Find where this function returns and ensure it returns false
                        for j in range(i, min(i+20, len(lines))):
                            if "return" in lines[j]:
                                lines[j] = "    const/4 v0, 0x0  # Bypassed native debug check\n    return v0"
                                break
                content = '\n'.join(lines)
        
        return content
    
    def _find_line_number(self, content: str, pattern: str) -> int:
        """Find line number where pattern occurs"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if pattern in line:
                return i + 1
        return -1
    
    def detect_device_debug_status(self) -> Dict[str, Any]:
        """Detect if device is in debug mode"""
        results = {
            "debug_enabled": False,
            "debug_methods_detected": [],
            "security_risk": 0,
            "recommendations": []
        }
        
        # Check if debugging is enabled (this would require root or special permissions)
        # This is a placeholder for actual device detection
        results["recommendations"].append("Use on non-development device for better results")
        results["recommendations"].append("Disable USB debugging if not needed")
        
        return results

# Global instance
anti_debug = AntiDebug()

def main():
    """Main function for testing anti-debug detection and bypass"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python anti_debug.py <command> <apk_path> [output_path]")
        print("Commands: detect, bypass, device-check")
        return
    
    command = sys.argv[1]
    apk_path = sys.argv[2]
    
    if command == "detect":
        result = anti_debug.detect_anti_debug_in_apk(apk_path)
        print(f"Anti-Debug Detection Results: {json.dumps(result, indent=2)}")
    
    elif command == "bypass":
        if len(sys.argv) < 4:
            print("Please provide output path")
            return
        
        output_path = sys.argv[3]
        result = anti_debug.bypass_anti_debug_in_apk(apk_path, output_path)
        print(f"Anti-Debug Bypass Results: {json.dumps(result, indent=2)}")
    
    elif command == "device-check":
        result = anti_debug.detect_device_debug_status()
        print(f"Device Debug Status: {json.dumps(result, indent=2)}")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()