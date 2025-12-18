#!/usr/bin/env python3
"""
🚦 CYBER CRACK PRO - Scheduler
Job scheduler and workflow manager
"""

import asyncio
import logging
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import redis
import aiofiles
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JobStatus(Enum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Job:
    """Represents a processing job"""
    job_id: str
    user_id: str
    job_type: str  # analyze, process, crack
    parameters: Dict[str, Any]
    priority: JobPriority = JobPriority.MEDIUM
    created_at: datetime = None
    scheduled_at: datetime = None
    started_at: datetime = None
    completed_at: datetime = None
    status: JobStatus = JobStatus.PENDING
    result: Optional[Dict] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

class JobScheduler:
    """Advanced job scheduler with prioritization and retry logic"""
    
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.job_queue = asyncio.Queue()
        self.active_jobs: Dict[str, Job] = {}
        self.completed_jobs: Dict[str, Job] = {}
        self.failed_jobs: Dict[str, Job] = {}
        self.redis_client = self._init_redis()
        self.max_concurrent_jobs = int(os.getenv("MAX_CONCURRENT_JOBS", "5"))
        self.active_task_count = 0
        
    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection for persistence"""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            client = redis.from_url(redis_url, decode_responses=True)
            client.ping()  # Test connection
            logger.info("Successfully connected to Redis for job persistence")
            return client
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            return None
    
    def create_job(self, user_id: str, job_type: str, parameters: Dict[str, Any], 
                   priority: JobPriority = JobPriority.MEDIUM, job_id: str = None) -> str:
        """Create a new job and add to queue"""
        if not job_id:
            job_id = f"job_{user_id}_{int(time.time())}_{len(self.jobs)}"
        
        job = Job(
            job_id=job_id,
            user_id=user_id,
            job_type=job_type,
            parameters=parameters,
            priority=priority,
            created_at=datetime.now(),
            status=JobStatus.PENDING
        )
        
        self.jobs[job_id] = job
        self._persist_job(job)
        
        # Add to queue based on priority
        self._add_to_queue(job)
        
        logger.info(f"Created job {job_id} for user {user_id}, type: {job_type}")
        return job_id
    
    def _add_to_queue(self, job: Job):
        """Add job to the appropriate queue"""
        # For now, we'll just use a single priority queue
        # In a more complex system, we could have multiple queues
        asyncio.create_task(self._queue_job_with_priority(job))
    
    async def _queue_job_with_priority(self, job: Job):
        """Add job to queue with proper priority handling"""
        # Wait based on priority (lower value = higher priority)
        priority_delay = (JobPriority.CRITICAL.value - job.priority.value) * 0.1
        await asyncio.sleep(priority_delay)
        
        await self.job_queue.put((job.priority.value, job.job_id))
        self._update_job_status(job.job_id, JobStatus.QUEUED)
    
    def _persist_job(self, job: Job):
        """Persist job to Redis"""
        if self.redis_client:
            try:
                job_data = {
                    'job_id': job.job_id,
                    'user_id': job.user_id,
                    'job_type': job.job_type,
                    'parameters': json.dumps(job.parameters),
                    'priority': job.priority.value,
                    'created_at': job.created_at.isoformat() if job.created_at else None,
                    'scheduled_at': job.scheduled_at.isoformat() if job.scheduled_at else None,
                    'started_at': job.started_at.isoformat() if job.started_at else None,
                    'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                    'status': job.status.value,
                    'result': json.dumps(job.result) if job.result else None,
                    'error_message': job.error_message,
                    'retry_count': job.retry_count,
                    'max_retries': job.max_retries
                }
                self.redis_client.setex(f"job:{job.job_id}", 86400, json.dumps(job_data))  # 24h expiry
            except Exception as e:
                logger.warning(f"Failed to persist job {job.job_id} to Redis: {e}")
    
    def _update_job_status(self, job_id: str, status: JobStatus, result: Dict = None):
        """Update job status and persist changes"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            job.status = status
            
            if status == JobStatus.PROCESSING:
                job.started_at = datetime.now()
            elif status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                job.completed_at = datetime.now()
                
            if result:
                job.result = result
            
            self._persist_job(job)
    
    async def process_job(self, job_id: str) -> Dict:
        """Process a single job"""
        if job_id not in self.jobs:
            return {"error": f"Job {job_id} not found"}
        
        job = self.jobs[job_id]
        self._update_job_status(job_id, JobStatus.PROCESSING)
        
        try:
            # Simulate processing based on job type
            if job.job_type == "analyze":
                result = await self._execute_analysis_job(job)
            elif job.job_type == "process":
                result = await self._execute_processing_job(job)
            elif job.job_type == "crack":
                result = await self._execute_crack_job(job)
            else:
                result = {"error": f"Unknown job type: {job.job_type}"}
            
            if not result.get("error"):
                self._update_job_status(job_id, JobStatus.COMPLETED, result)
                self.completed_jobs[job_id] = job
                del self.jobs[job_id]
                return result
            else:
                # Handle failure with retries
                await self._handle_job_failure(job)
                return result
                
        except Exception as e:
            error_msg = f"Job {job_id} failed: {str(e)}"
            logger.error(error_msg)
            
            # Update job with error
            job.error_message = error_msg
            self._update_job_status(job_id, JobStatus.FAILED, {"error": error_msg})
            self.failed_jobs[job_id] = job
            del self.jobs[job_id]
            
            return {"error": error_msg}
    
    async def _execute_analysis_job(self, job: Job) -> Dict:
        """Execute analysis job"""
        # Simulate analysis
        await asyncio.sleep(2)  # Simulate processing time
        
        # In a real implementation, this would call the analysis engines
        return {
            "job_id": job.job_id,
            "success": True,
            "result": {
                "vulnerabilities": ["Example vulnerability"],
                "protections": ["Certificate Pinning", "Root Detection"],
                "security_score": 65,
                "recommendations": ["Implement stronger encryption"]
            }
        }
    
    async def _execute_processing_job(self, job: Job) -> Dict:
        """Execute processing job"""
        # Simulate processing
        await asyncio.sleep(5)  # Simulate processing time
        
        # In a real implementation, this would modify the APK
        return {
            "job_id": job.job_id,
            "success": True,
            "result": {
                "modified_apk_path": f"output/{job.job_id}_modified.apk",
                "fixes_applied": ["Certificate pinning bypassed"],
                "stability_score": 85
            }
        }
    
    async def _execute_crack_job(self, job: Job) -> Dict:
        """Execute crack job"""
        # Simulate cracking
        await asyncio.sleep(3)  # Simulate processing time
        
        # In a real implementation, this would apply specific cracks
        return {
            "job_id": job.job_id,
            "success": True,
            "result": {
                "crack_type": job.parameters.get("crack_type", "unknown"),
                "target": job.parameters.get("target", "unknown"),
                "status": "applied"
            }
        }
    
    async def _handle_job_failure(self, job: Job):
        """Handle job failure with retry logic"""
        job.retry_count += 1
        
        if job.retry_count <= job.max_retries:
            logger.info(f"Job {job.job_id} failed, retrying ({job.retry_count}/{job.max_retries})")
            # Re-queue the job with a delay
            await asyncio.sleep(2 ** job.retry_count)  # Exponential backoff
            self._add_to_queue(job)
        else:
            logger.error(f"Job {job.job_id} failed after {job.max_retries} retries")
            self._update_job_status(job.job_id, JobStatus.FAILED)
            self.failed_jobs[job.job_id] = job
            if job.job_id in self.jobs:
                del self.jobs[job.job_id]
    
    async def process_queue(self):
        """Main processing loop"""
        logger.info("Job scheduler started")
        
        while True:
            try:
                # Process jobs from queue
                if self.active_task_count < self.max_concurrent_jobs and not self.job_queue.empty():
                    # Get job from queue (priority, job_id)
                    _, job_id = await self.job_queue.get()
                    
                    if job_id in self.jobs and self.jobs[job_id].status == JobStatus.QUEUED:
                        self.active_task_count += 1
                        # Process job in background
                        asyncio.create_task(self._finish_job_processing(job_id))
                
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(1)  # Brief pause before continuing
    
    async def _finish_job_processing(self, job_id: str):
        """Finish processing a job and update counters"""
        try:
            await self.process_job(job_id)
        finally:
            self.active_task_count -= 1
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get status of a specific job"""
        job = self.jobs.get(job_id)
        if not job:
            # Check completed/failed jobs
            job = self.completed_jobs.get(job_id) or self.failed_jobs.get(job_id)
        
        if job:
            return {
                'job_id': job.job_id,
                'user_id': job.user_id,
                'job_type': job.job_type,
                'status': job.status.value,
                'priority': job.priority.value,
                'created_at': job.created_at.isoformat() if job.created_at else None,
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'result': job.result,
                'error_message': job.error_message,
                'retry_count': job.retry_count
            }
        return None
    
    def get_user_jobs(self, user_id: str) -> List[Dict]:
        """Get all jobs for a specific user"""
        user_jobs = []
        
        # Check active jobs
        for job in self.jobs.values():
            if job.user_id == user_id:
                user_jobs.append(self.get_job_status(job.job_id))
        
        # Check completed jobs
        for job in self.completed_jobs.values():
            if job.user_id == user_id:
                user_jobs.append(self.get_job_status(job.job_id))
        
        # Check failed jobs
        for job in self.failed_jobs.values():
            if job.user_id == user_id:
                user_jobs.append(self.get_job_status(job.job_id))
        
        return user_jobs
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending or queued job"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            if job.status in [JobStatus.PENDING, JobStatus.QUEUED]:
                self._update_job_status(job_id, JobStatus.CANCELLED)
                del self.jobs[job_id]
                logger.info(f"Job {job_id} cancelled")
                return True
        return False
    
    def get_queue_stats(self) -> Dict:
        """Get statistics about the job queue"""
        return {
            'pending_jobs': len([j for j in self.jobs.values() if j.status == JobStatus.PENDING]),
            'queued_jobs': len([j for j in self.jobs.values() if j.status == JobStatus.QUEUED]),
            'processing_jobs': len([j for j in self.jobs.values() if j.status == JobStatus.PROCESSING]),
            'completed_jobs': len(self.completed_jobs),
            'failed_jobs': len(self.failed_jobs),
            'active_concurrent_jobs': self.active_task_count,
            'max_concurrent_jobs': self.max_concurrent_jobs
        }
    
    async def schedule_recurring_job(self, job_type: str, parameters: Dict, 
                                   interval_seconds: int, user_id: str = "system") -> str:
        """Schedule a recurring job"""
        # This would involve a more complex scheduling system
        # For now, just create a one-time job
        job_id = self.create_job(
            user_id=user_id,
            job_type=job_type,
            parameters=parameters,
            priority=JobPriority.LOW
        )
        logger.info(f"Scheduled recurring job {job_id} to run every {interval_seconds}s")
        return job_id

# Global instance
scheduler = JobScheduler()

async def start_scheduler():
    """Start the job scheduler"""
    await scheduler.process_queue()

def main():
    """Main function for testing scheduler"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python scheduler.py <command> [options]")
        print("Commands:")
        print("  create-job <user_id> <type> <params> [priority] - Create a job")
        print("  get-status <job_id>            - Get job status")
        print("  get-user-jobs <user_id>        - Get all jobs for user")
        print("  cancel <job_id>                - Cancel a job")
        print("  stats                          - Show queue statistics")
        print("  start                          - Start the scheduler (run separately)")
        return
    
    command = sys.argv[1]
    
    if command == "create-job":
        if len(sys.argv) < 5:
            print("Usage: python scheduler.py create-job <user_id> <type> <params_json> [priority]")
            return
        
        user_id = sys.argv[2]
        job_type = sys.argv[3]
        params_json = sys.argv[4]
        
        try:
            parameters = json.loads(params_json)
        except json.JSONDecodeError:
            print("Invalid JSON parameters")
            return
        
        priority_str = sys.argv[5] if len(sys.argv) > 5 else "MEDIUM"
        try:
            priority = JobPriority[priority_str.upper()]
        except KeyError:
            print(f"Invalid priority. Use: {', '.join([p.name for p in JobPriority])}")
            return
        
        job_id = scheduler.create_job(user_id, job_type, parameters, priority)
        print(f"Created job: {job_id}")
    
    elif command == "get-status":
        if len(sys.argv) < 3:
            print("Please provide job ID")
            return
        
        job_id = sys.argv[2]
        status = scheduler.get_job_status(job_id)
        print(f"Job status: {status}")
    
    elif command == "get-user-jobs":
        if len(sys.argv) < 3:
            print("Please provide user ID")
            return
        
        user_id = sys.argv[2]
        jobs = scheduler.get_user_jobs(user_id)
        print(f"User {user_id} has {len(jobs)} jobs:")
        for job in jobs:
            print(f"  - {job['job_id']}: {job['status']}")
    
    elif command == "cancel":
        if len(sys.argv) < 3:
            print("Please provide job ID")
            return
        
        job_id = sys.argv[2]
        result = scheduler.cancel_job(job_id)
        print(f"Cancel job: {'SUCCESS' if result else 'FAILED or job not found'}")
    
    elif command == "stats":
        stats = scheduler.get_queue_stats()
        print("Job Queue Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    elif command == "start":
        print("Starting job scheduler...")
        print("Use Ctrl+C to stop")
        try:
            asyncio.run(start_scheduler())
        except KeyboardInterrupt:
            print("\nScheduler stopped")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()