#!/usr/bin/env python3
"""
🤖 Python Bridge API Client
Handles communication between Python bridge and other services
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import httpx
import aiofiles
from datetime import datetime

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Custom exception for API-related errors"""
    pass

class PythonBridgeClient:
    """Client for communicating with other Cyber Crack Pro services"""
    
    def __init__(self, orchestrator_url: str = "http://localhost:5000"):
        self.orchestrator_url = orchestrator_url
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=5.0),
            headers={"User-Agent": "Cyber-Crack-Pro-Python-Bridge/3.0"}
        )
    
    async def analyze_apk_remote(self, apk_path: str, category: str = "auto") -> Dict[str, Any]:
        """Analyze APK using remote orchestrator"""
        try:
            response = await self.http_client.post(
                f"{self.orchestrator_url}/analyze",
                json={
                    "apk_path": apk_path,
                    "category": category,
                    "engine": "python_bridge"
                }
            )
            
            if response.status_code != 200:
                raise APIError(f"Remote analysis failed with status {response.status_code}: {response.text}")
            
            return response.json()
        
        except httpx.RequestError as e:
            logger.error(f"Request error during remote analysis: {e}")
            raise APIError(f"Request failed: {e}")
    
    async def crack_apk_remote(self, apk_path: str, category: str, features: List[str]) -> Dict[str, Any]:
        """Perform cracking using remote orchestrator"""
        try:
            response = await self.http_client.post(
                f"{self.orchestrator_url}/crack",
                json={
                    "apk_path": apk_path,
                    "category": category,
                    "features": features,
                    "engine": "python_bridge"
                }
            )
            
            if response.status_code != 200:
                raise APIError(f"Remote cracking failed with status {response.status_code}: {response.text}")
            
            return response.json()
        
        except httpx.RequestError as e:
            logger.error(f"Request error during remote cracking: {e}")
            raise APIError(f"Request failed: {e}")
    
    async def get_engine_status(self, engine_name: str) -> Dict[str, Any]:
        """Get status of a specific engine"""
        try:
            response = await self.http_client.get(
                f"{self.orchestrator_url}/engine/{engine_name}/status"
            )
            
            if response.status_code != 200:
                raise APIError(f"Failed to get engine status: {response.status_code}")
            
            return response.json()
        
        except httpx.RequestError as e:
            logger.error(f"Request error getting engine status: {e}")
            raise APIError(f"Request failed: {e}")
    
    async def get_all_engine_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all engines"""
        try:
            response = await self.http_client.get(
                f"{self.orchestrator_url}/engine/statuses"
            )
            
            if response.status_code != 200:
                raise APIError(f"Failed to get engine statuses: {response.status_code}")
            
            return response.json()
        
        except httpx.RequestError as e:
            logger.error(f"Request error getting all engine statuses: {e}")
            raise APIError(f"Request failed: {e}")
    
    async def submit_job(self, job_data: Dict[str, Any]) -> str:
        """Submit a job to the orchestrator"""
        try:
            response = await self.http_client.post(
                f"{self.orchestrator_url}/jobs/submit",
                json=job_data
            )
            
            if response.status_code != 200:
                raise APIError(f"Failed to submit job: {response.status_code} - {response.text}")
            
            result = response.json()
            return result.get("job_id", "")
        
        except httpx.RequestError as e:
            logger.error(f"Request error submitting job: {e}")
            raise APIError(f"Request failed: {e}")
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a submitted job"""
        try:
            response = await self.http_client.get(
                f"{self.orchestrator_url}/jobs/{job_id}/status"
            )
            
            if response.status_code != 200:
                raise APIError(f"Failed to get job status: {response.status_code}")
            
            return response.json()
        
        except httpx.RequestError as e:
            logger.error(f"Request error getting job status: {e}")
            raise APIError(f"Request failed: {e}")
    
    async def get_job_result(self, job_id: str) -> Dict[str, Any]:
        """Get result of a completed job"""
        try:
            response = await self.http_client.get(
                f"{self.orchestrator_url}/jobs/{job_id}/result"
            )
            
            if response.status_code != 200:
                raise APIError(f"Failed to get job result: {response.status_code}")
            
            return response.json()
        
        except httpx.RequestError as e:
            logger.error(f"Request error getting job result: {e}")
            raise APIError(f"Request failed: {e}")
    
    async def send_results_to_gateway(self, results: Dict[str, Any]) -> bool:
        """Send analysis results to API gateway"""
        try:
            response = await self.http_client.post(
                f"{self.orchestrator_url}/gateway/results",
                json=results
            )
            
            return response.status_code == 200
        
        except httpx.RequestError as e:
            logger.error(f"Request error sending results to gateway: {e}")
            return False
    
    async def upload_apk_to_gateway(self, apk_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Upload APK to gateway with metadata"""
        try:
            # Read APK file
            async with aiofiles.open(apk_path, 'rb') as apk_file:
                apk_content = await apk_file.read()
            
            # Create multipart form data
            files = {
                'file': (Path(apk_path).name, apk_content, 'application/vnd.android.package-archive')
            }
            
            data = {
                'metadata': json.dumps(metadata)
            }
            
            response = await self.http_client.post(
                f"{self.orchestrator_url}/gateway/upload",
                files=files,
                data=data
            )
            
            if response.status_code != 200:
                raise APIError(f"Failed to upload APK: {response.status_code} - {response.text}")
            
            return response.json()
        
        except httpx.RequestError as e:
            logger.error(f"Request error uploading APK: {e}")
            raise APIError(f"Upload failed: {e}")
    
    async def download_modified_apk(self, job_id: str, output_path: str) -> bool:
        """Download modified APK from orchestrator"""
        try:
            response = await self.http_client.get(
                f"{self.orchestrator_url}/jobs/{job_id}/download"
            )
            
            if response.status_code != 200:
                raise APIError(f"Failed to download APK: {response.status_code}")
            
            async with aiofiles.open(output_path, 'wb') as output_file:
                await output_file.write(response.content)
            
            return True
        
        except httpx.RequestError as e:
            logger.error(f"Request error downloading APK: {e}")
            return False
    
    async def get_pattern_library(self, category: str = None) -> List[Dict[str, Any]]:
        """Get pattern library from orchestrator"""
        try:
            url = f"{self.orchestrator_url}/patterns"
            if category:
                url += f"?category={category}"
            
            response = await self.http_client.get(url)
            
            if response.status_code != 200:
                raise APIError(f"Failed to get patterns: {response.status_code}")
            
            return response.json()
        
        except httpx.RequestError as e:
            logger.error(f"Request error getting patterns: {e}")
            raise APIError(f"Request failed: {e}")
    
    async def send_pattern_update(self, pattern_id: str, update_data: Dict[str, Any]) -> bool:
        """Send pattern update to orchestrator"""
        try:
            response = await self.http_client.post(
                f"{self.orchestrator_url}/patterns/{pattern_id}/update",
                json=update_data
            )
            
            return response.status_code == 200
        
        except httpx.RequestError as e:
            logger.error(f"Request error updating pattern: {e}")
            return False
    
    async def get_knowledge_base(self) -> Dict[str, Any]:
        """Get knowledge base from orchestrator"""
        try:
            response = await self.http_client.get(
                f"{self.orchestrator_url}/knowledge"
            )
            
            if response.status_code != 200:
                raise APIError(f"Failed to get knowledge base: {response.status_code}")
            
            return response.json()
        
        except httpx.RequestError as e:
            logger.error(f"Request error getting knowledge base: {e}")
            raise APIError(f"Request failed: {e}")
    
    async def update_knowledge_base(self, update_data: Dict[str, Any]) -> bool:
        """Update knowledge base"""
        try:
            response = await self.http_client.post(
                f"{self.orchestrator_url}/knowledge/update",
                json=update_data
            )
            
            return response.status_code == 200
        
        except httpx.RequestError as e:
            logger.error(f"Request error updating knowledge base: {e}")
            return False
    
    async def send_statistics(self, stats: Dict[str, Any]) -> bool:
        """Send statistics to orchestrator"""
        try:
            response = await self.http_client.post(
                f"{self.orchestrator_url}/stats",
                json=stats
            )
            
            return response.status_code == 200
        
        except httpx.RequestError as e:
            logger.error(f"Request error sending statistics: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Perform health check on orchestrator"""
        try:
            response = await self.http_client.get(
                f"{self.orchestrator_url}/health"
            )
            
            return response.status_code == 200
        
        except:
            return False
    
    async def close(self):
        """Close the HTTP client"""
        await self.http_client.aclose()

class PatternMatchResult:
    """Result of a pattern matching operation"""
    
    def __init__(self, pattern_id: str, matched_text: str, file_path: str, 
                 line_number: int, confidence: float, severity: str, fix_suggestion: str):
        self.pattern_id = pattern_id
        self.matched_text = matched_text
        self.file_path = file_path
        self.line_number = line_number
        self.confidence = confidence
        self.severity = severity
        self.fix_suggestion = fix_suggestion
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "pattern_id": self.pattern_id,
            "matched_text": self.matched_text,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "confidence": self.confidence,
            "severity": self.severity,
            "fix_suggestion": self.fix_suggestion,
            "timestamp": self.timestamp
        }

class CrackResult:
    """Result of a cracking operation"""
    
    def __init__(self, success: bool, modified_apk_path: str = None, 
                 fixes_applied: List[str] = None, vulnerabilities_found: int = 0,
                 protections_identified: int = 0, stability_score: int = 0,
                 processing_time_ms: int = 0, error: str = None):
        self.success = success
        self.modified_apk_path = modified_apk_path or ""
        self.fixes_applied = fixes_applied or []
        self.vulnerabilities_found = vulnerabilities_found
        self.protections_identified = protections_identified
        self.stability_score = stability_score
        self.processing_time_ms = processing_time_ms
        self.error = error
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "success": self.success,
            "modified_apk_path": self.modified_apk_path,
            "fixes_applied": self.fixes_applied,
            "vulnerabilities_found": self.vulnerabilities_found,
            "protections_identified": self.protections_identified,
            "stability_score": self.stability_score,
            "processing_time_ms": self.processing_time_ms,
            "error": self.error,
            "timestamp": self.timestamp
        }

class AnalysisResult:
    """Result of an analysis operation"""
    
    def __init__(self, apk_path: str, vulnerabilities: List[Dict[str, Any]], 
                 protections: List[Dict[str, Any]], security_score: int = 0,
                 complexity_level: str = "MEDIUM", recommendations: List[str] = None):
        self.apk_path = apk_path
        self.vulnerabilities = vulnerabilities
        self.protections = protections
        self.security_score = security_score
        self.complexity_level = complexity_level
        self.recommendations = recommendations or []
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "apk_path": self.apk_path,
            "vulnerabilities": self.vulnerabilities,
            "protections": self.protections,
            "security_score": self.security_score,
            "complexity_level": self.complexity_level,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp
        }

# Example usage
async def main():
    client = PythonBridgeClient()
    
    try:
        # Example: Submit a job
        job_data = {
            "apk_path": "/path/to/app.apk",
            "category": "login_bypass",
            "features": ["auth_bypass", "credential_extraction"],
            "options": {
                "aggressive_mode": True,
                "preserve_functionality": True
            }
        }
        
        job_id = await client.submit_job(job_data)
        print(f"Submitted job with ID: {job_id}")
        
        # Check job status
        while True:
            status = await client.get_job_status(job_id)
            print(f"Job status: {status}")
            
            if status["status"] in ["completed", "failed", "cancelled"]:
                break
            
            await asyncio.sleep(2)  # Wait before checking again
        
        # Get job result
        if status["status"] == "completed":
            result = await client.get_job_result(job_id)
            print(f"Job result: {result}")
        
    except APIError as e:
        print(f"API Error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())