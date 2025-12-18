"""
🛠️ Utilities for Cyber Crack Pro Security Modules
Shared utilities and helper functions for security-related operations
"""

import asyncio
import logging
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import hashlib
import base64
import json
import zipfile
import shutil
import stat
from datetime import datetime

logger = logging.getLogger(__name__)

class SecurityUtils:
    """Utility functions for security operations"""
    
    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read the file in chunks to handle large files efficiently
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def create_backup(original_path: str) -> str:
        """Create a backup of the original file"""
        backup_path = f"{original_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            shutil.copy2(original_path, backup_path)
            logger.info(f"Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise
    
    @staticmethod
    async def extract_apk(apk_path: str) -> str:
        """Extract APK using apktool"""
        temp_dir = tempfile.mkdtemp(prefix="apk_extract_")
        
        try:
            # Use apktool to extract the APK
            cmd = ["apktool", "d", apk_path, "-o", temp_dir, "--force"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 min timeout
            
            if result.returncode != 0:
                raise Exception(f"Apktool extraction failed: {result.stderr}")
            
            logger.info(f"APK extracted to: {temp_dir}")
            return temp_dir
            
        except subprocess.TimeoutExpired:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise Exception("APK extraction timed out")
        except FileNotFoundError:
            # apktool not found, try using zip extraction
            logger.warning("Apktool not found, using basic extraction")
            return await SecurityUtils.basic_extract_apk(apk_path)
    
    @staticmethod
    async def basic_extract_apk(apk_path: str) -> str:
        """Basic APK extraction using zip"""
        temp_dir = tempfile.mkdtemp(prefix="basic_apk_extract_")
        
        try:
            with zipfile.ZipFile(apk_path, 'r') as apk:
                apk.extractall(temp_dir)
            
            logger.info(f"APK extracted with basic method to: {temp_dir}")
            return temp_dir
            
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise Exception(f"Basic APK extraction failed: {e}")
    
    @staticmethod
    async def rebuild_apk(extracted_dir: str, output_path: str) -> bool:
        """Rebuild APK from extracted directory"""
        try:
            cmd = ["apktool", "b", extracted_dir, "-o", output_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # 10 min timeout
            
            if result.returncode != 0:
                logger.error(f"Rebuild failed: {result.stderr}")
                return False
            
            logger.info(f"APK rebuilt to: {output_path}")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("APK rebuild timed out")
            return False
    
    @staticmethod
    async def sign_apk(apk_path: str) -> bool:
        """Sign APK using debug keystore or system keystore"""
        try:
            # Create debug keystore if it doesn't exist
            keystore_path = "debug.keystore"
            
            if not Path(keystore_path).exists():
                # Create debug keystore
                keytool_cmd = [
                    "keytool", "-genkey", "-v", "-keystore", keystore_path,
                    "-alias", "androiddebugkey", "-storepass", "android",
                    "-keypass", "android", "-keyalg", "RSA", "-keysize", "2048",
                    "-validity", "10000", "-dname", "CN=Android Debug,O=Android,C=US"
                ]
                
                result = subprocess.run(keytool_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"Failed to create debug keystore: {result.stderr}")
                    return False
            
            # Sign the APK
            sign_cmd = [
                "apksigner", "sign", "--ks", keystore_path,
                "--out", apk_path, apk_path
            ]
            
            result = subprocess.run(sign_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"APK signing failed: {result.stderr}")
                return False
            
            logger.info(f"APK signed: {apk_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error signing APK: {e}")
            return False
    
    @staticmethod
    async def align_apk(apk_path: str) -> bool:
        """Align APK using zipalign"""
        try:
            aligned_apk = f"{apk_path}.aligned"
            
            # Align the APK
            cmd = ["zipalign", "-v", "4", apk_path, aligned_apk]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"APK alignment failed: {result.stderr}")
                return False
            
            # Replace original with aligned version
            os.replace(aligned_apk, apk_path)
            
            logger.info(f"APK aligned: {apk_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error aligning APK: {e}")
            return False
    
    @staticmethod
    def find_files_by_extension(directory: str, extension: str) -> List[str]:
        """Find all files with a specific extension in directory"""
        extension = extension.lower()
        files = []
        
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                if filename.lower().endswith(extension):
                    files.append(os.path.join(root, filename))
        
        return files
    
    @staticmethod
    def find_files_by_pattern(directory: str, pattern: str) -> List[str]:
        """Find all files matching a pattern"""
        regex = re.compile(pattern, re.IGNORECASE)
        files = []
        
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                if regex.search(filename):
                    files.append(os.path.join(root, filename))
        
        return files
    
    @staticmethod
    def read_file_content(file_path: str) -> Optional[str]:
        """Safely read file content with multiple encoding attempts"""
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        logger.warning(f"Could not read file with any of the attempted encodings: {file_path}")
        return None
    
    @staticmethod
    def write_file_content(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """Safely write file content"""
        try:
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Error writing to file: {e}")
            return False
    
    @staticmethod
    def file_contains_pattern(file_path: str, pattern: Union[str, re.Pattern]) -> bool:
        """Check if file contains a pattern"""
        content = SecurityUtils.read_file_content(file_path)
        if not content:
            return False
        
        if isinstance(pattern, str):
            # Simple string search
            return pattern.lower() in content.lower()
        else:
            # Regex pattern
            return bool(pattern.search(content))
    
    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """Get file size in MB"""
        try:
            size_bytes = os.path.getsize(file_path)
            return size_bytes / (1024 * 1024)
        except:
            return 0.0
    
    @staticmethod
    async def execute_shell_command(cmd: List[str], timeout: int = 30) -> Tuple[bool, str, str]:
        """Execute shell command safely"""
        try:
            # Ensure command is a list
            if isinstance(cmd, str):
                cmd = cmd.split()
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                success = process.returncode == 0
                out_str = stdout.decode('utf-8') if stdout else ""
                err_str = stderr.decode('utf-8') if stderr else ""
                
                return success, out_str, err_str
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return False, "", "Command timed out"
                
        except Exception as e:
            return False, "", str(e)
    
    @staticmethod
    def is_valid_apk(apk_path: str) -> bool:
        """Check if file is a valid APK"""
        if not Path(apk_path).exists():
            return False
        
        # Check if it's a ZIP file (APKs are ZIP files)
        try:
            with zipfile.ZipFile(apk_path, 'r') as apk_file:
                # Check for essential APK files
                name_list = apk_file.namelist()
                has_manifest = 'AndroidManifest.xml' in name_list
                has_dex = any(name.endswith('.dex') for name in name_list)
                
                return has_manifest and has_dex
        except:
            return False
    
    @staticmethod
    def validate_path(path: str, base_dir: str = None) -> bool:
        """Validate path to prevent directory traversal"""
        try:
            path_abs = Path(path).resolve()
            
            if base_dir:
                base_abs = Path(base_dir).resolve()
                return str(path_abs).startswith(str(base_abs))
            else:
                # Prevent common traversal patterns
                path_str = str(Path(path))
                return '../' not in path_str and '..\\' not in path_str
        except:
            return False
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        # Remove potentially harmful characters
        sanitized = re.sub(r'[^\w\-_\. ]', '_', filename)
        
        # Prevent directory traversal
        parts = sanitized.split('/')
        parts = [part for part in parts if part != '..' and part != '.']
        sanitized = '/'.join(parts)
        
        # Limit length
        if len(sanitized) > 255:
            sanitized = sanitized[:250] + sanitized[-5:]
        
        return sanitized
    
    @staticmethod
    async def get_apk_info(apk_path: str) -> Dict[str, Any]:
        """Get APK information using aapt"""
        try:
            cmd = ["aapt", "dump", "badging", apk_path]
            _, stdout, stderr = await SecurityUtils.execute_shell_command(cmd)
            
            if stderr:
                raise Exception(f"aapt failed: {stderr}")
            
            info = {}
            
            # Parse aapt output
            for line in stdout.split('\n'):
                if line.startswith("package:"):
                    # Extract package name and version
                    matches = re.search(r"name='([^']+)'", line)
                    if matches:
                        info['package_name'] = matches.group(1)
                    
                    version_matches = re.search(r"versionName='([^']+)'", line)
                    if version_matches:
                        info['version_name'] = version_matches.group(1)
                        
                    code_matches = re.search(r"versionCode='([^']+)'", line)
                    if code_matches:
                        info['version_code'] = code_matches.group(1)
                
                elif line.startswith("application-label:"):
                    label_match = re.search(r"'([^']+)'", line)
                    if label_match:
                        info['app_label'] = label_match.group(1)
                
                elif line.startswith("uses-permission:"):
                    # Extract permissions
                    if 'permissions' not in info:
                        info['permissions'] = []
                    perm_match = re.search(r"name='([^']+)'", line)
                    if perm_match:
                        info['permissions'].append(perm_match.group(1))
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting APK info: {e}")
            return {"error": str(e)}
    
    @staticmethod
    async def check_file_integrity(file_path: str, expected_hash: str) -> bool:
        """Check if file integrity matches the expected hash"""
        actual_hash = SecurityUtils.calculate_file_hash(file_path)
        return actual_hash == expected_hash
    
    @staticmethod
    def cleanup_temp_files(temp_dir: str):
        """Clean up temporary files"""
        try:
            if Path(temp_dir).exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            logger.error(f"Error cleaning up temporary directory: {e}")
    
    @staticmethod
    async def execute_multiple_commands(commands: List[List[str]], 
                                      max_concurrent: int = 5) -> List[Tuple[bool, str, str]]:
        """Execute multiple commands concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def run_command(cmd):
            async with semaphore:
                return await SecurityUtils.execute_shell_command(cmd)
        
        tasks = [run_command(cmd) for cmd in commands]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle potential exceptions
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append((False, "", str(result)))
            else:
                processed_results.append(result)
        
        return processed_results
    
    @staticmethod
    def format_size(bytes_size: int) -> str:
        """Format size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"
    
    @staticmethod
    def extract_strings_from_binary(file_path: str) -> List[str]:
        """Extract strings from binary file"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Use regex to find printable strings (4+ characters)
            strings = re.findall(rb'[ -~]{4,}', content)
            return [s.decode('utf-8', errors='ignore') for s in strings]
            
        except Exception as e:
            logger.error(f"Error extracting strings from binary: {e}")
            return []
    
    @staticmethod
    async def validate_smali_syntax(smali_content: str) -> bool:
        """Basic validation of Smali syntax"""
        # This is a simplified check
        # In a real implementation, you'd use proper Smali validation
        
        required_components = [
            '.class', '.super', '.method', '.end method', 
            '.field', '.end field', '.prologue'
        ]
        
        for component in required_components:
            if component in smali_content:
                return True  # Found at least one valid Smali component
        
        return len(smali_content) > 100  # If content is substantial, likely valid
    
    @staticmethod
    def create_directory_tree(directory: str):
        """Create directory tree if it doesn't exist"""
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def remove_sensitive_strings(content: str) -> str:
        """Remove or obfuscate sensitive strings from content"""
        # Patterns to identify sensitive information
        patterns = [
            # API keys
            (r'([A-Za-z0-9]{32,})', '***REMOVED***'),  # Long hex strings
            (r'(api_key|secret|token|password|key)=([A-Za-z0-9_-]{20,})', '\\1=***REMOVED***'),  # Key-value pairs with long values
            (r'("https?://[^"]*password=[^"]*")', '"http://example.com/login?password=***REMOVED***"'),  # Password in URLs
        ]
        
        modified_content = content
        for pattern, replacement in patterns:
            modified_content = re.sub(pattern, replacement, modified_content, flags=re.IGNORECASE)
        
        return modified_content

class PerformanceMonitor:
    """Monitor performance of security operations"""
    
    def __init__(self):
        self.start_times = {}
        self.results = {}
    
    def start_timer(self, operation: str):
        """Start timer for an operation"""
        self.start_times[operation] = datetime.now()
    
    def end_timer(self, operation: str) -> float:
        """End timer and return elapsed time in seconds"""
        if operation in self.start_times:
            elapsed = (datetime.now() - self.start_times[operation]).total_seconds()
            self.results[operation] = elapsed
            del self.start_times[operation]
            return elapsed
        return 0.0
    
    def get_average_time(self, operation: str) -> float:
        """Get average time for an operation type"""
        # In a real implementation, this would track multiple executions
        if operation in self.results:
            return self.results[operation]
        return 0.0
    
    def get_timings_summary(self) -> Dict[str, float]:
        """Get summary of all timings"""
        return self.results.copy()

# Create singleton instance
security_utils = SecurityUtils()
performance_monitor = PerformanceMonitor()