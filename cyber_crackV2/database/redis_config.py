#!/usr/bin/env python3
"""
📊 CYBER CRACK PRO - Redis Configuration
Redis configuration and connection manager for caching
"""

import redis
import logging
import os
from typing import Optional, Any, Dict
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RedisConfig:
    """Redis configuration and connection manager"""
    
    def __init__(self, 
                 host: str = None,
                 port: int = None,
                 password: str = None,
                 db: int = 0,
                 url: str = None):
        """
        Initialize Redis configuration
        If url is provided, it takes precedence over other parameters
        """
        self.host = host or os.getenv("REDIS_HOST", "localhost")
        self.port = port or int(os.getenv("REDIS_PORT", "6379"))
        self.password = password or os.getenv("REDIS_PASSWORD", None)
        self.db = db or int(os.getenv("REDIS_DB", "0"))
        self.url = url or os.getenv("REDIS_URL", None)
        
        # If URL is provided, parse it to get connection parameters
        if self.url:
            parsed = urlparse(self.url)
            if parsed.hostname:
                self.host = parsed.hostname
            if parsed.port:
                self.port = parsed.port
            if parsed.password:
                self.password = parsed.password
            if parsed.path and parsed.path != '/':
                self.db = int(parsed.path[1:])  # Remove leading '/'
        
        self.client = None
    
    def get_connection(self) -> redis.Redis:
        """Get Redis connection"""
        if self.client is None:
            try:
                self.client = redis.Redis(
                    host=self.host,
                    port=self.port,
                    password=self.password,
                    db=self.db,
                    decode_responses=True,  # Return string responses rather than bytes
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    health_check_interval=30
                )
                # Test connection
                self.client.ping()
                logger.info(f"Connected to Redis at {self.host}:{self.port}")
            except redis.ConnectionError as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error connecting to Redis: {e}")
                raise
        
        return self.client
    
    def test_connection(self) -> bool:
        """Test Redis connection"""
        try:
            client = self.get_connection()
            client.ping()
            return True
        except:
            return False
    
    def set_cache(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set a value in cache with expiration"""
        try:
            client = self.get_connection()
            result = client.setex(key, expire, value)
            return result
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    def get_cache(self, key: str) -> Optional[str]:
        """Get a value from cache"""
        try:
            client = self.get_connection()
            value = client.get(key)
            return value
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None
    
    def delete_cache(self, key: str) -> bool:
        """Delete a value from cache"""
        try:
            client = self.get_connection()
            result = client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False
    
    def clear_cache(self) -> bool:
        """Clear all keys in the current database"""
        try:
            client = self.get_connection()
            result = client.flushdb()
            return result
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    def get_keys(self, pattern: str = "*") -> list:
        """Get all keys matching a pattern"""
        try:
            client = self.get_connection()
            keys = client.keys(pattern)
            return keys
        except Exception as e:
            logger.error(f"Error getting keys: {e}")
            return []
    
    def set_json(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set a JSON value in cache"""
        import json
        try:
            client = self.get_connection()
            json_value = json.dumps(value)
            result = client.setex(key, expire, json_value)
            return result
        except Exception as e:
            logger.error(f"Error setting JSON cache: {e}")
            return False
    
    def get_json(self, key: str) -> Optional[Any]:
        """Get a JSON value from cache"""
        import json
        try:
            client = self.get_connection()
            value = client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting JSON from cache: {e}")
            return None

# Default shared instance
redis_config = RedisConfig()

# Common cache keys for the application
class CacheKeys:
    ANALYSIS_RESULTS = "analysis:results:{job_id}"
    PROCESSING_RESULTS = "processing:results:{job_id}"
    APK_METADATA = "apk:metadata:{hash}"
    USER_SESSION = "user:session:{user_id}"
    CRACK_PATTERN = "pattern:crack:{pattern_id}"
    ENGINE_STATUS = "engine:status:{engine_name}"
    TASK_QUEUE = "task:queue:{queue_name}"
    RATE_LIMIT = "rate:limit:{user_id}:{endpoint}"

def get_redis_client() -> redis.Redis:
    """Get the default Redis client"""
    return redis_config.get_connection()

def cache_analysis_result(job_id: str, result: Dict, expire: int = 7200) -> bool:
    """Cache analysis result"""
    key = CacheKeys.ANALYSIS_RESULTS.format(job_id=job_id)
    return redis_config.set_json(key, result, expire)

def get_cached_analysis(job_id: str) -> Optional[Dict]:
    """Get cached analysis result"""
    key = CacheKeys.ANALYSIS_RESULTS.format(job_id=job_id)
    return redis_config.get_json(key)

def cache_processing_result(job_id: str, result: Dict, expire: int = 7200) -> bool:
    """Cache processing result"""
    key = CacheKeys.PROCESSING_RESULTS.format(job_id=job_id)
    return redis_config.set_json(key, result, expire)

def get_cached_processing(job_id: str) -> Optional[Dict]:
    """Get cached processing result"""
    key = CacheKeys.PROCESSING_RESULTS.format(job_id=job_id)
    return redis_config.get_json(key)

def main():
    """Main function for testing Redis configuration"""
    import sys
    
    redis_cfg = RedisConfig()
    
    if len(sys.argv) < 2:
        print("Usage: python redis_config.py <command> [options]")
        print("Commands:")
        print("  test                           - Test Redis connection")
        print("  set <key> <value> [expire]     - Set a value in cache")
        print("  get <key>                      - Get a value from cache")
        print("  delete <key>                   - Delete a value from cache")
        print("  clear                          - Clear all cache")
        print("  keys [pattern]                 - Get keys matching pattern")
        return
    
    command = sys.argv[1]
    
    if command == "test":
        result = redis_cfg.test_connection()
        print(f"Connection test: {'SUCCESS' if result else 'FAILED'}")
    
    elif command == "set":
        if len(sys.argv) < 3:
            print("Please provide key and value")
            return
        
        key = sys.argv[2]
        value = sys.argv[3]
        expire = int(sys.argv[4]) if len(sys.argv) > 4 else 3600
        
        result = redis_cfg.set_cache(key, value, expire)
        print(f"Set operation: {'SUCCESS' if result else 'FAILED'}")
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("Please provide key")
            return
        
        key = sys.argv[2]
        result = redis_cfg.get_cache(key)
        print(f"Value: {result}")
    
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Please provide key")
            return
        
        key = sys.argv[2]
        result = redis_cfg.delete_cache(key)
        print(f"Delete operation: {'SUCCESS' if result else 'FAILED'}")
    
    elif command == "clear":
        result = redis_cfg.clear_cache()
        print(f"Clear operation: {'SUCCESS' if result else 'FAILED'}")
    
    elif command == "keys":
        pattern = sys.argv[2] if len(sys.argv) > 2 else "*"
        keys = redis_cfg.get_keys(pattern)
        print(f"Found {len(keys)} keys:")
        for key in keys:
            print(f"  - {key}")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()