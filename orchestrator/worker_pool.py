#!/usr/bin/env python3
"""
🚦 CYBER CRACK PRO - Worker Pool
Worker pool for managing concurrent processing tasks
"""

import asyncio
import logging
import json
import os
import signal
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum
import concurrent.futures
from asyncio import Queue, Task
from threading import Thread
import time
import psutil
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WorkerStatus(Enum):
    IDLE = "idle"
    WORKING = "working"
    UNHEALTHY = "unhealthy"
    SHUTDOWN = "shutdown"

class WorkerType(Enum):
    ANALYSIS = "analysis"
    PROCESSING = "processing"
    CRACKING = "cracking"
    GENERAL = "general"

@dataclass
class WorkerTask:
    """Represents a task for a worker"""
    task_id: str
    task_type: WorkerType
    payload: Dict[str, Any]
    priority: int = 0
    created_at: datetime = None
    started_at: datetime = None
    completed_at: datetime = None
    assigned_worker: Optional[str] = None
    timeout: int = 300  # 5 minutes default timeout
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class Worker:
    """Individual worker that processes tasks"""
    
    def __init__(self, worker_id: str, worker_type: WorkerType, max_concurrent_tasks: int = 1):
        self.worker_id = worker_id
        self.worker_type = worker_type
        self.status = WorkerStatus.IDLE
        self.max_concurrent_tasks = max_concurrent_tasks
        self.current_task_count = 0
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        
        # Task queues
        self.task_queue = Queue()
        self.active_tasks: Dict[str, Task] = {}
        
    async def start_worker(self):
        """Start the worker and begin processing tasks"""
        logger.info(f"Starting worker {self.worker_id} of type {self.worker_type.value}")
        
        while self.status != WorkerStatus.SHUTDOWN:
            try:
                if not self.task_queue.empty() and self.current_task_count < self.max_concurrent_tasks:
                    # Get next task
                    task = await self.task_queue.get()
                    self.current_task_count += 1
                    self.status = WorkerStatus.WORKING
                    self.last_activity = datetime.now()
                    
                    # Process task in background
                    asyncio.create_task(self.process_task(task))
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Error in worker {self.worker_id}: {e}")
                self.status = WorkerStatus.UNHEALTHY
                await asyncio.sleep(1)  # Brief pause before continuing
    
    async def process_task(self, task: WorkerTask):
        """Process a single task"""
        try:
            task.assigned_worker = self.worker_id
            task.started_at = datetime.now()
            
            logger.info(f"Worker {self.worker_id} processing task {task.task_id}")
            
            # Simulate processing based on task type
            if task.task_type == WorkerType.ANALYSIS:
                result = await self._perform_analysis(task.payload)
            elif task.task_type == WorkerType.PROCESSING:
                result = await self._perform_processing(task.payload)
            elif task.task_type == WorkerType.CRACKING:
                result = await self._perform_cracking(task.payload)
            else:
                result = await self._perform_general_task(task.payload)
            
            task.completed_at = datetime.now()
            logger.info(f"Task {task.task_id} completed by worker {self.worker_id}")
            
        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {e}")
        finally:
            self.current_task_count -= 1
            if self.current_task_count == 0:
                self.status = WorkerStatus.IDLE
            self.last_activity = datetime.now()
    
    async def _perform_analysis(self, payload: Dict) -> Dict:
        """Perform analysis task"""
        # Simulate analysis work
        await asyncio.sleep(payload.get("duration", 2))
        return {
            "success": True,
            "result": {
                "vulnerabilities": ["Simulated vulnerability"],
                "protections": ["Simulated protection"],
                "security_score": 75
            }
        }
    
    async def _perform_processing(self, payload: Dict) -> Dict:
        """Perform processing task"""
        # Simulate processing work
        await asyncio.sleep(payload.get("duration", 5))
        return {
            "success": True,
            "result": {
                "modified_apk_path": "path/to/modified.apk",
                "fixes_applied": ["Simulated fix"],
                "stability_score": 90
            }
        }
    
    async def _perform_cracking(self, payload: Dict) -> Dict:
        """Perform cracking task"""
        # Simulate cracking work
        await asyncio.sleep(payload.get("duration", 3))
        return {
            "success": True,
            "result": {
                "crack_type": payload.get("crack_type", "generic"),
                "status": "applied"
            }
        }
    
    async def _perform_general_task(self, payload: Dict) -> Dict:
        """Perform general task"""
        # Simulate general work
        await asyncio.sleep(payload.get("duration", 1))
        return {
            "success": True,
            "result": "General task completed"
        }
    
    def assign_task(self, task: WorkerTask) -> bool:
        """Assign a task to this worker"""
        if self.current_task_count < self.max_concurrent_tasks and self.status != WorkerStatus.SHUTDOWN:
            self.task_queue.put_nowait(task)
            return True
        return False
    
    def is_available(self) -> bool:
        """Check if worker is available for new tasks"""
        return (self.status == WorkerStatus.IDLE or 
                self.current_task_count < self.max_concurrent_tasks) and self.status != WorkerStatus.SHUTDOWN

class WorkerPool:
    """Pool of workers for managing concurrent processing"""
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.workers: Dict[str, Worker] = {}
        self.worker_tasks: Dict[str, WorkerTask] = {}
        self.active_task_count = 0
        self.task_queue = Queue()
        self.shutdown_requested = False
        
        # Resource monitoring
        self.cpu_threshold = float(os.getenv("CPU_THRESHOLD", "80.0"))
        self.memory_threshold = float(os.getenv("MEMORY_THRESHOLD", "80.0"))
        
    def create_worker(self, worker_type: WorkerType, max_concurrent: int = 1) -> str:
        """Create a new worker"""
        worker_id = f"worker_{len(self.workers)}_{worker_type.value}"
        
        worker = Worker(worker_id, worker_type, max_concurrent)
        self.workers[worker_id] = worker
        
        # Start worker in background
        asyncio.create_task(worker.start_worker())
        
        logger.info(f"Created worker: {worker_id} of type: {worker_type.value}")
        return worker_id
    
    def create_workers_by_type(self, worker_type: WorkerType, count: int, max_concurrent: int = 1):
        """Create multiple workers of the same type"""
        for i in range(count):
            self.create_worker(worker_type, max_concurrent)
    
    def submit_task(self, task_type: WorkerType, payload: Dict[str, Any], priority: int = 0) -> str:
        """Submit a task to the pool"""
        if self.shutdown_requested:
            raise Exception("Worker pool is shutting down")
        
        task_id = f"task_{int(time.time())}_{len(self.worker_tasks)}"
        
        task = WorkerTask(
            task_id=task_id,
            task_type=task_type,
            payload=payload,
            priority=priority
        )
        
        self.worker_tasks[task_id] = task
        self.task_queue.put_nowait(task)
        
        logger.info(f"Submitted task {task_id} of type {task_type.value}")
        return task_id
    
    async def distribute_tasks(self):
        """Distribute tasks to available workers"""
        while not self.shutdown_requested:
            try:
                # Check for tasks in the queue
                if not self.task_queue.empty():
                    task = self.task_queue.get_nowait()
                    
                    # Find an available worker for this task type
                    worker = self._get_available_worker(task.task_type)
                    
                    if worker:
                        if worker.assign_task(task):
                            logger.info(f"Assigned task {task.task_id} to worker {worker.worker_id}")
                        else:
                            # If assignment failed, put task back in queue
                            self.task_queue.put_nowait(task)
                    else:
                        # No available workers, put task back in queue
                        self.task_queue.put_nowait(task)
                
                # Monitor system resources
                self._check_resources()
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.05)
                
            except asyncio.QueueEmpty:
                # If queue is empty, just wait a bit longer
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in task distribution: {e}")
                await asyncio.sleep(0.1)
    
    def _get_available_worker(self, task_type: WorkerType) -> Optional[Worker]:
        """Get an available worker for the task type"""
        available_workers = []
        
        for worker in self.workers.values():
            # Filter by type and availability
            if (worker.worker_type == task_type or worker.worker_type == WorkerType.GENERAL) and worker.is_available():
                available_workers.append(worker)
        
        # If we have specific workers for this type, return one
        specific_workers = [w for w in available_workers if w.worker_type == task_type]
        if specific_workers:
            # Return the one with fewest active tasks
            return min(specific_workers, key=lambda w: w.current_task_count)
        
        # If no specific workers, return general workers
        general_workers = [w for w in available_workers if w.worker_type == WorkerType.GENERAL]
        if general_workers:
            return min(general_workers, key=lambda w: w.current_task_count)
        
        # No available workers
        return None
    
    def _check_resources(self):
        """Check system resources and adjust worker behavior if needed"""
        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            if cpu_percent > self.cpu_threshold or memory_percent > self.memory_threshold:
                logger.warning(f"High resource usage - CPU: {cpu_percent}%, Memory: {memory_percent}%")
                # In a real implementation, you might want to scale down or pause workers
                
        except Exception as e:
            logger.error(f"Error checking resources: {e}")
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get statistics about the worker pool"""
        total_workers = len(self.workers)
        active_workers = len([w for w in self.workers.values() if w.status == WorkerStatus.WORKING])
        idle_workers = len([w for w in self.workers.values() if w.status == WorkerStatus.IDLE])
        unhealthy_workers = len([w for w in self.workers.values() if w.status == WorkerStatus.UNHEALTHY])
        
        stats = {
            "total_workers": total_workers,
            "active_workers": active_workers,
            "idle_workers": idle_workers,
            "unhealthy_workers": unhealthy_workers,
            "max_workers": self.max_workers,
            "queue_size": self.task_queue.qsize(),
            "active_task_count": self.active_task_count,
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "platform": platform.platform()
            }
        }
        
        # Add per-worker stats
        worker_stats = {}
        for worker_id, worker in self.workers.items():
            worker_stats[worker_id] = {
                "status": worker.status.value,
                "type": worker.worker_type.value,
                "current_tasks": worker.current_task_count,
                "max_concurrent": worker.max_concurrent_tasks,
                "idle_time": (datetime.now() - worker.last_activity).total_seconds()
            }
        stats["worker_details"] = worker_stats
        
        return stats
    
    def get_worker_by_type(self, worker_type: WorkerType) -> List[Worker]:
        """Get all workers of a specific type"""
        return [w for w in self.workers.values() if w.worker_type == worker_type]
    
    async def shutdown(self):
        """Gracefully shutdown the worker pool"""
        logger.info("Shutting down worker pool...")
        self.shutdown_requested = True
        
        # Set all workers to shutdown status
        for worker in self.workers.values():
            worker.status = WorkerStatus.SHUTDOWN
        
        logger.info("Worker pool shutdown complete")

# Global instance
worker_pool = WorkerPool()

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    asyncio.create_task(worker_pool.shutdown())
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

async def main():
    """Main function for testing worker pool"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python worker_pool.py <command> [options]")
        print("Commands:")
        print("  create <type> <count> [max_concurrent] - Create workers")
        print("  submit <type> <payload_json> [priority] - Submit a task")
        print("  stats                              - Get pool statistics")
        print("  list-workers                       - List all workers")
        print("  start-distribution                 - Start task distribution")
        print("  worker-count <type>                - Count workers by type")
        return
    
    command = sys.argv[1]
    
    if command == "create":
        if len(sys.argv) < 4:
            print("Usage: python worker_pool.py create <type> <count> [max_concurrent]")
            return
        
        try:
            worker_type = WorkerType[sys.argv[2].upper()]
        except KeyError:
            print(f"Invalid worker type. Use: {[w.name for w in WorkerType]}")
            return
        
        count = int(sys.argv[3])
        max_concurrent = int(sys.argv[4]) if len(sys.argv) > 4 else 1
        
        for _ in range(count):
            worker_pool.create_worker(worker_type, max_concurrent)
        
        print(f"Created {count} {sys.argv[2]} workers")
    
    elif command == "submit":
        if len(sys.argv) < 4:
            print("Usage: python worker_pool.py submit <type> <payload_json> [priority]")
            return
        
        try:
            task_type = WorkerType[sys.argv[2].upper()]
        except KeyError:
            print(f"Invalid task type. Use: {[w.name for w in WorkerType]}")
            return
        
        try:
            payload = json.loads(sys.argv[3])
        except json.JSONDecodeError:
            print("Invalid JSON payload")
            return
        
        priority = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        
        task_id = worker_pool.submit_task(task_type, payload, priority)
        print(f"Submitted task: {task_id}")
    
    elif command == "stats":
        stats = worker_pool.get_pool_stats()
        print("Worker Pool Statistics:")
        print(json.dumps(stats, indent=2, default=str))
    
    elif command == "list-workers":
        print("Workers:")
        for worker_id, worker in worker_pool.workers.items():
            print(f"  - {worker_id}: {worker.worker_type.value}, status: {worker.status.value}, tasks: {worker.current_task_count}")
    
    elif command == "start-distribution":
        print("Starting task distribution (Ctrl+C to stop)...")
        try:
            await worker_pool.distribute_tasks()
        except KeyboardInterrupt:
            print("\nStopping task distribution...")
            await worker_pool.shutdown()
    
    elif command == "worker-count":
        if len(sys.argv) < 3:
            print("Please provide worker type")
            return
        
        try:
            worker_type = WorkerType[sys.argv[2].upper()]
        except KeyError:
            print(f"Invalid worker type. Use: {[w.name for w in WorkerType]}")
            return
        
        workers = worker_pool.get_worker_by_type(worker_type)
        print(f"Number of {worker_type.value} workers: {len(workers)}")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    asyncio.run(main())