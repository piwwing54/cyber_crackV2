import asyncio
import logging
import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import aiohttp
import redis.asyncio as redis
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import hashlib
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
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
class Task:
    """Task representation for the queue manager"""
    task_id: str
    user_id: str
    task_type: str  # "analyze", "process", "crack", etc.
    apk_path: str
    category: str
    features: List[str]
    priority: TaskPriority
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict] = None
    error_message: Optional[str] = None

class QueueManager:
    """Advanced task queue management system"""
    
    def __init__(self):
        self.redis_client = None
        self.active_tasks = {}
        self.max_queue_size = int(os.getenv("MAX_QUEUE_SIZE", "1000"))
        self.max_concurrent_tasks = int(os.getenv("MAX_CONCURRENT_TASKS", "20"))
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "current_queue_size": 0,
            "active_workers": 0
        }
        
    async def initialize(self):
        """Initialize queue manager"""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
        logger.info("Queue manager initialized")
    
    async def add_task(self, task_data: Dict) -> str:
        """Add task to queue"""
        task_id = f"task_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
        
        # Validate queue size
        current_size = await self.redis_client.llen("task_queue")
        if current_size >= self.max_queue_size:
            raise Exception(f"Queue at maximum capacity ({self.max_queue_size})")
        
        # Create task
        task = Task(
            task_id=task_id,
            user_id=task_data.get("user_id", "anonymous"),
            task_type=task_data.get("task_type", "analyze"),
            apk_path=task_data["apk_path"],
            category=task_data.get("category", "auto_detect"),
            features=task_data.get("features", []),
            priority=TaskPriority[task_data.get("priority", "MEDIUM")],
            created_at=datetime.now()
        )
        
        # Serialize task
        task_dict = asdict(task)
        task_dict["created_at"] = task_dict["created_at"].isoformat()
        task_dict["priority"] = task_dict["priority"].name
        task_dict["status"] = task_dict["status"].name
        
        # Add to Redis queue based on priority
        await self.redis_client.zadd(
            "task_queue:priority", 
            {task_id: task.priority.value}
        )
        
        # Also add to regular queue
        await self.redis_client.rpush("task_queue", task_id)
        
        # Store task details
        await self.redis_client.hset(f"task:{task_id}", mapping=task_dict)
        
        # Update stats
        self.stats["total_tasks"] += 1
        self.stats["current_queue_size"] += 1
        
        logger.info(f"Added task {task_id} to queue (priority: {task.priority.name})")
        return task_id
    
    async def get_next_task(self) -> Optional[Task]:
        """Get next task from queue based on priority"""
        # Get highest priority task
        task_ids = await self.redis_client.zrange(
            "task_queue:priority", 0, 0, desc=True
        )
        
        if not task_ids:
            return None
        
        task_id = task_ids[0]
        
        # Get task details
        task_data = await self.redis_client.hgetall(f"task:{task_id}")
        if not task_data:
            return None
        
        # Deserialize
        task_data["priority"] = TaskPriority[task_data["priority"]]
        task_data["status"] = TaskStatus[task_data["status"]]
        task_data["created_at"] = datetime.fromisoformat(task_data["created_at"])
        
        if task_data.get("started_at"):
            task_data["started_at"] = datetime.fromisoformat(task_data["started_at"])
        if task_data.get("completed_at"):
            task_data["completed_at"] = datetime.fromisoformat(task_data["completed_at"])
        
        if task_data.get("features"):
            try:
                task_data["features"] = json.loads(task_data["features"])
            except:
                task_data["features"] = []
        
        # Mark as processing
        task_data["status"] = TaskStatus.PROCESSING
        task_data["started_at"] = datetime.now().isoformat()
        
        await self.redis_client.hset(f"task:{task_id}", mapping={
            "status": TaskStatus.PROCESSING.name,
            "started_at": task_data["started_at"]
        })
        
        # Remove from priority queue
        await self.redis_client.zrem("task_queue:priority", task_id)
        
        return Task(**{k: v for k, v in task_data.items() if k in Task.__annotations__})
    
    async def update_task_status(self, task_id: str, status: TaskStatus, 
                               result: Optional[Dict] = None, error: Optional[str] = None):
        """Update task status"""
        updates = {
            "status": status.name,
            "updated_at": datetime.now().isoformat()
        }
        
        if result:
            updates["result"] = json.dumps(result)
        
        if error:
            updates["error_message"] = error
        
        if status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            updates["completed_at"] = datetime.now().isoformat()
            if status == TaskStatus.COMPLETED:
                self.stats["completed_tasks"] += 1
            elif status == TaskStatus.FAILED:
                self.stats["failed_tasks"] += 1
        
        await self.redis_client.hset(f"task:{task_id}", mapping=updates)
        
        # Update queue stats
        if status == TaskStatus.COMPLETED:
            self.stats["current_queue_size"] = max(0, self.stats["current_queue_size"] - 1)
    
    async def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get task status"""
        task_data = await self.redis_client.hgetall(f"task:{task_id}")
        
        if not task_data:
            return None
        
        # Convert status and priority
        task_data["status"] = TaskStatus[task_data["status"]].value
        if "priority" in task_data:
            try:
                task_data["priority"] = TaskPriority[task_data["priority"]].value
            except KeyError:
                task_data["priority"] = TaskPriority.MEDIUM.value
        
        # Parse JSON fields
        if "result" in task_data and task_data["result"]:
            try:
                task_data["result"] = json.loads(task_data["result"])
            except json.JSONDecodeError:
                pass
        
        if "features" in task_data and task_data["features"]:
            try:
                task_data["features"] = json.loads(task_data["features"])
            except json.JSONDecodeError:
                task_data["features"] = []
        
        return task_data
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        current_status = await self.redis_client.hget(f"task:{task_id}", "status")
        
        if current_status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            return False  # Can't cancel completed/failed tasks
        
        # Update status to cancelled
        await self.redis_client.hset(f"task:{task_id}", mapping={
            "status": TaskStatus.CANCELLED.name,
            "completed_at": datetime.now().isoformat()
        })
        
        # Remove from priority queue if exists
        await self.redis_client.zrem("task_queue:priority", task_id)
        
        # Remove from regular queue if exists
        await self.redis_client.lrem("task_queue", 0, task_id)
        
        return True
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        stats = self.stats.copy()
        
        # Add Redis-specific stats
        stats["queue_size"] = await self.redis_client.llen("task_queue")
        stats["waiting_tasks"] = await self.redis_client.zcard("task_queue:priority")
        stats["active_tasks"] = len([
            k for k in await self.redis_client.keys("task:*") 
            if await self.redis_client.hget(k, "status") == TaskStatus.PROCESSING.name
        ])
        
        return stats
    
    async def clear_queue(self) -> bool:
        """Clear all tasks from queue"""
        try:
            # Delete all queue-related keys
            await self.redis_client.delete("task_queue")
            await self.redis_client.delete("task_queue:priority")
            
            # Cancel all active tasks
            task_keys = await self.redis_client.keys("task:*")
            for key in task_keys:
                task_id = key.replace("task:", "")
                await self.cancel_task(task_id)
            
            # Reset stats
            self.stats["current_queue_size"] = 0
            
            return True
        except Exception as e:
            logger.error(f"Error clearing queue: {e}")
            return False
    
    async def get_user_tasks(self, user_id: str) -> List[Dict]:
        """Get all tasks for a specific user"""
        all_task_ids = await self.redis_client.lrange("task_queue", 0, -1)
        priority_task_ids = await self.redis_client.zrange("task_queue:priority", 0, -1)
        all_task_ids.extend(priority_task_ids)
        
        user_tasks = []
        for task_id in set(all_task_ids):  # Remove duplicates
            task_data = await self.redis_client.hgetall(f"task:{task_id}")
            if task_data and task_data.get("user_id") == user_id:
                # Format the task data
                formatted_task = {
                    "task_id": task_id,
                    "status": task_data.get("status", "unknown"),
                    "task_type": task_data.get("task_type", "unknown"),
                    "category": task_data.get("category", "unknown"),
                    "created_at": task_data.get("created_at", "unknown"),
                    "priority": task_data.get("priority", "MEDIUM")
                }
                user_tasks.append(formatted_task)
        
        # Sort by creation time
        user_tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return user_tasks[:50]  # Limit to last 50 tasks

# Global queue manager instance
queue_manager = QueueManager()

class LoadBalancer:
    """Advanced load balancer for distributing tasks to engines"""
    
    def __init__(self):
        self.engines = {}
        self.engine_stats = {}
        self.redis_client = None
        self.health_check_interval = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))
        
    async def initialize(self):
        """Initialize load balancer"""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
        # Register engines
        await self.register_engine("go-analyzer", os.getenv("GO_ENGINE_URL", "http://go-analyzer:8080"), "go", 10)
        await self.register_engine("rust-cracker", os.getenv("RUST_ENGINE_URL", "http://rust-cracker:8081"), "rust", 8)
        await self.register_engine("cpp-breaker", os.getenv("CPP_ENGINE_URL", "http://cpp-breaker:8082"), "cpp", 15)
        await self.register_engine("java-dex", os.getenv("JAVA_ENGINE_URL", "http://java-dex:8083"), "java", 12)
        await self.register_engine("python-bridge", os.getenv("PYTHON_ENGINE_URL", "http://python-bridge:8084"), "python", 5)
        
        # Start health check loop
        asyncio.create_task(self.health_check_loop())
        
        logger.info("Load balancer initialized with engines")
    
    async def register_engine(self, name: str, url: str, engine_type: str, capacity: int):
        """Register an engine with the load balancer"""
        self.engines[name] = {
            "url": url,
            "type": engine_type,
            "capacity": capacity,
            "current_load": 0,
            "status": "healthy",
            "last_health_check": datetime.now(),
            "response_times": [],
            "success_rate": 1.0
        }
        
        self.engine_stats[name] = {
            "requests_handled": 0,
            "success_count": 0,
            "error_count": 0,
            "avg_response_time": 0.0,
            "total_response_time": 0.0
        }
        
        # Store in Redis
        await self.redis_client.hset(f"engine:{name}", mapping={
            "url": url,
            "type": engine_type,
            "capacity": capacity,
            "status": "healthy",
            "current_load": 0
        })
    
    async def select_engine(self, task_type: str) -> Optional[str]:
        """Select optimal engine based on task type and current load"""
        available_engines = []
        
        for name, engine in self.engines.items():
            if (engine["status"] == "healthy" and 
                engine["current_load"] < engine["capacity"]):
                
                # Calculate score based on load (lower load = better)
                load_ratio = engine["current_load"] / engine["capacity"]
                score = (1 - load_ratio) * 100  # Higher score = better choice
                
                # Adjust score based on engine type suitability
                if task_type == "analyze" and engine["type"] == "go":
                    score += 20  # Go is best for analysis
                elif task_type == "crack" and engine["type"] in ["rust", "cpp"]:
                    score += 15  # Rust/CPP are good for cracking
                elif task_type == "modify" and engine["type"] == "java":
                    score += 25  # Java is best for Android mods
                
                available_engines.append((name, score))
        
        if not available_engines:
            return None
        
        # Sort by score (highest first)
        available_engines.sort(key=lambda x: x[1], reverse=True)
        return available_engines[0][0]
    
    async def distribute_task(self, task: Task) -> Dict[str, Any]:
        """Distribute task to optimal engine"""
        engine_name = await self.select_engine(task.task_type)
        
        if not engine_name:
            return {"error": "No healthy engines available", "success": False}
        
        # Update engine load
        self.engines[engine_name]["current_load"] += 1
        await self.redis_client.hincrby(f"engine:{engine_name}", "current_load", 1)
        
        try:
            # Prepare payload
            payload = {
                "apk_path": task.apk_path,
                "category": task.category,
                "features": task.features,
                "task_id": task.task_id,
                "user_id": task.user_id
            }
            
            # Send to engine
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.engines[engine_name]['url']}/{task.task_type}", json=payload) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Update engine stats - success
                        stats = self.engine_stats[engine_name]
                        stats["requests_handled"] += 1
                        stats["success_count"] += 1
                        stats["total_response_time"] += response_time
                        stats["avg_response_time"] = stats["total_response_time"] / stats["requests_handled"]
                        stats["success_rate"] = stats["success_count"] / stats["requests_handled"]
                        
                        # Update Redis stats
                        await self.redis_client.hset(f"engine:{engine_name}", mapping={
                            "success_rate": stats["success_rate"],
                            "avg_response_time": stats["avg_response_time"]
                        })
                        
                        return {
                            "success": True,
                            "engine": engine_name,
                            "result": result,
                            "response_time": response_time
                        }
                    else:
                        error_text = await response.text()
                        
                        # Update engine stats - failure
                        stats = self.engine_stats[engine_name]
                        stats["requests_handled"] += 1
                        stats["error_count"] += 1
                        stats["success_rate"] = stats["success_count"] / stats["requests_handled"] if stats["requests_handled"] > 0 else 0
                        
                        return {
                            "success": False,
                            "engine": engine_name,
                            "error": f"Engine returned {response.status}: {error_text}",
                            "response_time": response_time
                        }
        
        except Exception as e:
            # Update engine stats - error
            stats = self.engine_stats[engine_name]
            stats["requests_handled"] += 1
            stats["error_count"] += 1
            stats["success_rate"] = stats["success_count"] / stats["requests_handled"] if stats["requests_handled"] > 0 else 0
            
            # Mark engine as unhealthy if too many errors
            if stats["error_count"] / stats["requests_handled"] > 0.5:  # 50% error rate
                self.engines[engine_name]["status"] = "unhealthy"
                await self.redis_client.hset(f"engine:{engine_name}", "status", "unhealthy")
            
            return {
                "success": False,
                "engine": engine_name,
                "error": str(e)
            }
        
        finally:
            # Always decrease load
            self.engines[engine_name]["current_load"] -= 1
            await self.redis_client.hincrby(f"engine:{engine_name}", "current_load", -1)
    
    async def health_check_loop(self):
        """Continuously check engine health"""
        while True:
            try:
                for engine_name, engine_info in self.engines.items():
                    healthy = await self.check_engine_health(engine_name, engine_info["url"])
                    
                    # Update status
                    self.engines[engine_name]["status"] = "healthy" if healthy else "unhealthy"
                    self.engines[engine_name]["last_health_check"] = datetime.now()
                    
                    await self.redis_client.hset(f"engine:{engine_name}", mapping={
                        "status": "healthy" if healthy else "unhealthy",
                        "last_health_check": datetime.now().isoformat()
                    })
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(5)
    
    async def check_engine_health(self, engine_name: str, url: str) -> bool:
        """Check if engine is healthy"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(f"{url}/health") as response:
                    return response.status == 200
        except:
            return False
    
    async def get_engine_stats(self, engine_name: str = None) -> Dict[str, Any]:
        """Get engine statistics"""
        if engine_name and engine_name in self.engine_stats:
            return {
                "engine": engine_name,
                **self.engine_stats[engine_name],
                "current_status": self.engines[engine_name]["status"],
                "current_load": self.engines[engine_name]["current_load"],
                "capacity": self.engines[engine_name]["capacity"]
            }
        elif engine_name:
            return {"error": f"Engine {engine_name} not found"}
        else:
            # Return all engine stats
            all_stats = {}
            for name in self.engines.keys():
                all_stats[name] = await self.get_engine_stats(name)
            return all_stats

# Global load balancer instance
load_balancer = LoadBalancer()

async def initialize_system():
    """Initialize the complete system"""
    await queue_manager.initialize()
    await load_balancer.initialize()
    logger.info("✅ Cyber Crack Pro system initialized!")

async def main():
    """Main function for testing queue and load balancer"""
    import sys
    
    await initialize_system()
    
    if len(sys.argv) < 2:
        print("Usage: python queue_manager.py <command> [options]")
        print("Commands: add-task, get-next, get-stats, health-check, distribute, cancel")
        return
    
    command = sys.argv[1]
    
    if command == "add-task":
        if len(sys.argv) < 4:
            print("Usage: python queue_manager.py add-task <apk_path> <category> [priority]")
            return
        
        task_data = {
            "apk_path": sys.argv[2],
            "category": sys.argv[3],
            "priority": sys.argv[4] if len(sys.argv) > 4 else "MEDIUM"
        }
        
        task_id = await queue_manager.add_task(task_data)
        print(f"Task added: {task_id}")
    
    elif command == "get-next":
        task = await queue_manager.get_next_task()
        if task:
            print(f"Next task: {task.task_id} - {task.category} (priority: {task.priority.name})")
        else:
            print("No tasks in queue")
    
    elif command == "get-stats":
        stats = await queue_manager.get_queue_stats()
        print(f"Queue stats: {stats}")
    
    elif command == "health-check":
        stats = await load_balancer.get_engine_stats()
        print("Engine health check:")
        for engine, stat in stats.items():
            if isinstance(stat, dict) and "error" not in stat:
                status = stat.get("current_status", "unknown")
                load = stat.get("current_load", 0)
                capacity = stat.get("capacity", 0)
                success_rate = stat.get("success_rate", 0)
                print(f"  {engine}: {status} (load: {load}/{capacity}, success: {success_rate:.2%})")
    
    elif command == "distribute":
        if len(sys.argv) < 3:
            print("Usage: python queue_manager.py distribute <task_id>")
            return
        
        task_id = sys.argv[2]
        task_data = await queue_manager.get_task_status(task_id)
        
        if not task_data:
            print(f"Task {task_id} not found")
            return
        
        # Create task object from data
        task = Task(
            task_id=task_id,
            user_id=task_data.get("user_id", "unknown"),
            task_type=task_data.get("task_type", "analyze"),
            apk_path=task_data.get("apk_path", ""),
            category=task_data.get("category", ""),
            features=task_data.get("features", []),
            priority=TaskPriority[task_data.get("priority", "MEDIUM")],
            created_at=datetime.now()
        )
        
        result = await load_balancer.distribute_task(task)
        print(f"Distribution result: {result}")
    
    elif command == "cancel":
        if len(sys.argv) < 3:
            print("Usage: python queue_manager.py cancel <task_id>")
            return
        
        task_id = sys.argv[2]
        success = await queue_manager.cancel_task(task_id)
        print(f"Task cancellation: {'SUCCESS' if success else 'FAILED'}")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    asyncio.run(main())