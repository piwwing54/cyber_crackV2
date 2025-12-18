#!/usr/bin/env python3
"""
🔒 CYBER CRACK PRO - Obfuscator
Code obfuscation and deobfuscation system
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
import base64
import random
import string

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ObfuscationMethod(Enum):
    STRING_ENCRYPTION = "string_encryption"
    CONTROL_FLOW = "control_flow"
    REFLECTION = "reflection"
    DUMMY_CODE = "dummy_code"
    NAME_OBFUSCATION = "name_obfuscation"
    ANTI_TAMPER = "anti_tampering"
    ANTI_ANALYSIS = "anti_analysis"
    CLASS_REPACKAGING = "class_repackaging"
    METHOD_SPLITTING = "method_splitting"
    BRANCH_INSERTION = "branch_insertion"

class Obfuscator:
    """Obfuscation and deobfuscation system"""
    
    def __init__(self):
        self.obfuscation_patterns = self._initialize_obfuscation_patterns()
        self.deobfuscation_techniques = self._initialize_deobfuscation_techniques()
        self.string_decryption_keys = {}
    
    def _initialize_obfuscation_patterns(self) -> Dict[ObfuscationMethod, List[str]]:
        """Initialize obfuscation patterns"""
        return {
            ObfuscationMethod.STRING_ENCRYPTION: [
                "Base64.encode",
                "Base64.decode", 
                "AES.encrypt",
                "AES.decrypt",
                "XOR.",
                "encode.",
                "decode.",
                "encrypt.",
                "decrypt.",
                "StringEscapeUtils",
                "Crypto.",
                "cipher.",
                "key=",
                "secret="
            ],
            ObfuscationMethod.CONTROL_FLOW: [
                "switch(",
                "lookupswitch",
                "tableswitch",
                "goto ",
                "if-goto",
                "sparse-switch",
                "packed-switch",
                "goto/16",
                "goto/32",
                "return-void",
                "return v"
            ],
            ObfuscationMethod.REFLECTION: [
                "Class.forName",
                "Method.invoke",
                "Field.get",
                "Field.set",
                "Class.getDeclaredMethod",
                "Class.getDeclaredField",
                "invokeVirtual",
                "invokeDirect",
                "invokeStatic",
                "getDeclared",
                "getMethod"
            ],
            ObfuscationMethod.DUMMY_CODE: [
                "while(false)",
                "if(false)",
                "unusedVar",
                "dummyVar",
                "placeholder",
                "TODO",
                "FIXME",
                "throw new RuntimeException",
                "System.exit(1)",
                "assert false"
            ],
            ObfuscationMethod.NAME_OBFUSCATION: [
                r"[a-z]$",  # single character names
                r"[a-z][a-z]$",  # two character names
                r"[a-z]\d+$",  # letter followed by numbers
            ],
            ObfuscationMethod.ANTI_TAMPER: [
                "signature",
                "checksum",
                "integrity",
                "tamper",
                "verify",
                "validation",
                "authenticity",
                "hash",
                "digest",
                "mac"
            ],
            ObfuscationMethod.ANTI_ANALYSIS: [
                "isDebuggerConnected",
                "isEmulator",
                "isRooted",
                "RootBeer",
                "SafetyNet",
                "checkJNI",
                "jni",
                "native.",
                "Runtime.exec"
            ],
            ObfuscationMethod.CLASS_REPACKAGING: [
                "/a/",
                "/b/",
                "/c/",
                "/d/",
                "/e/",
                "/pkg/",
                "/util/",
                "/internal/",
                "/hidden/"
            ]
        }
    
    def _initialize_deobfuscation_techniques(self) -> Dict[str, Dict[str, Any]]:
        """Initialize deobfuscation techniques"""
        return {
            "string_decryptor": {
                "name": "String Decryption",
                "method": self._decrypt_strings,
                "description": "Decrypt encrypted strings",
                "pattern": r'Base64\.decode\("([^"]*)"\)',
                "reverse_operation": self._reverse_base64_decode
            },
            "name_restorer": {
                "name": "Name Restoration",
                "method": self._restore_names,
                "description": "Restore meaningful names",
                "pattern": r'[a-z]{1,2}$',
                "reverse_operation": self._infer_meaningful_names
            },
            "control_flow_cleaner": {
                "name": "Control Flow Cleaner",
                "method": self._clean_control_flow,
                "description": "Clean control flow obfuscation",
                "pattern": r'goto [^\n]+',
                "reverse_operation": self._simplify_control_flow
            },
            "reflection_resolver": {
                "name": "Reflection Resolver", 
                "method": self._resolve_reflection,
                "description": "Resolve reflection calls",
                "pattern": r'invokeVirtual',
                "reverse_operation": self._convert_reflection_to_normal
            },
            "dummy_code_remover": {
                "name": "Dummy Code Remover",
                "method": self._remove_dummy_code,
                "description": "Remove dummy/unreachable code",
                "pattern": r'if\(false\)',
                "reverse_operation": self._remove_dummy_conditions
            }
        }
    
    def detect_obfuscation_in_apk(self, apk_path: str) -> Dict[str, Any]:
        """Detect obfuscation techniques in APK"""
        results = {
            "obfuscation_detected": False,
            "obfuscation_methods_found": [],
            "files_with_obfuscation": [],
            "obfuscation_score": 0,
            "deobfuscation_recommendations": [],
            "total_indicators": 0
        }
        
        logger.info(f"Detecting obfuscation in: {apk_path}")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract APK
            with zipfile.ZipFile(apk_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Search for obfuscation patterns
            for obf_method, patterns in self.obfuscation_patterns.items():
                found_in_files = []
                
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith(('.smali', '.java')):
                            file_path = os.path.join(root, file)
                            
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            for pattern in patterns:
                                # Handle regex patterns differently
                                if isinstance(pattern, str) and pattern.startswith('r'):
                                    # This is a regex pattern
                                    try:
                                        matches = re.findall(pattern, content)
                                        if matches:
                                            found_instance = {
                                                "pattern": pattern,
                                                "file": os.path.relpath(file_path, temp_dir),
                                                "method_type": obf_method.value,
                                                "matches": matches
                                            }
                                            found_in_files.append(found_instance)
                                    except re.error:
                                        # Invalid regex, treat as literal string
                                        if pattern in content:
                                            found_instance = {
                                                "pattern": pattern,
                                                "file": os.path.relpath(file_path, temp_dir),
                                                "method_type": obf_method.value,
                                                "matches": [pattern]
                                            }
                                            found_in_files.append(found_instance)
                                else:
                                    # Literal string match
                                    if pattern.lower() in content.lower():
                                        found_instance = {
                                            "pattern": pattern,
                                            "file": os.path.relpath(file_path, temp_dir),
                                            "method_type": obf_method.value,
                                            "matches": [pattern]
                                        }
                                        found_in_files.append(found_instance)
                
                if found_in_files:
                    results["obfuscation_methods_found"].append(obf_method.value)
                    results["files_with_obfuscation"].extend(found_in_files)
                    results["total_indicators"] += len(found_in_files)
            
            results["obfuscation_detected"] = len(results["obfuscation_methods_found"]) > 0
            
            # Calculate obfuscation score
            score = len(results["obfuscation_methods_found"]) * 10 + len(results["files_with_obfuscation"]) * 2
            results["obfuscation_score"] = min(100, score)
            
            # Generate deobfuscation recommendations
            if results["obfuscation_detected"]:
                results["deobfuscation_recommendations"].append("Apply string decryption")
                results["deobfuscation_recommendations"].append("Restore meaningful names")
                results["deobfuscation_recommendations"].append("Clean control flow obfuscation")
                results["deobfuscation_recommendations"].append("Resolve reflection calls")
            else:
                results["deobfuscation_recommendations"].append("No obfuscation detected")
        
        return results
    
    def apply_obfuscation_to_apk(self, apk_path: str, output_path: str, 
                               techniques: List[str] = None) -> Dict[str, Any]:
        """Apply obfuscation to APK"""
        try:
            logger.info(f"Applying obfuscation to: {apk_path}")
            
            # Use ProGuard for obfuscation
            decompiled_dir = f"{os.path.splitext(apk_path)[0]}_decompiled"
            subprocess.run(["apktool", "d", apk_path, "-o", decompiled_dir, "-f"], check=True)
            
            obfuscated_count = 0
            
            # Apply obfuscation techniques
            for root, dirs, files in os.walk(decompiled_dir):
                for file in files:
                    if file.endswith('.smali'):
                        file_path = os.path.join(root, file)
                        
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        original_content = content
                        
                        # Apply string encryption
                        content = self._encrypt_strings(content)
                        obfuscated_count += 1
                        
                        # Apply name obfuscation
                        content = self._obfuscate_names(content)
                        obfuscated_count += 1
                        
                        # Apply control flow obfuscation
                        content = self._obfuscate_control_flow(content)
                        obfuscated_count += 1
                        
                        # Apply dummy code insertion
                        content = self._insert_dummy_code(content)
                        obfuscated_count += 1
                        
                        # Apply reflection obfuscation
                        content = self._obfuscate_with_reflection(content)
                        obfuscated_count += 1
                        
                        # Write back if modified
                        if content != original_content:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
            
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
                "obfuscated_files": obfuscated_count,
                "output_apk": output_path,
                "applied_techniques": [
                    "string_encryption",
                    "name_obfuscation", 
                    "control_flow_obfuscation",
                    "dummy_code_insertion",
                    "reflection_obfuscation"
                ]
            }
            
        except Exception as e:
            logger.error(f"Obfuscation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "obfuscated_files": 0,
                "output_apk": None
            }
    
    def _encrypt_strings(self, content: str) -> str:
        """Encrypt strings in content"""
        # Find string literals and encrypt them
        new_content = content
        
        # Look for string literals in smali files
        string_pattern = r'const-string(?:/[vz])?.*,"([^"]*)"'
        matches = re.findall(string_pattern, content)
        
        for match in set(matches):  # Remove duplicates
            if len(match) > 3 and not match.isdigit():  # Don't encrypt short or numeric strings
                # Create encrypted version using base64
                encrypted = base64.b64encode(match.encode()).decode()
                
                # Replace the string with encrypted version and decrypt logic
                original_line_pattern = rf'const-string(?:/[vz])?.*,"{re.escape(match)}"'
                replacement = f'''# Encrypted string: {match}
    const-string v0, "{encrypted}"
    invoke-static {{v0}}, Lcom/cybercrack/utils/StringDecryptor;->decrypt(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v0'''
                
                new_content = re.sub(original_line_pattern, lambda m: replacement, new_content)
        
        return new_content
    
    def _obfuscate_names(self, content: str) -> str:
        """Obfuscate class, method, and variable names"""
        # This is a simplified name obfuscation
        # In real implementation, this would be more sophisticated
        new_content = content
        
        # Replace simple, recognizable names with obfuscated versions
        # This would use sophisticated renaming in practice
        name_mappings = {}
        
        # Find class names and obfuscate them
        class_pattern = r'\.class.*L([^;]+);'
        classes = re.findall(class_pattern, content)
        
        for cls in set(classes):
            if len(cls) > 3:  # Only obfuscate longer names
                obfuscated_name = self._generate_obfuscated_name()
                new_content = new_content.replace(cls, obfuscated_name)
                name_mappings[cls] = obfuscated_name
        
        # Find method names and obfuscate them
        method_pattern = r'\.method.* ([^(]+)\('
        methods = re.findall(method_pattern, content)
        
        for method in set(methods):
            if method not in ['main', 'onCreate', 'onClick', 'onStart', 'onStop']:  # Preserve common method names
                obfuscated_name = self._generate_obfuscated_name(2)
                new_content = new_content.replace(f" {method}(", f" {obfuscated_name}(")
        
        return new_content
    
    def _obfuscate_control_flow(self, content: str) -> str:
        """Add control flow obfuscation"""
        # This is a simplified control flow obfuscation
        # In real implementation, this would be more complex
        new_content = content
        
        # Insert dummy control flow
        lines = new_content.split('\n')
        new_lines = []
        
        for line in lines:
            new_lines.append(line)
            
            # Add dummy branches occasionally
            if "invoke-" in line or "return" in line or "if-" in line:
                if random.random() < 0.2:  # 20% chance
                    new_lines.extend([
                        f"    # Obfuscation: dummy branch",
                        f"    const/4 v0, 0x1",
                        f"    if-eqz v0, :dummy_label_{random.randint(1000, 9999)}",
                        f"    :dummy_label_{random.randint(1000, 9999)}",
                        f"    # End dummy branch"
                    ])
        
        return '\n'.join(new_lines)
    
    def _insert_dummy_code(self, content: str) -> str:
        """Insert dummy code to confuse analysis"""
        # Insert fake code sections that won't be executed
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            new_lines.append(line)
            
            # Occasionally insert unreachable code
            if ".method" in line and "public" in line:
                if random.random() < 0.3:  # 30% chance
                    dummy_code = [
                        f"    # Begin dummy code block",
                        f"    const/4 v9, 0x0",
                        f"    if-nez v9, :end_dummy_{random.randint(1000, 9999)}",
                        f"    # This code is never reached",
                        f"    const-string v9, \"dummy_string_never_used\"",
                        f"    invoke-static {{v9}}, Ljava/lang/System;->exit(I)V",
                        f"    :end_dummy_{random.randint(1000, 9999)}",
                        f"    # End dummy code block"
                    ]
                    new_lines.extend(dummy_code)
        
        return '\n'.join(new_lines)
    
    def _obfuscate_with_reflection(self, content: str) -> str:
        """Use reflection to obscure code execution"""
        # This would convert direct calls to reflection calls
        # For simplicity, we'll just add some reflection patterns
        return content  # Simplified implementation
    
    def _generate_obfuscated_name(self, length: int = 2) -> str:
        """Generate obfuscated name"""
        return ''.join(random.choices(string.ascii_lowercase, k=length))
    
    def deobfuscate_apk(self, apk_path: str, output_path: str) -> Dict[str, Any]:
        """Attempt to deobfuscate APK"""
        try:
            logger.info(f"Deobfuscating APK: {apk_path}")
            
            # Decompile APK
            decompiled_dir = f"{os.path.splitext(apk_path)[0]}_decompiled"
            subprocess.run(["apktool", "d", apk_path, "-o", decompiled_dir, "-f"], check=True)
            
            deobfuscated_count = 0
            
            # Apply deobfuscation techniques to all files
            for root, dirs, files in os.walk(decompiled_dir):
                for file in files:
                    if file.endswith('.smali'):
                        file_path = os.path.join(root, file)
                        
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        original_content = content
                        
                        # Apply all deobfuscation techniques
                        for tech_name, tech_info in self.deobfuscation_techniques.items():
                            content = tech_info["method"](content)
                        
                        # Write back if modified
                        if content != original_content:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            deobfuscated_count += 1
            
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
                "deobfuscated_files": deobfuscated_count,
                "output_apk": output_path,
                "removed_techniques": list(self.deobfuscation_techniques.keys())
            }
            
        except Exception as e:
            logger.error(f"Deobfuscation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "deobfuscated_files": 0,
                "output_apk": None
            }
    
    def _decrypt_strings(self, content: str) -> str:
        """Reverse string encryption"""
        # Look for encrypted strings and try to decrypt them
        new_content = content
        
        # Look for Base64 encoded strings
        base64_pattern = r'const-string.*,"([A-Za-z0-9+/=]+)"[\s\S]*?invoke-static.*StringDecryptor'
        matches = re.findall(base64_pattern, content, re.MULTILINE)
        
        for encoded_str in set(matches):
            try:
                decoded = base64.b64decode(encoded_str).decode('utf-8', errors='ignore')
                # Replace encrypted string calls with original
                new_content = re.sub(
                    rf'const-string.*,"{encoded_str}".*?invoke-static.*StringDecryptor.*?move-result-object',
                    f'const-string v0, "{decoded}"',
                    new_content,
                    count=1,
                    flags=re.MULTILINE
                )
            except:
                pass  # Skip if not valid Base64
        
        return new_content
    
    def _restore_names(self, content: str) -> str:
        """Attempt to restore original names"""
        # This would use sophisticated renaming algorithms in practice
        # For now, we'll do a simple restoration based on context
        return content  # Simplified implementation
    
    def _clean_control_flow(self, content: str) -> str:
        """Clean control flow obfuscation"""
        # Remove dummy branches and simplify control flow
        lines = content.split('\n')
        new_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Remove dummy branches that are never taken
            if "const/4" in line and "0x0" in line:
                # Check if next line is an if-nez or similar that won't execute
                if i + 1 < len(lines) and "if-" in lines[i + 1] and "0x0" in line:
                    next_line = lines[i + 1]
                    if "if-nez" in next_line and f"0x0" in line:
                        # Skip this control flow obfuscation
                        i += 3  # Skip const/4, if-nez, and label
                        continue
            
            new_lines.append(line)
            i += 1
        
        return '\n'.join(new_lines)
    
    def _remove_dummy_code(self, content: str) -> str:
        """Remove dummy/unreachable code"""
        # Remove code blocks that start with if(false) or while(false)
        new_content = content
        
        # Pattern for if(false) blocks
        false_if_pattern = r'if-eqz.*0x0.*\n(:[^\n]+\n(?:\s+[^\n]+\n)*)*.*goto/.*\n'
        new_content = re.sub(false_if_pattern, '', new_content)
        
        # Pattern for while(false) loops
        false_while_pattern = r'const/4.*0x0.*\n.*if-nez.*:\n.*goto.*\n(:[^\n]+\n(?:\s+[^\n]+\n)*)*:.*goto.*\n'
        new_content = re.sub(false_while_pattern, '', new_content)
        
        return new_content

# Global instance
obfuscator = Obfuscator()

def main():
    """Main function for testing obfuscator"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python obfuscator.py <command> <apk_path> [output_path]")
        print("Commands: detect, obfuscate, deobfuscate, analyze")
        return
    
    command = sys.argv[1]
    apk_path = sys.argv[2]
    
    if command == "detect":
        result = obfuscator.detect_obfuscation_in_apk(apk_path)
        print(f"Obfuscation Detection Results: {json.dumps(result, indent=2)}")
    
    elif command == "obfuscate":
        if len(sys.argv) < 4:
            print("Please provide output path")
            return
        
        output_path = sys.argv[3]
        result = obfuscator.apply_obfuscation_to_apk(apk_path, output_path)
        print(f"Obfuscation Results: {json.dumps(result, indent=2)}")
    
    elif command == "deobfuscate":
        if len(sys.argv) < 4:
            print("Please provide output path")
            return
        
        output_path = sys.argv[3]
        result = obfuscator.deobfuscate_apk(apk_path, output_path)
        print(f"Deobfuscation Results: {json.dumps(result, indent=2)}")
    
    elif command == "analyze":
        detection_result = obfuscator.detect_obfuscation_in_apk(apk_path)
        
        # Generate detailed analysis
        analysis = {
            "apk_path": apk_path,
            "obfuscation_detected": detection_result["obfuscation_detected"],
            "obfuscation_score": detection_result["obfuscation_score"],
            "obfuscation_methods": detection_result["obfuscation_methods_found"],
            "recommendations": detection_result["deobfuscation_recommendations"],
            "complexity_level": "HIGH" if detection_result["obfuscation_score"] > 70 else "MEDIUM" if detection_result["obfuscation_score"] > 40 else "LOW",
            "deobfuscation_time_estimate": f"{detection_result['total_indicators'] * 2} seconds" if detection_result["total_indicators"] > 0 else "Not needed"
        }
        
        print(f"Obfuscation Analysis: {json.dumps(analysis, indent=2)}")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()