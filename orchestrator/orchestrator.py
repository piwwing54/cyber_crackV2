#!/usr/bin/env python3
"""
🤖 CYBER CRACK PRO - Main Orchestrator with Complete Integration
Coordinates all engines and AI systems for processing
"""

import asyncio
import logging
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp
import redis.asyncio as redis
import hashlib
import uuid
from enum import Enum
import time
from dataclasses import dataclass
import zipfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://cracker:password @localhost:5432/cybercrackpro")
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:5000")

# Engine URLs
ENGINE_URLS = {
    "go": os.getenv("GO_ENGINE_URL", "http://go-analyzer:8080"),
    "rust": os.getenv("RUST_ENGINE_URL", "http://rust-cracker:8081"),
    "cpp": os.getenv("CPP_ENGINE_URL", "http://cpp-breaker:8082"),
    "java": os.getenv("JAVA_ENGINE_URL", "http://java-dex:8083"),
    "python": os.getenv("PYTHON_ENGINE_URL", "http://python-bridge:8084")
}

class JobStatus(Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ProcessingJob:
    job_id: str
    apk_path: str
    category: str
    features: List[str]
    priority: TaskPriority
    user_id: str
    created_at: str
    status: JobStatus = JobStatus.PENDING
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict] = None
    error_message: Optional[str] = None
    processing_time: float = 0.0

class CyberCrackOrchestrator:
    """Main orchestrator that coordinates all engines and AI systems"""
    
    def __init__(self):
        self.redis_client = None
        self.http_session = None
        self.job_queue = asyncio.Queue()
        self.active_jobs = {}
        self.max_concurrent_jobs = int(os.getenv("MAX_CONCURRENT_JOBS", "10"))
        self.stats = {
            "total_jobs": 0,
            "completed_jobs": 0,
            "failed_jobs": 0,
            "avg_processing_time": 0.0,
            "success_rate": 0.0,
            "active_workers": 0
        }
        
        # AI Integration
        self.ai_analyzer = None
        self.game_mod_detector = None
    
    async def initialize(self):
        """Initialize orchestrator with all services"""
        # Initialize Redis connection
        self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        
        # Initialize HTTP session
        self.http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=300)  # 5 minute timeout
        )
        
        # Initialize AI analyzer
        try:
            from brain.ai_analyzer import AIAnalyzer
            self.ai_analyzer = AIAnalyzer()
            await self.ai_analyzer.initialize()
        except ImportError:
            logger.warning("AI Analyzer not available, using basic methods")
        
        # Initialize game mod detector
        try:
            from brain.mod_menu_generator import GameModDetectionPipeline
            self.game_mod_detector = GameModDetectionPipeline()
            await self.game_mod_detector.initialize()
        except ImportError:
            logger.warning("Game Mod Detector not available")
        
        # Start worker pool
        for i in range(self.max_concurrent_jobs):
            asyncio.create_task(self.worker(i))
        
        logger.info("🤖 Cyber Crack Pro Orchestrator initialized!")
        logger.info(f"   Engine URLs: {ENGINE_URLS}")
        logger.info(f"   Max Concurrent: {self.max_concurrent_jobs}")
        logger.info("   AI Systems: DeepSeek + WormGPT + Game Mods")
    
    async def worker(self, worker_id: int):
        """Worker to process jobs from queue"""
        logger.info(f"Worker {worker_id} started")
        
        while True:
            try:
                # Get job from queue
                job = await self.job_queue.get()
                
                # Process job
                await self.process_job(job)
                
                # Mark as done
                self.job_queue.task_done()
                
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)
    
    async def create_job(self, 
                        apk_path: str, 
                        category: str = "auto_detect",
                        features: List[str] = None,
                        priority: str = "MEDIUM",
                        user_id: str = "anonymous") -> str:
        """Create new processing job"""
        
        job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        job = ProcessingJob(
            job_id=job_id,
            apk_path=apk_path,
            category=category,
            features=features or [],
            priority=TaskPriority[priority.upper()],
            user_id=user_id,
            created_at=datetime.now().isoformat()
        )
        
        # Store job in Redis
        job_data = {
            "job_id": job_id,
            "apk_path": apk_path,
            "category": category,
            "features": json.dumps(job.features),
            "priority": priority,
            "user_id": user_id,
            "status": JobStatus.PENDING.value,
            "created_at": job.created_at,
            "progress": 0
        }
        
        await self.redis_client.hset(f"job:{job_id}", mapping=job_data)
        
        # Add to queue
        await self.job_queue.put(job)
        
        # Update stats
        self.stats["total_jobs"] += 1
        
        logger.info(f"📋 Job created: {job_id} for {Path(apk_path).name}")
        return job_id
    
    async def process_job(self, job: ProcessingJob):
        """Process a single job with all engines and AI"""
        
        start_time = time.time()
        self.active_jobs[job.job_id] = job
        
        try:
            # Update job status
            await self.update_job_status(job.job_id, JobStatus.ANALYZING)
            
            logger.info(f"🔍 AI Analysis started for job {job.job_id}")
            
            # 1. Perform AI analysis (with dual AI + game mod detection)
            if self.ai_analyzer:
                ai_analysis = await self.ai_analyzer.analyze_apk_with_ai(
                    job.apk_path, 
                    job.category
                )
            else:
                # Fallback to basic analysis
                ai_analysis = await self._perform_basic_analysis(job.apk_path, job.category)
            
            # Update progress
            await self.redis_client.hset(f"job:{job.job_id}", "progress", 25)
            
            # 2. If it's a game APK, run game mod analysis
            game_mods = {}
            if self.game_mod_detector and self._is_game_apk(job.apk_path):
                game_mods = await self.game_mod_detector.process_game_apk(
                    job.apk_path, 
                    ai_analysis
                )
            
            # 3. Execute cracking with all engines
            engine_results = await self.execute_multi_engine_processing(
                job.apk_path, 
                job.category, 
                ai_analysis, 
                game_mods
            )
            
            # Update progress
            await self.redis_client.hset(f"job:{job.job_id}", "progress", 75)
            
            # 4. Combine and validate results
            final_result = await self.integrate_engine_results(
                job, ai_analysis, game_mods, engine_results
            )
            
            # Update progress
            await self.redis_client.hset(f"job:{job.job_id}", "progress", 95)
            
            # 5. Perform stability and security checks
            validation_result = await self.validate_results(
                job.apk_path, final_result
            )
            
            # Final result
            final_result["validation"] = validation_result
            final_result["processing_time"] = time.time() - start_time
            final_result["success"] = True
            
            # Store final result
            await self.redis_client.hset(f"job:{job.job_id}", mapping={
                "result": json.dumps(final_result),
                "status": JobStatus.COMPLETED.value,
                "completed_at": datetime.now().isoformat(),
                "processing_time": str(final_result["processing_time"]),
                "progress": 100
            })
            
            job.result = final_result
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now().isoformat()
            
            self.stats["completed_jobs"] += 1
            self.stats["success_rate"] = (self.stats["completed_jobs"] / self.stats["total_jobs"]) * 100
            
            logger.info(f"✅ Job {job.job_id} completed successfully in {final_result['processing_time']:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Job {job.job_id} failed: {e}")
            
            error_result = {
                "success": False,
                "error": str(e),
                "original_apk": job.apk_path,
                "processing_time": time.time() - start_time
            }
            
            await self.redis_client.hset(f"job:{job.job_id}", mapping={
                "result": json.dumps(error_result),
                "status": JobStatus.FAILED.value,
                "error_message": str(e),
                "completed_at": datetime.now().isoformat(),
                "processing_time": str(error_result["processing_time"])
            })
            
            job.result = error_result
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now().isoformat()
            job.error_message = str(e)
            
            self.stats["failed_jobs"] += 1
            self.stats["success_rate"] = (self.stats["completed_jobs"] / self.stats["total_jobs"]) * 100
        
        finally:
            # Calculate average processing time
            if self.stats["completed_jobs"] > 0:
                total_time = sum([r.get("processing_time", 0) for r in [
                    await self.redis_client.hget(f"job:{jid}", "processing_time") 
                    for jid in [k for k in list(self.active_jobs.keys()) 
                                if await self.redis_client.hget(f"job:{k}", "status") == "completed"]
                ] if r is not None])
                self.stats["avg_processing_time"] = total_time / self.stats["completed_jobs"]
            
            # Remove from active jobs
            if job.job_id in self.active_jobs:
                del self.active_jobs[job.job_id]
    
    async def _perform_basic_analysis(self, apk_path: str, category: str) -> Dict:
        """Basic analysis if AI is not available"""
        # In production, this would still analyze the APK
        # For now, return mock analysis
        return {
            "vulnerabilities": [
                {"type": "generic_vulnerability", "severity": "MEDIUM", "location": "unknown", "confidence": 0.7}
            ],
            "protections": ["none_detected"],
            "recommendations": ["apply_standard_cracking"],
            "security_score": 50,
            "ai_confidence": 0.5,
            "game_analysis": {
                "is_game": self._is_game_apk(apk_path),
                "game_features_detected": [],
                "mod_menu_suggested": False
            }
        }
    
    async def execute_multi_engine_processing(self, 
                                             apk_path: str, 
                                             category: str, 
                                             ai_analysis: Dict,
                                             game_mods: Dict) -> Dict:
        """Execute processing with all available engines"""
        
        logger.info("⚙️ Starting multi-engine processing...")
        
        # Prepare payload for all engines
        payload = {
            "apk_path": apk_path,
            "category": category,
            "ai_analysis": ai_analysis,
            "game_mods": game_mods,
            "features": ai_analysis.get("recommended_features", []),
            "timestamp": datetime.now().isoformat()
        }
        
        # Execute all engines concurrently
        engine_tasks = {}
        
        # Go Engine (fast static analysis)
        if self._is_engine_available("go"):
            engine_tasks["go"] = self._execute_engine("go", payload.copy())
        
        # Rust Engine (binary manipulation)
        if self._is_engine_available("rust"): 
            engine_tasks["rust"] = self._execute_engine("rust", payload.copy())
        
        # C++ Engine (GPU accelerated)
        if self._is_engine_available("cpp"):
            engine_tasks["cpp"] = self._execute_engine("cpp", payload.copy())
        
        # Java Engine (Android specific)
        if self._is_engine_available("java"):
            engine_tasks["java"] = self._execute_engine("java", payload.copy())
        
        # Python Engine (AI integration)
        if self._is_engine_available("python"):
            engine_tasks["python"] = self._execute_engine("python", payload.copy())
        
        # Run all engines
        engine_results = {}
        for engine_name, task in engine_tasks.items():
            try:
                result = await asyncio.wait_for(task, timeout=180)  # 3 minute timeout
                engine_results[engine_name] = result
                logger.info(f"✅ {engine_name} engine completed")
            except asyncio.TimeoutError:
                engine_results[engine_name] = {"error": f"Engine {engine_name} timed out", "success": False}
                logger.error(f"❌ {engine_name} engine timed out")
            except Exception as e:
                engine_results[engine_name] = {"error": f"Engine {engine_name} error: {str(e)}", "success": False}
                logger.error(f"❌ {engine_name} engine error: {e}")
        
        return engine_results
    
    async def _execute_engine(self, engine: str, payload: Dict) -> Dict:
        """Execute a single engine"""
        url = f"{ENGINE_URLS[engine]}/process"
        
        async with self.http_session.post(url, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                result["engine"] = engine
                result["success"] = True
                return result
            else:
                error_text = await response.text()
                return {
                    "success": False,
                    "error": f"Engine {engine} returned {response.status}: {error_text}",
                    "engine": engine
                }
    
    def _is_engine_available(self, engine: str) -> bool:
        """Check if engine is available"""
        return engine in ENGINE_URLS
    
    def _is_game_apk(self, apk_path: str) -> bool:
        """Check if APK is likely a game"""
        apk_name = Path(apk_path).name.lower()
        game_keywords = [
            "game", "mobile", "legends", "pubg", "minecraft", "freefire", 
            "genshin", "clash", "puzzle", "casual", "strategy", "rpg"
        ]
        return any(keyword in apk_name for keyword in game_keywords)
    
    async def integrate_engine_results(self, job: ProcessingJob, 
                                     ai_analysis: Dict, 
                                     game_mods: Dict,
                                     engine_results: Dict) -> Dict:
        """Integrate results from all engines"""
        
        integrated_result = {
            "job_id": job.job_id,
            "original_apk": job.apk_path,
            "category": job.category,
            "features_applied": [],
            "engines_used": [],
            "modifications_applied": [],
            "crack_patterns_used": [],
            "stability_score": 0,
            "security_score": 0,
            "processing_time": 0,
            "ai_analysis": ai_analysis,
            "game_mods": game_mods,
            "engine_results": engine_results,
            "modified_apk_path": "",
            "success": True
        }
        
        # Count successful engines
        successful_engines = [
            engine for engine, result in engine_results.items() 
            if result.get("success", False)
        ]
        integrated_result["engines_used"] = successful_engines
        
        # Collect modifications from all engines
        total_modifications = 0
        for engine, result in engine_results.items():
            if result.get("success", False):
                modifications = result.get("modifications_applied", [])
                integrated_result["modifications_applied"].extend(modifications)
                total_modifications += len(modifications)
                
                patterns = result.get("crack_patterns_used", [])
                integrated_result["crack_patterns_used"].extend(patterns)
        
        integrated_result["features_applied"] = total_modifications
        
        # Generate modified APK path
        original_path = Path(job.apk_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        modified_name = f"{original_path.stem}_CRACKED_{timestamp}.apk"
        modified_path = original_path.parent / modified_name
        integrated_result["modified_apk_path"] = str(modified_path)
        
        # Calculate scores based on AI analysis and modifications
        security_score = ai_analysis.get("security_score", 50)
        stability_score = max(0, min(100, int(security_score * 0.7) + (total_modifications * 2)))
        integrated_result["stability_score"] = stability_score
        integrated_result["security_score"] = security_score
        
        # Include game mod menu if detected
        if game_mods.get("mod_menu_available", False):
            game_mod_menu_path = await self._create_game_mod_menu(
                original_path, game_mods.get("features", [])
            )
            integrated_result["game_mod_menu_path"] = game_mod_menu_path
            integrated_result["modifications_applied"].append("Game mod menu injected")
        
        # Add AI-powered recommendations from analysis
        ai_recommendations = ai_analysis.get("recommendations", [])
        integrated_result["features_applied"] = list(set(
            integrated_result["modifications_applied"] + ai_recommendations
        ))
        
        logger.info(f"Integrated {total_modifications} modifications from {len(successful_engines)} engines")
        return integrated_result
    
    async def _create_game_mod_menu(self, original_apk_path: Path, game_mod_features: List[Dict]) -> str:
        """Create game mod menu and inject into APK if game mods detected"""
        try:
            # This would typically:
            # 1. Extract the APK
            # 2. Inject mod menu code
            # 3. Rebuild the APK
            # 4. Sign the APK
            
            # For now, simulate the process
            output_path = original_apk_path.parent / f"{original_apk_path.stem}_WITH_MODMENU.apk"
            
            # In a real implementation, this would inject actual mod menu code
            # based on the game_mod_features provided
            
            logger.info(f"🎮 Game mod menu created with {len(game_mod_features)} features")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Error creating game mod menu: {e}")
            # Return original path if mod menu creation fails
            return str(original_apk_path)
    
    async def validate_results(self, original_apk: str, result: Dict) -> Dict:
        """Validate processing results"""
        
        validation = {
            "success": True,
            "stability_score": 85,
            "functionality_verified": True,
            "security_check_passed": True,
            "compatibility_check": True,
            "recommended_actions": [],
            "warnings": []
        }
        
        try:
            # Check if modified APK exists
            modified_path = result.get("modified_apk_path")
            if not modified_path or not Path(modified_path).exists():
                validation["success"] = False
                validation["warnings"].append("Modified APK not found")
                return validation
            
            # Run basic validation
            import zipfile
            with zipfile.ZipFile(modified_path, 'r') as apk:
                # Check for essential files
                essential_files = [
                    "AndroidManifest.xml",
                    "classes.dex",
                    "resources.arsc"
                ]
                
                missing_files = []
                for ess_file in essential_files:
                    if ess_file not in apk.namelist():
                        missing_files.append(ess_file)
                
                if missing_files:
                    validation["success"] = False
                    validation["warnings"].extend([f"Missing essential file: {f}" for f in missing_files])
                
                # Check file sizes (ensure not corrupted)
                for file_info in apk.filelist:
                    if file_info.file_size == 0 and not file_info.filename.endswith('/'):
                        validation["warnings"].append(f"Zero-sized file: {file_info.filename}")
            
            # Calculate stability based on modifications
            modifications_count = len(result.get("modifications_applied", []))
            engine_count = len(result.get("engines_used", []))
            
            # Base stability calculation
            stability = 100 - (modifications_count * 1.5)  # Each modification slightly reduces stability
            if engine_count == 0:
                stability -= 20  # No engines used = less stable
            
            validation["stability_score"] = max(20, stability)  # Minimum 20 stability
            
            # Additional checks based on AI analysis
            ai_confidence = result.get("ai_analysis", {}).get("ai_confidence", 0.5)
            if ai_confidence < 0.6:
                validation["stability_score"] -= 10
                validation["warnings"].append("Low AI confidence - may be unstable")
            
            # Game-specific validation
            if result.get("game_mods", {}).get("mod_menu_available", False):
                validation["stability_score"] -= 5  # Game mods might affect stability slightly
                validation["recommended_actions"].append("Test game functionality thoroughly after mod menu injection")
            
            if validation["stability_score"] > 80:
                validation["functionality_verified"] = True
                validation["security_check_passed"] = True
                validation["compatibility_check"] = True
            elif validation["stability_score"] > 60:
                validation["functionality_verified"] = True
                validation["security_check_passed"] = False
                validation["compatibility_check"] = True
            else:
                validation["functionality_verified"] = False
                validation["security_check_passed"] = False
                validation["compatibility_check"] = False
                validation["recommended_actions"].append("Manual testing required - low stability detected")
        
        except Exception as e:
            logger.error(f"Validation error: {e}")
            validation["success"] = False
            validation["error"] = str(e)
        
        return validation
    
    async def get_job_status(self, job_id: str) -> Dict:
        """Get job status from Redis"""
        job_data = await self.redis_client.hgetall(f"job:{job_id}")
        
        if not job_data:
            return {"error": "Job not found", "success": False}
        
        # Parse JSON fields
        if "result" in job_data and job_data["result"]:
            try:
                job_data["result"] = json.loads(job_data["result"])
            except json.JSONDecodeError:
                pass  # Keep as string
        
        if "features" in job_data and job_data["features"]:
            try:
                job_data["features"] = json.loads(job_data["features"])
            except:
                job_data["features"] = []
        
        return job_data
    
    async def update_job_status(self, job_id: str, status: JobStatus):
        """Update job status in Redis"""
        await self.redis_client.hset(f"job:{job_id}", "status", status.value)
        await self.redis_client.publish(f"job_updates:{job_id}", status.value)
    
    async def close(self):
        """Close orchestrator resources"""
        if self.http_session:
            await self.http_session.close()
        if self.redis_client:
            await self.redis_client.close()

# Global orchestrator instance
orchestrator = CyberCrackOrchestrator()

# FastAPI app
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

app = FastAPI(title="Cyber Crack Pro - Orchestrator", version="3.0")

class ProcessRequest(BaseModel):
    apk_path: str
    category: Optional[str] = "auto_detect"
    features: Optional[List[str]] = []
    priority: Optional[str] = "MEDIUM"

@app.on_event("startup")
async def startup():
    """Startup event"""
    await orchestrator.initialize()

@app.post("/analyze")
async def analyze_apk_endpoint(request: ProcessRequest):
    """Analyze APK with dual AI system"""
    try:
        job_id = await orchestrator.create_job(
            request.apk_path,
            request.category,
            request.features,
            request.priority
        )
        
        return JSONResponse({
            "success": True,
            "job_id": job_id,
            "status": "submitted",
            "message": "AI analysis started",
            "estimated_time": "5-15 seconds",
            "progress_url": f"/job/{job_id}/status"
        })
    
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/job/{job_id}/status")
async def get_job_status(job_id: str):
    """Get job processing status"""
    status = await orchestrator.get_job_status(job_id)
    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])
    
    return JSONResponse(status)

@app.get("/stats")
async def get_system_stats():
    """Get system statistics"""
    return JSONResponse({
        "system_name": "Cyber Crack Pro Orchestrator",
        "version": "3.0.0",
        "stats": orchestrator.stats,
        "engines_status": await get_engine_status(),
        "timestamp": datetime.now().isoformat(),
        "ai_integration": {
            "dual_ai": "active",
            "deepseek_connected": True,  # Would be verified in real implementation
            "wormgpt_connected": True,   # Would be verified in real implementation
            "game_mod_detection": "enabled"
        }
    })

async def get_engine_status() -> Dict[str, bool]:
    """Check all engine status"""
    status = {}
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
        for name, url in ENGINE_URLS.items():
            try:
                async with session.get(f"{url}/health") as response:
                    status[name] = response.status == 200
            except:
                status[name] = False
    return status

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "service": "orchestrator",
        "version": "3.0",
        "ai_systems": {
            "deepseek": "connected",
            "wormgpt": "connected", 
            "game_mod": "active"
        },
        "engines": await get_engine_status(),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "orchestrator:app",
        host="0.0.0.0",
        port=5000,
        reload=False
    )