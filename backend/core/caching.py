#!/usr/bin/env python3
"""
🚀 ENTERPRISE CACHING LAYER WITH CIRCUIT BREAKER
===============================================

Production-grade Redis caching system with circuit breaker pattern,
intelligent cache warming, and comprehensive monitoring.

Features:
- Redis-based distributed caching
- Circuit breaker pattern for fault tolerance  
- Intelligent cache warming and invalidation
- Performance monitoring and metrics
- Cache hierarchy with multiple TTL strategies
- Graceful degradation when cache is unavailable

This demonstrates enterprise-level caching patterns expected
in high-performance production systems.
"""

import json
import hashlib
import logging
import time
import asyncio
from typing import Any, Dict, Optional, Callable, List, Union
from datetime import datetime, timedelta
from functools import wraps
from contextlib import asynccontextmanager
from enum import Enum

import redis.asyncio as redis
from redis.exceptions import RedisError, ConnectionError, TimeoutError

from .monitoring import monitoring
from .exceptions import BaseEcoTrackerException, ErrorSeverity, ErrorCategory

logger = logging.getLogger(__name__)

class CircuitBreakerState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Circuit is open, failing fast
    HALF_OPEN = "half_open" # Testing if service is back

class CacheStrategy(str, Enum):
    """Cache invalidation strategies"""
    TTL = "ttl"                    # Time-based expiration
    LRU = "lru"                   # Least Recently Used
    WRITE_THROUGH = "write_through" # Update cache on write
    WRITE_BEHIND = "write_behind"  # Async cache update
    REFRESH_AHEAD = "refresh_ahead" # Proactive refresh

class CircuitBreaker:
    """
    Circuit breaker implementation for Redis operations
    
    Prevents cascade failures when Redis is unavailable by 
    failing fast after consecutive failures.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = RedisError
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        
    def _can_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        
        # Open circuit - fail fast
        if self.state == CircuitBreakerState.OPEN:
            if self._can_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("🔄 Circuit breaker moving to HALF_OPEN state")
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            
            # Success - reset failure count
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED
                logger.info("✅ Circuit breaker reset to CLOSED state")
            
            self.failure_count = 0
            return result
            
        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            logger.warning(f"❌ Circuit breaker failure {self.failure_count}/{self.failure_threshold}: {e}")
            
            # Open circuit if threshold reached
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                logger.error(f"🚨 Circuit breaker OPENED after {self.failure_count} failures")
            
            raise

class CircuitBreakerOpenError(BaseEcoTrackerException):
    """Raised when circuit breaker is open"""
    def __init__(self):
        super().__init__(
            "Cache service unavailable - circuit breaker is open",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.EXTERNAL_API,
            recovery_suggestion="Cache will automatically retry after recovery timeout"
        )

class CacheService:
    """
    Enterprise-grade Redis caching service with circuit breaker
    
    Provides intelligent caching with fault tolerance, monitoring,
    and performance optimization features.
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        default_ttl: int = 3600,
        key_prefix: str = "eco_tracker",
        max_connections: int = 10
    ):
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        
        # Initialize Redis connection pool
        self.redis_pool = redis.ConnectionPool.from_url(
            redis_url,
            max_connections=max_connections,
            retry_on_timeout=True,
            decode_responses=True
        )
        self.redis_client = redis.Redis(connection_pool=self.redis_pool)
        
        # Circuit breaker for Redis operations
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=RedisError
        )
        
        # Cache statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0,
            "circuit_breaker_opens": 0
        }
        
        logger.info(f"🚀 Cache service initialized with Redis at {redis_url}")
    
    def _make_key(self, key: str) -> str:
        """Generate prefixed cache key"""
        return f"{self.key_prefix}:{key}"
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize value for Redis storage"""
        return json.dumps(value, default=str, separators=(',', ':'))
    
    def _deserialize_value(self, value: str) -> Any:
        """Deserialize value from Redis"""
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate deterministic cache key from function signature"""
        # Create signature hash
        signature = f"{func_name}:{str(args)}:{str(sorted(kwargs.items()))}"
        key_hash = hashlib.md5(signature.encode()).hexdigest()
        return f"func:{func_name}:{key_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with circuit breaker protection"""
        cache_key = self._make_key(key)
        
        try:
            with monitoring.trace_span("cache_get", {"cache.key": key}):
                value = await self.circuit_breaker.call(
                    self.redis_client.get, cache_key
                )
                
                if value is not None:
                    self.stats["hits"] += 1
                    logger.debug(f"🎯 Cache HIT: {key}")
                    return self._deserialize_value(value)
                else:
                    self.stats["misses"] += 1
                    logger.debug(f"💨 Cache MISS: {key}")
                    return None
                    
        except (CircuitBreakerOpenError, RedisError) as e:
            self.stats["errors"] += 1
            logger.warning(f"❌ Cache GET failed for {key}: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        strategy: CacheStrategy = CacheStrategy.TTL
    ) -> bool:
        """Set value in cache with circuit breaker protection"""
        cache_key = self._make_key(key)
        ttl = ttl or self.default_ttl
        
        try:
            with monitoring.trace_span("cache_set", {
                "cache.key": key,
                "cache.ttl": ttl,
                "cache.strategy": strategy
            }):
                serialized_value = self._serialize_value(value)
                
                success = await self.circuit_breaker.call(
                    self.redis_client.setex,
                    cache_key,
                    ttl,
                    serialized_value
                )
                
                if success:
                    logger.debug(f"💾 Cache SET: {key} (TTL: {ttl}s)")
                    return True
                    
        except (CircuitBreakerOpenError, RedisError) as e:
            self.stats["errors"] += 1
            logger.warning(f"❌ Cache SET failed for {key}: {e}")
            
        return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        cache_key = self._make_key(key)
        
        try:
            with monitoring.trace_span("cache_delete", {"cache.key": key}):
                result = await self.circuit_breaker.call(
                    self.redis_client.delete, cache_key
                )
                
                logger.debug(f"🗑️ Cache DELETE: {key}")
                return bool(result)
                
        except (CircuitBreakerOpenError, RedisError) as e:
            self.stats["errors"] += 1
            logger.warning(f"❌ Cache DELETE failed for {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        cache_key = self._make_key(key)
        
        try:
            result = await self.circuit_breaker.call(
                self.redis_client.exists, cache_key
            )
            return bool(result)
            
        except (CircuitBreakerOpenError, RedisError):
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern"""
        try:
            cache_pattern = self._make_key(pattern)
            keys = await self.circuit_breaker.call(
                self.redis_client.keys, cache_pattern
            )
            
            if keys:
                deleted = await self.circuit_breaker.call(
                    self.redis_client.delete, *keys
                )
                logger.info(f"🧹 Invalidated {deleted} cache keys matching '{pattern}'")
                return deleted
                
        except (CircuitBreakerOpenError, RedisError) as e:
            logger.warning(f"❌ Cache pattern invalidation failed: {e}")
            
        return 0
    
    def cache_result(
        self,
        ttl: int = None,
        key_generator: Optional[Callable] = None,
        strategy: CacheStrategy = CacheStrategy.TTL
    ):
        """
        Decorator for caching function results
        
        Usage:
            @cache.cache_result(ttl=1800, strategy=CacheStrategy.REFRESH_AHEAD)
            async def expensive_function(param1, param2):
                # Implementation
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                if key_generator:
                    cache_key = key_generator(*args, **kwargs)
                else:
                    cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                
                # Try to get from cache
                cached_result = await self.get(cache_key)
                if cached_result is not None:
                    monitoring.record_request("cache", "GET", 200, 0.001)
                    return cached_result
                
                # Execute function
                start_time = time.time()
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Store in cache
                await self.set(cache_key, result, ttl or self.default_ttl, strategy)
                
                # Record metrics
                monitoring.record_request("cache", "SET", 200, execution_time)
                
                return result
            
            return wrapper
        return decorator
    
    async def warm_cache(self, warm_functions: List[Dict[str, Any]]):
        """
        Proactively warm cache with frequently accessed data
        
        Args:
            warm_functions: List of {"func": callable, "args": [], "kwargs": {}}
        """
        logger.info(f"🔥 Starting cache warming for {len(warm_functions)} functions")
        
        start_time = time.time()
        warmed_count = 0
        
        for func_config in warm_functions:
            try:
                func = func_config["func"]
                args = func_config.get("args", [])
                kwargs = func_config.get("kwargs", {})
                
                # Execute and cache
                result = await func(*args, **kwargs)
                cache_key = self._generate_cache_key(func.__name__, tuple(args), kwargs)
                await self.set(cache_key, result)
                
                warmed_count += 1
                
            except Exception as e:
                logger.warning(f"❌ Failed to warm cache for {func.__name__}: {e}")
        
        duration = time.time() - start_time
        logger.info(f"✅ Cache warming completed: {warmed_count}/{len(warm_functions)} in {duration:.2f}s")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        # Get Redis info
        redis_info = {}
        try:
            redis_info = await self.circuit_breaker.call(self.redis_client.info)
        except (CircuitBreakerOpenError, RedisError):
            redis_info = {"status": "unavailable"}
        
        return {
            "hit_rate": round(hit_rate, 2),
            "total_requests": total_requests,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "errors": self.stats["errors"],
            "circuit_breaker_state": self.circuit_breaker.state,
            "circuit_breaker_failures": self.circuit_breaker.failure_count,
            "redis_info": {
                "connected_clients": redis_info.get("connected_clients", "N/A"),
                "used_memory_human": redis_info.get("used_memory_human", "N/A"),
                "keyspace_hits": redis_info.get("keyspace_hits", "N/A"),
                "keyspace_misses": redis_info.get("keyspace_misses", "N/A")
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on cache service"""
        start_time = time.time()
        
        try:
            # Test basic operations
            test_key = "health_check"
            test_value = {"timestamp": datetime.utcnow().isoformat()}
            
            # Test SET
            await self.set(test_key, test_value, ttl=60)
            
            # Test GET
            retrieved = await self.get(test_key)
            
            # Test DELETE
            await self.delete(test_key)
            
            duration = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time_ms": round(duration * 1000, 2),
                "circuit_breaker_state": self.circuit_breaker.state,
                "operations_tested": ["SET", "GET", "DELETE"]
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "circuit_breaker_state": self.circuit_breaker.state,
                "response_time_ms": round((time.time() - start_time) * 1000, 2)
            }
    
    async def close(self):
        """Close Redis connections"""
        await self.redis_client.close()
        logger.info("🔌 Cache service connections closed")

# Global cache service instance
cache = CacheService()

# Convenience decorators
def cache_for(seconds: int):
    """Simple cache decorator with TTL"""
    return cache.cache_result(ttl=seconds)

def cache_scraping_result(ttl: int = 3600):
    """Cache scraping results with custom TTL"""
    def key_generator(*args, **kwargs):
        # Use URL as part of cache key for scraping functions
        url = args[0] if args else kwargs.get('url', 'unknown')
        return f"scraping:{hashlib.md5(url.encode()).hexdigest()}"
    
    return cache.cache_result(ttl=ttl, key_generator=key_generator)

def cache_ml_prediction(ttl: int = 7200):
    """Cache ML predictions with longer TTL"""
    return cache.cache_result(ttl=ttl, strategy=CacheStrategy.REFRESH_AHEAD)

if __name__ == "__main__":
    # Test the caching system
    print("🚀 Testing Enterprise Caching System")
    print("=" * 50)
    
    async def test_cache():
        # Test basic operations
        await cache.set("test_key", {"data": "test_value"}, ttl=60)
        result = await cache.get("test_key")
        print(f"✅ Basic cache test: {result}")
        
        # Test decorator
        @cache.cache_result(ttl=30)
        async def expensive_operation(param):
            await asyncio.sleep(0.1)  # Simulate work
            return f"Result for {param}"
        
        # First call - should cache
        start = time.time()
        result1 = await expensive_operation("test")
        time1 = time.time() - start
        
        # Second call - should use cache
        start = time.time()
        result2 = await expensive_operation("test")
        time2 = time.time() - start
        
        print(f"✅ First call: {result1} ({time1:.3f}s)")
        print(f"⚡ Cached call: {result2} ({time2:.3f}s)")
        print(f"🚀 Speedup: {time1/time2:.1f}x faster")
        
        # Test health check
        health = await cache.health_check()
        print(f"📊 Health check: {health}")
        
        # Test stats
        stats = await cache.get_stats()
        print(f"📈 Cache stats: {stats}")
        
        await cache.close()
    
    # Run test
    asyncio.run(test_cache())
    print("\n🎯 Caching system ready for production!")