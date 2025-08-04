"""
Redis Caching Service
Multi-tier caching with intelligent invalidation and performance monitoring.
"""

import json
import time
import hashlib
from typing import Any, Optional, Dict, List, Union
from functools import wraps
import redis.asyncio as redis
from fastapi import Request

from core.config import settings


class RedisCacheService:
    """Multi-tier Redis caching service with intelligent invalidation."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.aioredis_client: Optional[redis.Redis] = None
        self.cache_stats: Dict[str, Any] = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }
        self.cache_layers = {
            "query": "query_cache",
            "object": "object_cache", 
            "api": "api_cache",
            "session": "session_cache"
        }
    
    async def initialize(self):
        """Initialize Redis connections."""
        try:
            self.redis_client = redis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                encoding="utf-8",
                decode_responses=True,
                db=settings.REDIS_DB
            )
            
            self.aioredis_client = redis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                encoding="utf-8",
                decode_responses=True,
                db=settings.REDIS_DB
            )
            
            # Test connection
            await self.redis_client.ping()
            print("Redis connection established successfully")
            
        except Exception as e:
            print(f"Failed to initialize Redis: {e}")
            self.redis_client = None
            self.aioredis_client = None
    
    def _generate_cache_key(self, layer: str, key: str, **kwargs) -> str:
        """Generate a cache key with layer prefix."""
        # Create a hash of additional parameters
        param_hash = hashlib.md5(json.dumps(kwargs, sort_keys=True).encode()).hexdigest()[:8]
        return f"{layer}:{key}:{param_hash}"
    
    async def get(self, layer: str, key: str, **kwargs) -> Optional[Any]:
        """Get value from cache layer."""
        if not self.redis_client:
            return None
        
        try:
            cache_key = self._generate_cache_key(layer, key, **kwargs)
            value = await self.redis_client.get(cache_key)
            
            if value:
                self.cache_stats["hits"] += 1
                return json.loads(value)
            else:
                self.cache_stats["misses"] += 1
                return None
                
        except Exception as e:
            self.cache_stats["errors"] += 1
            print(f"Cache get error: {e}")
            return None
    
    async def set(self, layer: str, key: str, value: Any, ttl: int = None, **kwargs):
        """Set value in cache layer."""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_cache_key(layer, key, **kwargs)
            serialized_value = json.dumps(value)
            
            if ttl is None:
                ttl = settings.REDIS_CACHE_EXPIRE_SECONDS
            
            await self.redis_client.setex(cache_key, ttl, serialized_value)
            self.cache_stats["sets"] += 1
            return True
            
        except Exception as e:
            self.cache_stats["errors"] += 1
            print(f"Cache set error: {e}")
            return False
    
    async def delete(self, layer: str, key: str, **kwargs):
        """Delete value from cache layer."""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_cache_key(layer, key, **kwargs)
            await self.redis_client.delete(cache_key)
            self.cache_stats["deletes"] += 1
            return True
            
        except Exception as e:
            self.cache_stats["errors"] += 1
            print(f"Cache delete error: {e}")
            return False
    
    async def invalidate_pattern(self, layer: str, pattern: str):
        """Invalidate all keys matching pattern in layer."""
        if not self.redis_client:
            return False
        
        try:
            search_pattern = f"{layer}:{pattern}*"
            keys = await self.redis_client.keys(search_pattern)
            
            if keys:
                await self.redis_client.delete(*keys)
                self.cache_stats["deletes"] += len(keys)
            
            return True
            
        except Exception as e:
            self.cache_stats["errors"] += 1
            print(f"Cache invalidate pattern error: {e}")
            return False
    
    async def clear_layer(self, layer: str):
        """Clear entire cache layer."""
        if not self.redis_client:
            return False
        
        try:
            search_pattern = f"{layer}:*"
            keys = await self.redis_client.keys(search_pattern)
            
            if keys:
                await self.redis_client.delete(*keys)
                self.cache_stats["deletes"] += len(keys)
            
            return True
            
        except Exception as e:
            self.cache_stats["errors"] += 1
            print(f"Cache clear layer error: {e}")
            return False
    
    async def get_multi(self, layer: str, keys: List[str], **kwargs) -> Dict[str, Any]:
        """Get multiple values from cache layer."""
        if not self.redis_client:
            return {}
        
        try:
            cache_keys = [self._generate_cache_key(layer, key, **kwargs) for key in keys]
            values = await self.redis_client.mget(cache_keys)
            
            result = {}
            for key, value in zip(keys, values):
                if value:
                    result[key] = json.loads(value)
                    self.cache_stats["hits"] += 1
                else:
                    self.cache_stats["misses"] += 1
            
            return result
            
        except Exception as e:
            self.cache_stats["errors"] += 1
            print(f"Cache get_multi error: {e}")
            return {}
    
    async def set_multi(self, layer: str, data: Dict[str, Any], ttl: int = None, **kwargs):
        """Set multiple values in cache layer."""
        if not self.redis_client:
            return False
        
        try:
            pipeline = self.redis_client.pipeline()
            
            for key, value in data.items():
                cache_key = self._generate_cache_key(layer, key, **kwargs)
                serialized_value = json.dumps(value)
                
                if ttl is None:
                    ttl = settings.REDIS_CACHE_EXPIRE_SECONDS
                
                pipeline.setex(cache_key, ttl, serialized_value)
            
            await pipeline.execute()
            self.cache_stats["sets"] += len(data)
            return True
            
        except Exception as e:
            self.cache_stats["errors"] += 1
            print(f"Cache set_multi error: {e}")
            return False
    
    def cache_decorator(self, layer: str, ttl: int = None, key_func=None):
        """Decorator for caching function results."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    # Default key generation
                    key_parts = [func.__name__]
                    key_parts.extend([str(arg) for arg in args])
                    key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
                    cache_key = ":".join(key_parts)
                
                # Try to get from cache
                cached_result = await self.get(layer, cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                await self.set(layer, cache_key, result, ttl)
                
                return result
            return wrapper
        return decorator
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        hit_rate = 0
        if self.cache_stats["hits"] + self.cache_stats["misses"] > 0:
            hit_rate = self.cache_stats["hits"] / (self.cache_stats["hits"] + self.cache_stats["misses"])
        
        return {
            **self.cache_stats,
            "hit_rate": hit_rate,
            "total_operations": sum(self.cache_stats.values())
        }
    
    async def get_memory_usage(self) -> Dict[str, Any]:
        """Get Redis memory usage information."""
        if not self.redis_client:
            return {}
        
        try:
            info = await self.redis_client.info("memory")
            return {
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "used_memory_peak": info.get("used_memory_peak", 0),
                "used_memory_peak_human": info.get("used_memory_peak_human", "0B"),
                "used_memory_rss": info.get("used_memory_rss", 0),
                "used_memory_rss_human": info.get("used_memory_rss_human", "0B")
            }
        except Exception as e:
            print(f"Error getting memory usage: {e}")
            return {}
    
    async def optimize_cache(self) -> Dict[str, Any]:
        """Optimize cache performance."""
        try:
            optimizations = []
            
            # Check memory usage
            memory_usage = await self.get_memory_usage()
            used_memory = memory_usage.get("used_memory", 0)
            
            if used_memory > 100 * 1024 * 1024:  # 100MB
                optimizations.append("Consider increasing Redis memory limit")
            
            # Check hit rate
            stats = await self.get_cache_stats()
            hit_rate = stats.get("hit_rate", 0)
            
            if hit_rate < 0.5:
                optimizations.append("Low cache hit rate - consider adjusting TTL or cache keys")
            
            # Check error rate
            total_ops = stats.get("total_operations", 0)
            error_rate = stats.get("errors", 0) / total_ops if total_ops > 0 else 0
            
            if error_rate > 0.01:  # 1% error rate
                optimizations.append("High cache error rate - check Redis connection")
            
            return {
                "optimizations": optimizations,
                "memory_usage": memory_usage,
                "cache_stats": stats
            }
            
        except Exception as e:
            print(f"Error optimizing cache: {e}")
            return {"error": str(e)}
    
    async def warm_cache(self, layer: str, warmup_data: Dict[str, Any]):
        """Warm up cache with frequently accessed data."""
        try:
            await self.set_multi(layer, warmup_data)
            print(f"Cache warmed up for layer: {layer}")
            return True
        except Exception as e:
            print(f"Error warming cache: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check cache health."""
        try:
            if not self.redis_client:
                return {"status": "unhealthy", "error": "Redis not connected"}
            
            # Test connection
            await self.redis_client.ping()
            
            # Get basic stats
            stats = await self.get_cache_stats()
            memory = await self.get_memory_usage() # Corrected to call get_memory_usage directly
            
            return {
                "status": "healthy",
                "stats": stats,
                "memory": memory,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }


# Create singleton instance
redis_cache = RedisCacheService()


# Convenience functions for common cache operations
async def cache_query_result(key: str, result: Any, ttl: int = 3600):
    """Cache database query result."""
    return await redis_cache.set("query", key, result, ttl)

async def get_cached_query_result(key: str) -> Optional[Any]:
    """Get cached database query result."""
    return await redis_cache.get("query", key)

async def cache_api_response(key: str, response: Any, ttl: int = 1800):
    """Cache API response."""
    return await redis_cache.set("api", key, response, ttl)

async def get_cached_api_response(key: str) -> Optional[Any]:
    """Get cached API response."""
    return await redis_cache.get("api", key)

async def cache_user_session(user_id: str, session_data: Any, ttl: int = 7200):
    """Cache user session data."""
    return await redis_cache.set("session", f"user:{user_id}", session_data, ttl)

async def get_cached_user_session(user_id: str) -> Optional[Any]:
    """Get cached user session data."""
    return await redis_cache.get("session", f"user:{user_id}")

async def invalidate_user_cache(user_id: str):
    """Invalidate all cache entries for a user."""
    await redis_cache.invalidate_pattern("session", f"user:{user_id}")
    await redis_cache.invalidate_pattern("object", f"user:{user_id}")

async def invalidate_garden_cache(garden_id: str):
    """Invalidate all cache entries for a garden."""
    await redis_cache.invalidate_pattern("query", f"garden:{garden_id}")
    await redis_cache.invalidate_pattern("object", f"garden:{garden_id}")
    await redis_cache.invalidate_pattern("api", f"garden:{garden_id}")
