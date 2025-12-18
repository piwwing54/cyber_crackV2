#!/usr/bin/env python3
"""
🚦 CYBER CRACK PRO - Load Balancer
Load balancing system for distributing jobs across multiple processing engines
"""

import asyncio
import logging
import json
import os
import random
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import redis
import aiohttp
from asyncio import Queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class EngineInfo:
    """Information about a processing engine"""
    name: str
    url: str
    status: str  # 'active', 'inactive', 'overloaded'
    load: float  # 0.0 to 1.0
    capacity: int  # Max concurrent jobs
    current_jobs: int
    last_heartbeat: datetime
    supported_types: List[str]  # Job types this engine supports
    version: str
    region: str  # Geographic region

class LoadBalancer:
    """Distributed load balancer for processing engines"""
    
    def __init__(self):
        self.engines: Dict[str, EngineInfo] = {}
        self.redis_client = self._init_redis()
        self.job_queue = Queue()
        self.engine_stats = {}
        self.heartbeat_interval = int(os.getenv("HEARTBEAT_INTERVAL", "30"))
        self.health_check_interval = int(os.getenv("HEALTH_CHECK_INTERVAL", "10"))
        
    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection"""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            client = redis.from_url(redis_url, decode_responses=True)
            client.ping()
            logger.info("Successfully connected to Redis for load balancing")
            return client
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            return None
    
    def register_engine(self, 
                       name: str, 
                       url: str, 
                       capacity: int,
                       supported_types: List[str],
                       version: str = "1.0",
                       region: str = "default") -> bool:
        """Register a new processing engine"""
        engine_info = EngineInfo(
            name=name,
            url=url,
            status="active",
            load=0.0,
            capacity=capacity,
            current_jobs=0,
            last_heartbeat=datetime.now(),
            supported_types=supported_types,
            version=version,
            region=region
        )
        
        self.engines[name] = engine_info
        self.engine_stats[name] = {
            'requests': 0,
            'successes': 0,
            'failures': 0,
            'avg_response_time': 0.0,
            'total_response_time': 0.0
        }
        
        # Persist to Redis
        if self.redis_client:
            try:
                engine_data = {
                    'name': engine_info.name,
                    'url': engine_info.url,
                    'status': engine_info.status,
                    'load': engine_info.load,
                    'capacity': engine_info.capacity,
                    'current_jobs': engine_info.current_jobs,
                    'last_heartbeat': engine_info.last_heartbeat.isoformat(),
                    'supported_types': json.dumps(engine_info.supported_types),
                    'version': engine_info.version,
                    'region': engine_info.region
                }
                self.redis_client.hset("engines", name, json.dumps(engine_data))
                self.redis_client.sadd("engine_list", name)
            except Exception as e:
                logger.error(f"Failed to register engine in Redis: {e}")
        
        logger.info(f"Registered engine: {name} at {url}")
        return True
    
    def get_healthy_engines(self, job_type: str = None) -> List[EngineInfo]:
        """Get list of healthy engines, optionally filtered by job type"""
        healthy_engines = []
        
        for engine in self.engines.values():
            # Check if engine is active and not overloaded
            if (engine.status == "active" and 
                engine.load < 0.9 and  # Not overloaded
                engine.current_jobs < engine.capacity and
                (job_type is None or job_type in engine.supported_types)):
                healthy_engines.append(engine)
        
        return healthy_engines
    
    def select_engine_round_robin(self, job_type: str = None) -> Optional[EngineInfo]:
        """Select engine using round-robin algorithm"""
        healthy_engines = self.get_healthy_engines(job_type)
        if not healthy_engines:
            return None
        
        # Simple round-robin: sort by name and pick next one
        # In a real system, we'd track the last selected engine
        healthy_engines.sort(key=lambda x: x.name)
        return healthy_engines[0]
    
    def select_engine_least_loaded(self, job_type: str = None) -> Optional[EngineInfo]:
        """Select engine with the least current load"""
        healthy_engines = self.get_healthy_engines(job_type)
        if not healthy_engines:
            return None
        
        # Find engine with minimum load
        return min(healthy_engines, key=lambda e: e.current_jobs / e.capacity)
    
    def select_engine_random(self, job_type: str = None) -> Optional[EngineInfo]:
        """Select engine randomly"""
        healthy_engines = self.get_healthy_engines(job_type)
        if not healthy_engines:
            return None
        
        return random.choice(healthy_engines)
    
    def select_engine_weighted_random(self, job_type: str = None) -> Optional[EngineInfo]:
        """Select engine using weighted random based on remaining capacity"""
        healthy_engines = self.get_healthy_engines(job_type)
        if not healthy_engines:
            return None
        
        # Calculate weights based on remaining capacity (higher capacity = higher weight)
        total_remaining = sum(engine.capacity - engine.current_jobs for engine in healthy_engines)
        
        if total_remaining <= 0:
            # All engines are at capacity, return the one with most capacity
            return max(healthy_engines, key=lambda e: e.capacity - e.current_jobs)
        
        # Calculate weighted probabilities
        weights = []
        for engine in healthy_engines:
            remaining_capacity = engine.capacity - engine.current_jobs
            weight = max(remaining_capacity / total_remaining, 0.01)  # Minimum 1% weight
            weights.append(weight)
        
        # Select using weighted random choice
        import random
        selected_engine = random.choices(healthy_engines, weights=weights)[0]
        return selected_engine
    
    def select_engine(self, job_type: str = None, algorithm: str = "least_loaded") -> Optional[EngineInfo]:
        """Select an engine using specified algorithm"""
        if algorithm == "round_robin":
            return self.select_engine_round_robin(job_type)
        elif algorithm == "least_loaded":
            return self.select_engine_least_loaded(job_type)
        elif algorithm == "random":
            return self.select_engine_random(job_type)
        elif algorithm == "weighted_random":
            return self.select_engine_weighted_random(job_type)
        else:
            # Default to least loaded
            return self.select_engine_least_loaded(job_type)
    
    def assign_job_to_engine(self, job_data: Dict, engine: EngineInfo) -> str:
        """Assign a job to a specific engine"""
        # Update engine load
        engine.current_jobs += 1
        engine.load = engine.current_jobs / engine.capacity
        
        # Update stats
        self.engine_stats[engine.name]['requests'] += 1
        
        # This would actually send the job to the engine
        # For simulation, we'll just return a job ID
        job_id = f"lb_job_{int(time.time())}_{engine.name}"
        
        logger.info(f"Assigned job {job_id} to engine {engine.name}")
        return job_id
    
    async def send_job_to_engine(self, job_data: Dict, engine: EngineInfo) -> Tuple[bool, Dict]:
        """Send job to the selected engine"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                # Send job to engine
                async with session.post(
                    f"{engine.url}/process",
                    json=job_data,
                    timeout=aiohttp.ClientTimeout(total=300)  # 5 minute timeout
                ) as response:
                    result = await response.json()
                    success = response.status == 200
                    
                    response_time = time.time() - start_time
                    
                    # Update engine stats
                    stats = self.engine_stats[engine.name]
                    stats['total_response_time'] += response_time
                    stats['avg_response_time'] = stats['total_response_time'] / stats['requests']
                    
                    if success:
                        stats['successes'] += 1
                        logger.info(f"Job completed successfully on {engine.name}")
                    else:
                        stats['failures'] += 1
                        logger.warning(f"Job failed on {engine.name}: {response.status}")
                    
                    return success, result
                    
        except asyncio.TimeoutError:
            logger.error(f"Engine {engine.name} timed out")
            self.engine_stats[engine.name]['failures'] += 1
            # Mark engine as potentially unhealthy
            engine.status = "overloaded"
            return False, {"error": "Engine timeout"}
            
        except Exception as e:
            logger.error(f"Error sending job to engine {engine.name}: {e}")
            self.engine_stats[engine.name]['failures'] += 1
            return False, {"error": str(e)}
    
    def update_engine_load(self, engine_name: str, completed: bool = True):
        """Update engine load after job completion"""
        if engine_name in self.engines:
            engine = self.engines[engine_name]
            if completed:
                engine.current_jobs = max(0, engine.current_jobs - 1)
            engine.load = engine.current_jobs / engine.capacity if engine.capacity > 0 else 0
            
            # If this was a failure, consider marking the engine as unhealthy
            if not completed:
                self.engine_stats[engine_name]['failures'] += 1
                # If failure rate is too high, mark as inactive
                stats = self.engine_stats[engine_name]
                total_requests = stats['requests']
                if total_requests > 10:  # Only consider after 10 requests
                    failure_rate = stats['failures'] / total_requests
                    if failure_rate > 0.5:  # 50% failure rate
                        engine.status = "inactive"
                        logger.warning(f"Engine {engine_name} marked as inactive due to high failure rate: {failure_rate:.2%}")
    
    async def health_check_engine(self, engine_name: str) -> bool:
        """Perform health check on an engine"""
        if engine_name not in self.engines:
            return False
        
        engine = self.engines[engine_name]
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(f"{engine.url}/health") as response:
                    is_healthy = response.status == 200
                    
                    if is_healthy:
                        engine.status = "active"
                        engine.last_heartbeat = datetime.now()
                        # Calculate load based on current jobs vs capacity
                        engine.load = engine.current_jobs / engine.capacity if engine.capacity > 0 else 0
                    else:
                        engine.status = "inactive"
                    
                    return is_healthy
        except Exception as e:
            logger.warning(f"Health check failed for engine {engine_name}: {e}")
            engine.status = "inactive"
            return False
    
    async def periodic_health_check(self):
        """Periodically check health of all engines"""
        while True:
            try:
                for engine_name in list(self.engines.keys()):
                    await self.health_check_engine(engine_name)
                
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    async def heartbeat_monitor(self):
        """Monitor engine heartbeats and mark inactive engines"""
        while True:
            try:
                current_time = datetime.now()
                cutoff_time = current_time - timedelta(seconds=self.heartbeat_interval * 2)
                
                for engine_name, engine in self.engines.items():
                    if engine.last_heartbeat < cutoff_time and engine.status == "active":
                        logger.warning(f"Engine {engine_name} appears to be down (no heartbeat)")
                        engine.status = "inactive"
                
                await asyncio.sleep(self.heartbeat_interval)
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")
                await asyncio.sleep(self.heartbeat_interval)
    
    def get_engine_stats(self, engine_name: str = None) -> Dict:
        """Get statistics for engines"""
        if engine_name:
            if engine_name in self.engine_stats and engine_name in self.engines:
                stats = self.engine_stats[engine_name].copy()
                stats['engine_info'] = self.engines[engine_name]
                return stats
            else:
                return {"error": f"Engine {engine_name} not found"}
        else:
            # Return stats for all engines
            all_stats = {}
            for name in self.engines.keys():
                all_stats[name] = self.get_engine_stats(name)
            return all_stats
    
    def get_load_distribution(self) -> Dict[str, float]:
        """Get load distribution across all engines"""
        distribution = {}
        for name, engine in self.engines.items():
            distribution[name] = engine.load
        return distribution
    
    def rebalance_workload(self) -> Dict[str, Any]:
        """Suggest workload rebalancing based on current loads"""
        rebalancing_suggestions = {}
        
        active_engines = [e for e in self.engines.values() if e.status == "active"]
        if not active_engines:
            return {"message": "No active engines"}
        
        avg_load = sum(e.load for e in active_engines) / len(active_engines)
        
        for engine in active_engines:
            if engine.load > avg_load * 1.5:  # 150% of average
                rebalancing_suggestions[engine.name] = {
                    "status": "overloaded",
                    "current_load": engine.load,
                    "suggested_action": "reduce job assignment"
                }
            elif engine.load < avg_load * 0.5:  # 50% of average
                rebalancing_suggestions[engine.name] = {
                    "status": "underutilized",
                    "current_load": engine.load,
                    "suggested_action": "increase job assignment"
                }
        
        return rebalancing_suggestions

# Global instance
load_balancer = LoadBalancer()

async def main():
    """Main function for testing load balancer"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python load_balancer.py <command> [options]")
        print("Commands:")
        print("  register <name> <url> <capacity> <types> - Register an engine")
        print("  list-engines                      - List all registered engines")
        print("  select <job_type> [algorithm]     - Select an engine for job type")
        print("  stats [engine_name]              - Get engine statistics")
        print("  load-distribution                 - Get load distribution")
        print("  rebalance                         - Get rebalancing suggestions")
        print("  health-check [engine_name]        - Perform health check")
        print("  start-health-checks               - Start periodic health checks")
        return
    
    command = sys.argv[1]
    
    if command == "register":
        if len(sys.argv) < 5:
            print("Usage: python load_balancer.py register <name> <url> <capacity> <types_comma_separated>")
            return
        
        name = sys.argv[2]
        url = sys.argv[3]
        capacity = int(sys.argv[4])
        types = sys.argv[5].split(',') if len(sys.argv) > 5 else ["analyze", "process", "crack"]
        
        result = load_balancer.register_engine(name, url, capacity, types)
        print(f"Register engine: {'SUCCESS' if result else 'FAILED'}")
    
    elif command == "list-engines":
        print("Registered Engines:")
        for name, engine in load_balancer.engines.items():
            print(f"  - {name}: {engine.url} (status: {engine.status}, load: {engine.load:.2f}, capacity: {engine.capacity})")
    
    elif command == "select":
        if len(sys.argv) < 3:
            print("Usage: python load_balancer.py select <job_type> [algorithm]")
            return
        
        job_type = sys.argv[2]
        algorithm = sys.argv[3] if len(sys.argv) > 3 else "least_loaded"
        
        engine = load_balancer.select_engine(job_type, algorithm)
        if engine:
            print(f"Selected engine: {engine.name} (load: {engine.load:.2f})")
        else:
            print("No suitable engine found")
    
    elif command == "stats":
        engine_name = sys.argv[2] if len(sys.argv) > 2 else None
        stats = load_balancer.get_engine_stats(engine_name)
        print(f"Engine stats: {json.dumps(stats, indent=2, default=str)}")
    
    elif command == "load-distribution":
        distribution = load_balancer.get_load_distribution()
        print("Load Distribution:")
        for engine, load in distribution.items():
            print(f"  {engine}: {load:.2f}")
    
    elif command == "rebalance":
        suggestions = load_balancer.rebalance_workload()
        print("Rebalancing Suggestions:")
        for engine, suggestion in suggestions.items():
            print(f"  {engine}: {suggestion['status']} - {suggestion['suggested_action']}")
    
    elif command == "health-check":
        engine_name = sys.argv[2] if len(sys.argv) > 2 else None
        if engine_name:
            result = await load_balancer.health_check_engine(engine_name)
            print(f"Health check for {engine_name}: {'HEALTHY' if result else 'UNHEALTHY'}")
        else:
            # Check all engines
            tasks = []
            for name in load_balancer.engines.keys():
                tasks.append(load_balancer.health_check_engine(name))
            
            results = await asyncio.gather(*tasks)
            for name, result in zip(load_balancer.engines.keys(), results):
                print(f"  {name}: {'HEALTHY' if result else 'UNHEALTHY'}")
    
    elif command == "start-health-checks":
        print("Starting periodic health checks...")
        await load_balancer.periodic_health_check()
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    asyncio.run(main())