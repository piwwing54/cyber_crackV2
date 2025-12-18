#!/usr/bin/env python3
"""
💾 CYBER CRACK PRO - Cache Manager  
Advanced caching system with Redis and PostgreSQL integration
"""

import asyncio
import logging
import json
import os
import hashlib
import pickle
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from pathlib import Path
import redis.asyncio as redis
import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool
from dataclasses import dataclass, asdict
import aioredis
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CacheType(Enum):
    RESULT_CACHE = "results"
    PATTERN_CACHE = "patterns" 
    ANALYSIS_CACHE = "analysis"
    APK_INFO_CACHE = "apk_info"
    TEMP_CACHE = "temp"
    SESSION_CACHE = "session"

@dataclass
class CacheEntry:
    """Represents a cache entry"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime] = None
    cache_type: CacheType = CacheType.RESULT_CACHE
    tags: List[str] = None
    size: int = 0
    hit_count: int = 0
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.size == 0:
            self.size = len(str(self.value).encode('utf-8'))

class CacheManager:
    """Advanced cache management system"""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = None
        self.postgres_pool = None
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evicted": 0,
            "current_size": 0,
            "max_size": int(os.getenv("CACHE_MAX_SIZE_MB", "1024")) * 1024 * 1024
        }
        
    async def initialize(self):
        """Initialize cache managers"""
        # Initialize Redis
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                encoding="utf-8"
            )
            await self.redis_client.ping()
            logger.info("✅ Redis cache connected")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            raise
        
        # Initialize PostgreSQL connection pool
        try:
            db_url = os.getenv("POSTGRES_URL", "postgresql://cracker:password @localhost:5432/cybercrackpro")
            # Parse PostgreSQL URL
            # This is a simplified URL parser - in production use proper library
            self.postgres_pool = ThreadedConnectionPool(1, 20, dsn=db_url)
            
            # Create cache table if not exists
            conn = self.postgres_pool.getconn()
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    id SERIAL PRIMARY KEY,
                    key TEXT UNIQUE NOT NULL,
                    value JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    cache_type VARCHAR(50),
                    tags TEXT[],
                    size INTEGER DEFAULT 0,
                    hit_count INTEGER DEFAULT 0
                );
                
                CREATE INDEX IF NOT EXISTS idx_cache_key ON cache_entries(key);
                CREATE INDEX IF NOT EXISTS idx_cache_type ON cache_entries(cache_type);
                CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache_entries(expires_at);
            """)
            
            conn.commit()
            self.postgres_pool.putconn(conn)
            
            logger.info("✅ PostgreSQL cache connected")
        except Exception as e:
            logger.error(f"❌ Failed to connect to PostgreSQL: {e}")
            # Continue without PostgreSQL cache if it fails
    
    async def get(self, key: str, cache_type: CacheType = CacheType.RESULT_CACHE) -> Optional[Any]:
        """Get value from cache (Redis first, then PostgreSQL)"""
        # Try Redis first (faster)
        if self.redis_client:
            try:
                value = await self.redis_client.get(key)
                if value:
                    # Try to deserialize as JSON first, then as pickle
                    try:
                        # Increment hit counter
                        await self.redis_client.incr(f"cache:hit:{key}")
                        await self.redis_client.expire(f"cache:hit:{key}", 86400)
                        
                        self.stats["hits"] += 1
                        
                        deserialized = json.loads(value)
                        if isinstance(deserialized, dict) and "___serialized___" in deserialized:
                            # This was pickled and JSON-encoded
                            return pickle.loads(base64.b64decode(deserialized["___serialized___"]))
                        return deserialized
                    except json.JSONDecodeError:
                        # Try pickle if JSON fails
                        try:
                            unpickled = pickle.loads(value.encode('latin1'))
                            await self.redis_client.incr(f"cache:hit:{key}")
                            self.stats["hits"] += 1
                            return unpickled
                        except:
                            self.stats["hits"] += 1
                            return value
            except Exception as e:
                logger.warning(f"Redis get error for {key}: {e}")
        
        # Fallback to PostgreSQL if Redis fails or not found
        if self.postgres_pool:
            try:
                conn = self.postgres_pool.getconn()
                cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                
                query = """
                    SELECT value, expires_at, hit_count 
                    FROM cache_entries 
                    WHERE key = %s AND (expires_at > NOW() OR expires_at IS NULL)
                """
                cursor.execute(query, (key,))
                result = cursor.fetchone()
                
                self.postgres_pool.putconn(conn)
                
                if result:
                    self.stats["hits"] += 1
                    await self._increment_hit_count(key)
                    return result["value"]
            except Exception as e:
                logger.warning(f"PostgreSQL get error for {key}: {e}")
        
        self.stats["misses"] += 1
        return None
    
    async def set(self, 
                 key: str, 
                 value: Any, 
                 expire: int = 3600, 
                 cache_type: CacheType = CacheType.RESULT_CACHE,
                 tags: List[str] = None) -> bool:
        """Set value in cache (both Redis and PostgreSQL)"""
        success = True
        tags = tags or []
        
        try:
            # Prepare value - serialize complex objects
            if isinstance(value, (dict, list, tuple, set)) or hasattr(value, '__dict__'):
                # Serialize with JSON first, fall back to pickle
                try:
                    json.dumps(value)  # Test if JSON serializable
                    serialized_value = json.dumps(value)
                except (TypeError, ValueError):
                    # Use pickle for complex objects
                    pickled = pickle.dumps(value)
                    serialized_value = json.dumps({
                        "___serialized___": base64.b64encode(pickled).decode('utf-8')
                    })
            else:
                serialized_value = str(value)
            
            # Set in Redis
            if self.redis_client:
                await self.redis_client.setex(key, expire, serialized_value)
                
                # Store metadata
                await self.redis_client.hset(f"cache:meta:{key}", mapping={
                    "type": cache_type.value,
                    "tags": json.dumps(tags),
                    "size": len(serialized_value.encode('utf-8')),
                    "created_at": datetime.now().isoformat(),
                    "expires_at": (datetime.now() + timedelta(seconds=expire)).isoformat()
                })
                await self.redis_client.expire(f"cache:meta:{key}", expire)
                
                # Update stats
                current_size = await self.redis_client.strlen(key)
                self.stats["current_size"] += current_size
                if self.stats["current_size"] > self.stats["max_size"]:
                    await self._evict_old_items()
            
            # Set in PostgreSQL (async)
            if self.postgres_pool:
                try:
                    conn = self.postgres_pool.getconn()
                    cursor = conn.cursor()
                    
                    query = """
                        INSERT INTO cache_entries (key, value, expires_at, cache_type, tags, size)
                        VALUES (%s, %s, NOW() + INTERVAL '%s seconds', %s, %s, %s)
                        ON CONFLICT (key) DO UPDATE SET
                            value = EXCLUDED.value,
                            expires_at = EXCLUDED.expires_at,
                            cache_type = EXCLUDED.cache_type,
                            tags = EXCLUDED.tags,
                            size = EXCLUDED.size,
                            hit_count = cache_entries.hit_count + 1
                    """
                    cursor.execute(query, (
                        key,
                        json.loads(serialized_value) if isinstance(json.loads(serialized_value), (dict, list)) else serialized_value,
                        expire,
                        cache_type.value,
                        tags,
                        len(serialized_value.encode('utf-8'))
                    ))
                    
                    conn.commit()
                    self.postgres_pool.putconn(conn)
                except Exception as e:
                    logger.warning(f"PostgreSQL set error: {e}")
                    # Don't fail if PostgreSQL fails
        
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            success = False
        
        return success
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache (both Redis and PostgreSQL)"""
        success = True
        
        # Delete from Redis
        if self.redis_client:
            try:
                deleted = await self.redis_client.delete(key)
                await self.redis_client.delete(f"cache:meta:{key}")
                await self.redis_client.delete(f"cache:hit:{key}")
                
                # Update size stats
                if deleted:
                    # Get the size of the deleted item to adjust current size
                    meta = await self.redis_client.hgetall(f"cache:meta:{key}")
                    if "size" in meta:
                        self.stats["current_size"] -= int(meta["size"])
            except Exception as e:
                logger.warning(f"Redis delete error: {e}")
                success = False
        
        # Delete from PostgreSQL
        if self.postgres_pool:
            try:
                conn = self.postgres_pool.getconn()
                cursor = conn.cursor()
                
                query = "DELETE FROM cache_entries WHERE key = %s"
                cursor.execute(query, (key,))
                
                conn.commit()
                self.postgres_pool.putconn(conn)
            except Exception as e:
                logger.warning(f"PostgreSQL delete error: {e}")
                # Don't fail if PostgreSQL fails
        
        return success
    
    async def clear(self, cache_type: Optional[CacheType] = None) -> bool:
        """Clear cache entries"""
        try:
            if cache_type:
                # Clear specific cache type
                pattern = f"cache:{cache_type.value}:*"
            else:
                # Clear all caches
                pattern = "*"
            
            # Clear Redis
            if self.redis_client:
                keys_to_delete = await self.redis_client.keys(pattern)
                if keys_to_delete:
                    await self.redis_client.delete(*keys_to_delete)
                    self.stats["current_size"] = 0
            
            # Clear PostgreSQL
            if self.postgres_pool:
                conn = self.postgres_pool.getconn()
                cursor = conn.cursor()
                
                if cache_type:
                    query = "DELETE FROM cache_entries WHERE cache_type = %s"
                    cursor.execute(query, (cache_type.value,))
                else:
                    cursor.execute("DELETE FROM cache_entries")
                
                conn.commit()
                self.postgres_pool.putconn(conn)
            
            logger.info(f"Cleared cache: {cache_type or 'all'}")
            return True
            
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        # Check Redis first
        if self.redis_client:
            try:
                exists = await self.redis_client.exists(key)
                return exists > 0
            except:
                pass
        
        # Check PostgreSQL
        if self.postgres_pool:
            try:
                conn = self.postgres_pool.getconn()
                cursor = conn.cursor()
                
                query = """
                    SELECT 1 FROM cache_entries 
                    WHERE key = %s AND (expires_at > NOW() OR expires_at IS NULL)
                    LIMIT 1
                """
                cursor.execute(query, (key,))
                result = cursor.fetchone()
                
                self.postgres_pool.putconn(conn)
                
                return result is not None
            except:
                pass
        
        return False
    
    async def get_keys_by_tag(self, tag: str) -> List[str]:
        """Get all keys with a specific tag"""
        keys = []
        
        # Get from Redis
        if self.redis_client:
            try:
                all_keys = await self.redis_client.keys("*")
                for key in all_keys:
                    if key.startswith("cache:meta:"):
                        continue  # Skip metadata keys
                    
                    meta = await self.redis_client.hgetall(f"cache:meta:{key}")
                    if meta and "tags" in meta:
                        try:
                            tags = json.loads(meta["tags"])
                            if tag in tags:
                                keys.append(key)
                        except:
                            continue
            except Exception as e:
                logger.warning(f"Error getting keys by tag from Redis: {e}")
        
        # Get from PostgreSQL
        if self.postgres_pool:
            try:
                conn = self.postgres_pool.getconn()
                cursor = conn.cursor()
                
                query = "SELECT key FROM cache_entries WHERE %s = ANY(tags) AND (expires_at > NOW() OR expires_at IS NULL)"
                cursor.execute(query, (tag,))
                result = cursor.fetchall()
                
                for row in result:
                    keys.append(row[0])
                
                self.postgres_pool.putconn(conn)
            except Exception as e:
                logger.warning(f"Error getting keys by tag from PostgreSQL: {e}")
        
        return keys
    
    async def get_keys_by_type(self, cache_type: CacheType) -> List[str]:
        """Get all keys of a specific type"""
        keys = []
        
        # From Redis
        if self.redis_client:
            try:
                all_keys = await self.redis_client.keys(f"cache:{cache_type.value}:*")
                keys.extend([k.split(":")[-1] for k in all_keys if ":" in k])  # Extract actual keys
            except Exception as e:
                logger.warning(f"Error getting keys by type from Redis: {e}")
        
        # From PostgreSQL
        if self.postgres_pool:
            try:
                conn = self.postgres_pool.getconn()
                cursor = conn.cursor()
                
                query = "SELECT key FROM cache_entries WHERE cache_type = %s AND (expires_at > NOW() OR expires_at IS NULL)"
                cursor.execute(query, (cache_type.value,))
                result = cursor.fetchall()
                
                for row in result:
                    keys.append(row[0])
                
                self.postgres_pool.putconn(conn)
            except Exception as e:
                logger.warning(f"Error getting keys by type from PostgreSQL: {e}")
        
        return keys
    
    async def _evict_old_items(self):
        """Evict old cache items to manage memory"""
        if not self.redis_client:
            return
        
        try:
            # Get all keys with metadata
            meta_keys = await self.redis_client.keys("cache:meta:*")
            
            # Get creation times and sort by oldest
            items = []
            for meta_key in meta_keys:
                key = meta_key.replace("cache:meta:", "")
                meta = await self.redis_client.hgetall(meta_key)
                if meta and "created_at" in meta:
                    created_at = datetime.fromisoformat(meta["created_at"])
                    size = int(meta.get("size", 0))
                    items.append((key, created_at, size))
            
            # Sort by creation time (oldest first)
            items.sort(key=lambda x: x[1])
            
            # Remove oldest items until size is within limit
            removed_size = 0
            for key, created_at, size in items:
                if self.stats["current_size"] - removed_size <= self.stats["max_size"] * 0.8:  # Keep at 80% capacity
                    break
                
                await self.redis_client.delete(key)
                await self.redis_client.delete(f"cache:meta:{key}")
                await self.redis_client.delete(f"cache:hit:{key}")
                
                removed_size += size
                self.stats["evicted"] += 1
            
            self.stats["current_size"] -= removed_size
            
        except Exception as e:
            logger.error(f"Error evicting old items: {e}")
    
    async def _increment_hit_count(self, key: str):
        """Increment hit counter"""
        if self.redis_client:
            try:
                await self.redis_client.incr(f"cache:hit:{key}")
                await self.redis_client.expire(f"cache:hit:{key}", 86400)
            except Exception as e:
                logger.warning(f"Error incrementing hit count: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = self.stats.copy()
        
        if self.redis_client:
            try:
                redis_info = await self.redis_client.info()
                stats.update({
                    "redis_connected": True,
                    "redis_memory_used": redis_info.get("used_memory_human", "N/A"),
                    "redis_keys_count": await self.redis_client.dbsize(),
                    "redis_uptime": redis_info.get("uptime_in_seconds", 0),
                })
            except Exception as e:
                stats["redis_connected"] = False
                logger.warning(f"Could not get Redis stats: {e}")
        
        if self.postgres_pool:
            try:
                conn = self.postgres_pool.getconn()
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM cache_entries")
                postgres_keys = cursor.fetchone()[0]
                
                cursor.execute("SELECT SUM(size) FROM cache_entries WHERE expires_at > NOW() OR expires_at IS NULL")
                postgres_size = cursor.fetchone()[0] or 0
                
                conn.commit()
                self.postgres_pool.putconn(conn)
                
                stats.update({
                    "postgres_connected": True,
                    "postgres_keys_count": postgres_keys,
                    "postgres_size_bytes": postgres_size,
                    "hit_rate": stats["hits"] / (stats["hits"] + stats["misses"]) if (stats["hits"] + stats["misses"]) > 0 else 0
                })
            except Exception as e:
                stats["postgres_connected"] = False
                logger.warning(f"Could not get PostgreSQL stats: {e}")
        
        stats["total_requests"] = stats["hits"] + stats["misses"]
        stats["hit_rate_percent"] = (stats["hits"] / stats["total_requests"] * 100) if stats["total_requests"] > 0 else 0
        
        return stats

class KnowledgeCache:
    """Specialized cache for knowledge base patterns"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.pattern_cache_key = "knowledge_patterns"
        self.crack_templates_cache_key = "crack_templates"
        self.vulnerability_cache_key = "vulnerabilities"
    
    async def get_crack_patterns(self, category: str = None) -> List[Dict]:
        """Get crack patterns from cache"""
        cache_key = f"{self.pattern_cache_key}:{category or 'all'}"
        
        cached_patterns = await self.cache_manager.get(cache_key, CacheType.PATTERN_CACHE)
        if cached_patterns:
            return cached_patterns
        
        # Load from knowledge base (this would normally come from brain/knowledge_base.json)
        # For now, return some default patterns
        patterns = self._load_default_patterns(category)
        
        # Cache for 1 hour
        await self.cache_manager.set(cache_key, patterns, expire=3600, cache_type=CacheType.PATTERN_CACHE)
        
        return patterns
    
    def _load_default_patterns(self, category: str = None) -> List[Dict]:
        """Load default crack patterns"""
        all_patterns = [
            {
                "name": "LOGIN_BYPASS_ALWAYS_TRUE",
                "pattern": "const/4 v0, 0x0",
                "replacement": "const/4 v0, 0x1",
                "category": "authentication",
                "risk": "LOW",
                "stability": "HIGH",
                "priority": 1
            },
            {
                "name": "IAP_VERIFY_ALWAYS_SUCCESS", 
                "pattern": "verifyPurchase.*Z",
                "replacement": "const/4 v0, 0x1\nreturn v0",
                "category": "inapp_purchase",
                "risk": "MEDIUM",
                "stability": "HIGH",
                "priority": 2
            },
            {
                "name": "ROOT_CHECK_RETURN_FALSE",
                "pattern": "isRooted.*Z", 
                "replacement": "const/4 v0, 0x0\nreturn v0",
                "category": "root_detection",
                "risk": "LOW",
                "stability": "HIGH",
                "priority": 1
            },
            {
                "name": "SSL_PINNING_TRUST_ALL",
                "pattern": "checkServerTrusted",
                "replacement": "return-void",
                "category": "ssl_pinning",
                "risk": "HIGH",
                "stability": "MEDIUM",
                "priority": 3
            },
            {
                "name": "ANTI_DEBUG_DISABLE",
                "pattern": "isDebuggerConnected",
                "replacement": "const/4 v0, 0x0",
                "category": "anti_debug",
                "risk": "MEDIUM",
                "stability": "HIGH",
                "priority": 2
            }
        ]
        
        if category:
            return [p for p in all_patterns if p["category"] == category]
        
        return all_patterns
    
    async def get_crack_templates(self, feature_type: str = None) -> Dict[str, Any]:
        """Get crack templates from cache"""
        cache_key = f"{self.crack_templates_cache_key}:{feature_type or 'all'}"
        
        cached_templates = await self.cache_manager.get(cache_key, CacheType.TEMPLATE_CACHE)
        if cached_templates:
            return cached_templates
        
        # Load default templates
        templates = self._load_default_templates(feature_type)
        
        # Cache for 2 hours
        await self.cache_manager.set(cache_key, templates, expire=7200, cache_type=CacheType.TEMPLATE_CACHE)
        
        return templates
    
    def _load_default_templates(self, feature_type: str = None) -> Dict[str, Any]:
        """Load default crack templates"""
        templates = {
            "login_bypass": {
                "name": "Login Bypass Template",
                "description": "Bypass login authentication",
                "smali_code": """
.method public static authenticate(Ljava/lang/String;Ljava/lang/String;)Z
    .locals 1
    .prologue
    
    # BYPASSED: Always return authenticated
    const/4 v0, 0x1
    return v0
.end method
                """,
                "requirements": ["authentication_bypass"],
                "risks": ["account_security"],
                "stability": 95
            },
            "iap_bypass": {
                "name": "In-App Purchase Bypass",
                "description": "Bypass in-app purchase verification",
                "smali_code": """
.method public static verifyPurchase(Ljava/lang/String;)Z
    .locals 1
    .prologue
    
    # BYPASSED: Always return purchase verified
    const/4 v0, 0x1
    return v0
.end method
                """,
                "requirements": ["billing_bypass"],
                "risks": ["payment_fraud"],
                "stability": 90
            },
            "premium_unlock": {
                "name": "Premium Feature Unlock",
                "description": "Unlock premium features",
                "smali_code": """
.method public static isPremium()Z
    .locals 1
    .prologue
    
    # BYPASSED: Always return premium
    const/4 v0, 0x1
    return v0
.end method
                """,
                "requirements": ["feature_unlock"],
                "risks": ["license_violation"],
                "stability": 98
            }
        }
        
        if feature_type:
            return {feature_type: templates.get(feature_type, {})}
        
        return templates

# Global cache instances
cache_manager = CacheManager()
knowledge_cache = None

async def initialize_cache_system():
    """Initialize the cache system"""
    global knowledge_cache
    await cache_manager.initialize()
    knowledge_cache = KnowledgeCache(cache_manager)
    logger.info("💾 Cache system initialized")

async def get_result_from_cache(job_id: str) -> Optional[Dict]:
    """Get processing result from cache"""
    cache_key = f"result:{job_id}"
    return await cache_manager.get(cache_key, CacheType.RESULT_CACHE)

async def cache_result(job_id: str, result: Dict, ttl: int = 7200) -> bool:
    """Cache processing result"""
    cache_key = f"result:{job_id}"
    return await cache_manager.set(cache_key, result, expire=ttl, cache_type=CacheType.RESULT_CACHE)

async def cache_analysis_result(apk_hash: str, analysis: Dict, ttl: int = 3600) -> bool:
    """Cache APK analysis result"""
    cache_key = f"analysis:{apk_hash}"
    return await cache_manager.set(cache_key, analysis, expire=ttl, cache_type=CacheType.ANALYSIS_CACHE)

async def get_analysis_from_cache(apk_hash: str) -> Optional[Dict]:
    """Get APK analysis from cache"""
    cache_key = f"analysis:{apk_hash}"
    return await cache_manager.get(cache_key, CacheType.ANALYSIS_CACHE)

async def cache_apk_info(apk_hash: str, info: Dict, ttl: int = 86400) -> bool:
    """Cache APK information"""
    cache_key = f"apk_info:{apk_hash}"
    return await cache_manager.set(cache_key, info, expire=ttl, cache_type=CacheType.APK_INFO_CACHE)

async def get_apk_info_from_cache(apk_hash: str) -> Optional[Dict]:
    """Get APK information from cache"""
    cache_key = f"apk_info:{apk_hash}"
    return await cache_manager.get(cache_key, CacheType.APK_INFO_CACHE)

async def cache_pattern_match(pattern_id: str, result: Dict, ttl: int = 1800) -> bool:
    """Cache pattern matching result"""
    cache_key = f"pattern_match:{pattern_id}"
    return await cache_manager.set(cache_key, result, expire=ttl, cache_type=CacheType.PATTERN_CACHE)

async def get_pattern_match_from_cache(pattern_id: str) -> Optional[Dict]:
    """Get pattern matching result from cache"""
    cache_key = f"pattern_match:{pattern_id}"
    return await cache_manager.get(cache_key, CacheType.PATTERN_CACHE)

async def main():
    """Main function for testing cache system"""
    import sys
    
    await initialize_cache_system()
    
    if len(sys.argv) < 2:
        print("Usage: python cache_manager.py <command> [options]")
        print("Commands: test, set, get, delete, stats, clear")
        return
    
    command = sys.argv[1]
    
    if command == "test":
        # Test basic operations
        print("Testing cache operations...")
        
        # Test set
        success = await cache_manager.set("test_key", {"data": "test_value", "timestamp": time.time()}, expire=60)
        print(f"Set operation: {'SUCCESS' if success else 'FAILED'}")
        
        # Test get
        value = await cache_manager.get("test_key")
        print(f"Get operation: {value}")
        
        # Test exists
        exists = await cache_manager.exists("test_key")
        print(f"Exists operation: {'EXISTS' if exists else 'NOT EXISTS'}")
        
        # Test stats
        stats = await cache_manager.get_stats()
        print(f"Cache stats: {stats}")
        
    elif command == "set":
        if len(sys.argv) < 4:
            print("Usage: python cache_manager.py set <key> <value> [expire]")
            return
        
        key = sys.argv[2]
        value = sys.argv[3]
        expire = int(sys.argv[4]) if len(sys.argv) > 4 else 3600
        
        try:
            # Try to parse as JSON if possible
            value_obj = json.loads(value)
        except:
            value_obj = value
        
        success = await cache_manager.set(key, value_obj, expire=expire)
        print(f"Set operation: {'SUCCESS' if success else 'FAILED'}")
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("Usage: python cache_manager.py get <key>")
            return
        
        key = sys.argv[2]
        value = await cache_manager.get(key)
        print(f"Value: {value}")
    
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Usage: python cache_manager.py delete <key>")
            return
        
        key = sys.argv[2]
        success = await cache_manager.delete(key)
        print(f"Delete operation: {'SUCCESS' if success else 'FAILED'}")
    
    elif command == "stats":
        stats = await cache_manager.get_stats()
        print(json.dumps(stats, indent=2, default=str))
    
    elif command == "clear":
        cache_type = sys.argv[2] if len(sys.argv) > 2 else None
        cache_type_enum = CacheType(cache_type) if cache_type else None
        success = await cache_manager.clear(cache_type=cache_type_enum)
        print(f"Clear operation: {'SUCCESS' if success else 'FAILED'}")
    
    elif command == "knowledge":
        # Test knowledge cache
        patterns = await knowledge_cache.get_crack_patterns()
        print(f"Loaded {len(patterns)} crack patterns")
        
        templates = await knowledge_cache.get_crack_templates()
        print(f"Loaded {len(templates)} crack templates")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    asyncio.run(main())