#!/usr/bin/env python3
"""
🚦 CYBER CRACK PRO - Job Manager
Advanced job management system for tracking and controlling jobs across engines
"""

import asyncio
import logging
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
from concurrent.futures import ThreadPoolExecutor
import aiofiles

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JobStatus(Enum):
    PENDING = "pending"
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"
    TIMEOUT = "timeout"

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
    job_type: str  # analyze, process, crack, custom
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
    timeout_seconds: int = 3600  # 1 hour default timeout
    engine: str = "auto"  # Which engine to use
    dependencies: List[str] = None  # Job IDs this job depends on
    metadata: Dict[str, Any] = None  # Additional metadata

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}

class JobManager:
    """Advanced job management system"""
    
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.redis_client = self._init_redis()
        self.db_connection = self._init_postgres()
        self.max_concurrent_jobs = int(os.getenv("MAX_CONCURRENT_JOBS", "10"))
        self.active_jobs: Dict[str, asyncio.Task] = {}
        
    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection"""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            client = redis.from_url(redis_url, decode_responses=True)
            client.ping()
            logger.info("Successfully connected to Redis for job persistence")
            return client
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            return None
    
    def _init_postgres(self) -> Optional[psycopg2.extensions.connection]:
        """Initialize PostgreSQL connection for persistence"""
        try:
            conn = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST", "localhost"),
                database=os.getenv("POSTGRES_DB", "cybercrackpro"),
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", "password"),
                port=os.getenv("POSTGRES_PORT", "5432")
            )
            logger.info("Successfully connected to PostgreSQL for job persistence")
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            return None
    
    def create_job(self, 
                   user_id: str, 
                   job_type: str, 
                   parameters: Dict[str, Any],
                   priority: JobPriority = JobPriority.MEDIUM,
                   engine: str = "auto",
                   dependencies: List[str] = None,
                   timeout_seconds: int = 3600) -> str:
        """Create a new job"""
        job_id = f"job_{uuid.uuid4().hex}"
        
        job = Job(
            job_id=job_id,
            user_id=user_id,
            job_type=job_type,
            parameters=parameters,
            priority=priority,
            engine=engine,
            dependencies=dependencies or [],
            timeout_seconds=timeout_seconds
        )
        
        self.jobs[job_id] = job
        self._persist_job(job)
        
        logger.info(f"Created job {job_id} for user {user_id}, type: {job_type}")
        return job_id
    
    def _persist_job(self, job: Job):
        """Persist job to both Redis and PostgreSQL"""
        # Persist to Redis for fast access
        if self.redis_client:
            try:
                job_data = asdict(job)
                # Convert datetime objects to ISO format strings
                for key, value in job_data.items():
                    if isinstance(value, datetime):
                        job_data[key] = value.isoformat()
                    elif isinstance(value, JobPriority):
                        job_data[key] = value.name
                    elif isinstance(value, JobStatus):
                        job_data[key] = value.name
                
                self.redis_client.setex(f"job:{job.job_id}", 86400, json.dumps(job_data))
            except Exception as e:
                logger.warning(f"Failed to persist job {job.job_id} to Redis: {e}")
        
        # Persist to PostgreSQL for permanent storage
        if self.db_connection:
            try:
                with self.db_connection.cursor() as cur:
                    # Insert job data
                    cur.execute("""
                        INSERT INTO jobs (
                            job_id, user_id, apk_name, category, subcategory, 
                            status, priority, created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (job_id) DO UPDATE SET
                            status = EXCLUDED.status,
                            priority = EXCLUDED.priority,
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        str(job.job_id),
                        job.user_id,
                        job.parameters.get('apk_name', 'unknown.apk'),
                        job.parameters.get('category', 'unknown'),
                        job.parameters.get('subcategory', 'unknown'),
                        job.status.name,
                        job.priority.value,
                        job.created_at.isoformat()
                    ))
                    self.db_connection.commit()
            except Exception as e:
                logger.warning(f"Failed to persist job {job.job_id} to PostgreSQL: {e}")
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        # First check in-memory cache
        if job_id in self.jobs:
            return self.jobs[job_id]
        
        # Then check Redis
        if self.redis_client:
            try:
                job_data = self.redis_client.get(f"job:{job_id}")
                if job_data:
                    data = json.loads(job_data)
                    # Convert string values back to proper types
                    data['priority'] = JobPriority[data['priority']]
                    data['status'] = JobStatus[data['status']]
                    if data['created_at']:
                        data['created_at'] = datetime.fromisoformat(data['created_at'])
                    if data['scheduled_at']:
                        data['scheduled_at'] = datetime.fromisoformat(data['scheduled_at'])
                    if data['started_at']:
                        data['started_at'] = datetime.fromisoformat(data['started_at'])
                    if data['completed_at']:
                        data['completed_at'] = datetime.fromisoformat(data['completed_at'])
                    
                    job = Job(**{k: v for k, v in data.items() if k in Job.__annotations__})
                    self.jobs[job_id] = job  # Cache in memory
                    return job
            except Exception as e:
                logger.warning(f"Failed to get job {job_id} from Redis: {e}")
        
        return None
    
    def update_job_status(self, job_id: str, status: JobStatus, result: Dict = None):
        """Update job status and persist changes"""
        job = self.get_job(job_id)
        if not job:
            logger.error(f"Job {job_id} not found for status update")
            return False
        
        job.status = status
        
        if status == JobStatus.PROCESSING:
            job.started_at = datetime.now()
        elif status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            job.completed_at = datetime.now()
        
        if result:
            job.result = result
        
        self._persist_job(job)
        return True
    
    def update_job_result(self, job_id: str, result: Dict):
        """Update job result without changing status"""
        job = self.get_job(job_id)
        if job:
            job.result = result
            self._persist_job(job)
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job"""
        job = self.get_job(job_id)
        if not job:
            return False
        
        if job.status in [JobStatus.PENDING, JobStatus.QUEUED, JobStatus.SCHEDULED]:
            self.update_job_status(job_id, JobStatus.CANCELLED)
            logger.info(f"Job {job_id} cancelled")
            return True
        else:
            logger.warning(f"Cannot cancel job {job_id}, current status: {job.status}")
            return False
    
    def retry_job(self, job_id: str) -> bool:
        """Retry a failed job"""
        job = self.get_job(job_id)
        if not job or job.status != JobStatus.FAILED:
            return False
        
        if job.retry_count < job.max_retries:
            job.retry_count += 1
            job.status = JobStatus.RETRYING
            job.started_at = None
            job.completed_at = None
            job.error_message = None
            self._persist_job(job)
            logger.info(f"Job {job_id} scheduled for retry {job.retry_count}/{job.max_retries}")
            return True
        
        return False
    
    def get_user_jobs(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get jobs for a specific user"""
        # This would typically query the database
        user_jobs = []
        
        # In-memory filtering (for demonstration)
        all_jobs = list(self.jobs.values())
        user_jobs.extend([
            job for job in all_jobs 
            if job.user_id == user_id
        ])
        
        # Also check Redis for persisted jobs
        if self.redis_client:
            try:
                # Get all job keys for this user (this is simplified)
                job_keys = self.redis_client.keys(f"job:*")
                for key in job_keys:
                    job_data = self.redis_client.get(key)
                    if job_data:
                        data = json.loads(job_data)
                        if data.get('user_id') == user_id:
                            user_jobs.append(self._dict_to_job(data))
            except Exception as e:
                logger.warning(f"Error retrieving user jobs from Redis: {e}")
        
        # Sort by creation time, newest first
        user_jobs.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply limit and offset
        start_idx = offset
        end_idx = offset + limit
        paginated_jobs = user_jobs[start_idx:end_idx]
        
        # Convert to dict format
        return [asdict(job) for job in paginated_jobs]
    
    def _dict_to_job(self, data: Dict) -> Job:
        """Convert dictionary to Job object"""
        # Convert string values back to proper types
        data['priority'] = JobPriority[data['priority']]
        data['status'] = JobStatus[data['status']]
        if data['created_at']:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data['scheduled_at']:
            data['scheduled_at'] = datetime.fromisoformat(data['scheduled_at'])
        if data['started_at']:
            data['started_at'] = datetime.fromisoformat(data['started_at'])
        if data['completed_at']:
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        
        return Job(**{k: v for k, v in data.items() if k in Job.__annotations__})
    
    def get_job_stats(self, user_id: str = None) -> Dict:
        """Get statistics about jobs"""
        stats = {
            'total_jobs': 0,
            'by_status': {},
            'by_type': {},
            'by_priority': {},
            'avg_processing_time': 0
        }
        
        jobs_to_check = list(self.jobs.values())
        
        # Add jobs from Redis
        if self.redis_client:
            try:
                job_keys = self.redis_client.keys(f"job:*")
                for key in job_keys:
                    job_data = self.redis_client.get(key)
                    if job_data:
                        data = json.loads(job_data)
                        job = self._dict_to_job(data)
                        if not user_id or job.user_id == user_id:
                            jobs_to_check.append(job)
            except Exception as e:
                logger.warning(f"Error getting job stats from Redis: {e}")
        
        # Filter by user if specified
        if user_id:
            jobs_to_check = [job for job in jobs_to_check if job.user_id == user_id]
        
        stats['total_jobs'] = len(jobs_to_check)
        
        # Count by status
        for job in jobs_to_check:
            status = job.status.name
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            job_type = job.job_type
            stats['by_type'][job_type] = stats['by_type'].get(job_type, 0) + 1
            
            priority = job.priority.name
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
        
        # Calculate average processing time
        processing_times = []
        for job in jobs_to_check:
            if job.started_at and job.completed_at:
                processing_time = (job.completed_at - job.started_at).total_seconds()
                processing_times.append(processing_time)
        
        if processing_times:
            stats['avg_processing_time'] = sum(processing_times) / len(processing_times)
        
        return stats
    
    def cleanup_old_jobs(self, days_old: int = 7) -> int:
        """Clean up jobs older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        deleted_count = 0
        
        jobs_to_delete = []
        for job_id, job in self.jobs.items():
            if job.completed_at and job.completed_at < cutoff_date:
                jobs_to_delete.append(job_id)
        
        for job_id in jobs_to_delete:
            del self.jobs[job_id]
            # Also remove from Redis if present
            if self.redis_client:
                try:
                    self.redis_client.delete(f"job:{job_id}")
                except:
                    pass
            deleted_count += 1
        
        logger.info(f"Cleaned up {deleted_count} jobs older than {days_old} days")
        return deleted_count

# Global instance
job_manager = JobManager()

async def main():
    """Main function for testing job manager"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python job_manager.py <command> [options]")
        print("Commands:")
        print("  create <user_id> <type> <params_json> [priority] - Create a job")
        print("  get <job_id>                    - Get job details")
        print("  update-status <job_id> <status> - Update job status")
        print("  cancel <job_id>                 - Cancel a job")
        print("  retry <job_id>                  - Retry a failed job")
        print("  user-jobs <user_id> [limit] [offset] - Get user's jobs")
        print("  stats [user_id]                 - Get job statistics")
        print("  cleanup [days]                  - Clean up old jobs")
        return
    
    command = sys.argv[1]
    
    if command == "create":
        if len(sys.argv) < 5:
            print("Usage: python job_manager.py create <user_id> <type> <params_json> [priority]")
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
        
        job_id = job_manager.create_job(user_id, job_type, parameters, priority)
        print(f"Created job: {job_id}")
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("Please provide job ID")
            return
        
        job_id = sys.argv[2]
        job = job_manager.get_job(job_id)
        if job:
            print(f"Job: {asdict(job)}")
        else:
            print(f"Job {job_id} not found")
    
    elif command == "update-status":
        if len(sys.argv) < 4:
            print("Usage: python job_manager.py update-status <job_id> <status>")
            return
        
        job_id = sys.argv[2]
        status_str = sys.argv[3]
        try:
            status = JobStatus[status_str.upper()]
        except KeyError:
            print(f"Invalid status. Use: {', '.join([s.name for s in JobStatus])}")
            return
        
        result = job_manager.update_job_status(job_id, status)
        print(f"Update status: {'SUCCESS' if result else 'FAILED'}")
    
    elif command == "cancel":
        if len(sys.argv) < 3:
            print("Please provide job ID")
            return
        
        job_id = sys.argv[2]
        result = job_manager.cancel_job(job_id)
        print(f"Cancel job: {'SUCCESS' if result else 'FAILED'}")
    
    elif command == "retry":
        if len(sys.argv) < 3:
            print("Please provide job ID")
            return
        
        job_id = sys.argv[2]
        result = job_manager.retry_job(job_id)
        print(f"Retry job: {'SUCCESS' if result else 'FAILED'}")
    
    elif command == "user-jobs":
        if len(sys.argv) < 3:
            print("Please provide user ID")
            return
        
        user_id = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        offset = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        
        jobs = job_manager.get_user_jobs(user_id, limit, offset)
        print(f"Found {len(jobs)} jobs:")
        for job in jobs:
            print(f"  - {job['job_id']}: {job['status']} ({job['job_type']})")
    
    elif command == "stats":
        user_id = sys.argv[2] if len(sys.argv) > 2 else None
        stats = job_manager.get_job_stats(user_id)
        print("Job Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    elif command == "cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        count = job_manager.cleanup_old_jobs(days)
        print(f"Cleaned up {count} old jobs")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    asyncio.run(main())