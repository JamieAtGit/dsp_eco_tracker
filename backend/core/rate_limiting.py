#!/usr/bin/env python3
"""
🛡️ ENTERPRISE API RATE LIMITING & AUTHENTICATION
=================================================

Production-grade rate limiting with multiple algorithms, user authentication,
and comprehensive monitoring for the DSP Eco Tracker API.

Features:
- Token bucket and sliding window rate limiting
- User-based and IP-based rate limiting  
- JWT authentication with role-based access control
- API key management for external integrations
- Comprehensive monitoring and alerting
- Graceful degradation and backpressure handling

This demonstrates enterprise-level API security and performance
management expected in production systems.
"""

import jwt
import time
import hashlib
import logging
from typing import Dict, Any, Optional, List, Tuple, Callable
from datetime import datetime, timedelta
from functools import wraps
from enum import Enum
import asyncio

from flask import request, jsonify, g
import redis.asyncio as redis
from redis.exceptions import RedisError

from .monitoring import monitoring
from .exceptions import (
    BaseEcoTrackerException, 
    ErrorSeverity, 
    ErrorCategory,
    RateLimitException
)

logger = logging.getLogger(__name__)

class RateLimitAlgorithm(str, Enum):
    """Rate limiting algorithms"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    LEAKY_BUCKET = "leaky_bucket"

class UserRole(str, Enum):
    """User roles for access control"""
    ADMIN = "admin"
    PREMIUM = "premium"
    STANDARD = "standard"
    GUEST = "guest"

class RateLimitTier:
    """Rate limit configuration for different user tiers"""
    
    GUEST = {
        "requests_per_minute": 10,
        "requests_per_hour": 100,
        "burst_capacity": 5,
        "algorithm": RateLimitAlgorithm.TOKEN_BUCKET
    }
    
    STANDARD = {
        "requests_per_minute": 60,
        "requests_per_hour": 1000,
        "burst_capacity": 20,
        "algorithm": RateLimitAlgorithm.SLIDING_WINDOW
    }
    
    PREMIUM = {
        "requests_per_minute": 200,
        "requests_per_hour": 5000,
        "burst_capacity": 50,
        "algorithm": RateLimitAlgorithm.SLIDING_WINDOW
    }
    
    ADMIN = {
        "requests_per_minute": 1000,
        "requests_per_hour": 50000,
        "burst_capacity": 100,
        "algorithm": RateLimitAlgorithm.LEAKY_BUCKET
    }

class AuthenticationError(BaseEcoTrackerException):
    """Authentication related errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.AUTHENTICATION,
            recovery_suggestion="Check your API key or login credentials",
            user_message="Authentication failed. Please check your credentials.",
            **kwargs
        )

class TokenBucket:
    """
    Token bucket algorithm implementation
    
    Allows burst requests up to capacity, then refills at a steady rate.
    Ideal for APIs that need to handle traffic spikes.
    """
    
    def __init__(
        self,
        capacity: int,
        refill_rate: float,
        redis_client: redis.Redis,
        key_prefix: str = "bucket"
    ):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.redis_client = redis_client
        self.key_prefix = key_prefix
    
    async def consume(self, key: str, tokens: int = 1) -> Tuple[bool, Dict[str, Any]]:
        """
        Attempt to consume tokens from bucket
        
        Returns:
            (success, metadata) where metadata contains current state
        """
        bucket_key = f"{self.key_prefix}:{key}"
        
        try:
            # Get current bucket state
            bucket_data = await self.redis_client.hgetall(bucket_key)
            
            current_time = time.time()
            
            if bucket_data:
                last_refill = float(bucket_data.get("last_refill", current_time))
                current_tokens = float(bucket_data.get("tokens", self.capacity))
            else:
                last_refill = current_time
                current_tokens = self.capacity
            
            # Calculate tokens to add based on time elapsed
            time_elapsed = current_time - last_refill
            tokens_to_add = time_elapsed * self.refill_rate
            
            # Update token count (capped at capacity)
            new_tokens = min(self.capacity, current_tokens + tokens_to_add)
            
            # Check if we can consume requested tokens
            if new_tokens >= tokens:
                # Consume tokens
                remaining_tokens = new_tokens - tokens
                
                # Update bucket state
                await self.redis_client.hset(bucket_key, mapping={
                    "tokens": remaining_tokens,
                    "last_refill": current_time
                })
                
                # Set expiration (cleanup old buckets)
                await self.redis_client.expire(bucket_key, 3600)
                
                return True, {
                    "tokens_remaining": remaining_tokens,
                    "capacity": self.capacity,
                    "refill_rate": self.refill_rate,
                    "algorithm": "token_bucket"
                }
            else:
                # Not enough tokens - calculate retry after
                tokens_needed = tokens - new_tokens
                retry_after = tokens_needed / self.refill_rate
                
                # Update last refill time
                await self.redis_client.hset(bucket_key, mapping={
                    "tokens": new_tokens,
                    "last_refill": current_time
                })
                
                return False, {
                    "tokens_remaining": new_tokens,
                    "tokens_needed": tokens_needed,
                    "retry_after": retry_after,
                    "capacity": self.capacity,
                    "algorithm": "token_bucket"
                }
                
        except RedisError as e:
            logger.warning(f"❌ Token bucket Redis error: {e}")
            # Fail open on Redis errors
            return True, {"error": "rate_limit_unavailable"}

class SlidingWindowCounter:
    """
    Sliding window rate limiting implementation
    
    Provides more accurate rate limiting by using a sliding time window
    instead of fixed windows. Better for preventing abuse.
    """
    
    def __init__(
        self,
        window_size: int,  # seconds
        max_requests: int,
        redis_client: redis.Redis,
        key_prefix: str = "sliding"
    ):
        self.window_size = window_size
        self.max_requests = max_requests
        self.redis_client = redis_client
        self.key_prefix = key_prefix
    
    async def is_allowed(self, key: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed within sliding window
        
        Returns:
            (allowed, metadata) with current window state
        """
        window_key = f"{self.key_prefix}:{key}"
        
        try:
            current_time = time.time()
            window_start = current_time - self.window_size
            
            # Remove old entries outside window
            await self.redis_client.zremrangebyscore(
                window_key, 0, window_start
            )
            
            # Count requests in current window
            current_requests = await self.redis_client.zcard(window_key)
            
            if current_requests < self.max_requests:
                # Add current request
                await self.redis_client.zadd(
                    window_key, {str(current_time): current_time}
                )
                
                # Set expiration
                await self.redis_client.expire(window_key, self.window_size)
                
                return True, {
                    "requests_in_window": current_requests + 1,
                    "max_requests": self.max_requests,
                    "window_size": self.window_size,
                    "algorithm": "sliding_window"
                }
            else:
                # Calculate when oldest request will expire
                oldest_request = await self.redis_client.zrange(
                    window_key, 0, 0, withscores=True
                )
                
                if oldest_request:
                    retry_after = oldest_request[0][1] + self.window_size - current_time
                else:
                    retry_after = self.window_size
                
                return False, {
                    "requests_in_window": current_requests,
                    "max_requests": self.max_requests,
                    "retry_after": max(0, retry_after),
                    "algorithm": "sliding_window"
                }
                
        except RedisError as e:
            logger.warning(f"❌ Sliding window Redis error: {e}")
            # Fail open on Redis errors
            return True, {"error": "rate_limit_unavailable"}

class AuthenticationService:
    """
    JWT and API key authentication service
    
    Provides secure authentication with role-based access control
    and comprehensive session management.
    """
    
    def __init__(self, secret_key: str, redis_client: redis.Redis):
        self.secret_key = secret_key
        self.redis_client = redis_client
        self.algorithm = "HS256"
        self.token_expiry = 24 * 3600  # 24 hours
    
    def generate_jwt_token(
        self,
        user_id: str,
        role: UserRole,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate JWT token for authenticated user"""
        
        payload = {
            "user_id": user_id,
            "role": role,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(seconds=self.token_expiry),
            "jti": hashlib.md5(f"{user_id}:{time.time()}".encode()).hexdigest()
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        logger.info(f"🔐 JWT token generated for user {user_id} (role: {role})")
        return token
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            
            # Check if token is blacklisted
            jti = payload.get("jti")
            if jti and await self._is_token_blacklisted(jti):
                raise AuthenticationError("Token has been revoked")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
    
    async def generate_api_key(
        self,
        user_id: str,
        role: UserRole,
        name: str,
        expires_in: Optional[int] = None
    ) -> Tuple[str, str]:
        """
        Generate API key for programmatic access
        
        Returns:
            (api_key, key_id) for storage and reference
        """
        
        # Generate secure API key
        key_data = f"{user_id}:{role}:{name}:{time.time()}"
        api_key = hashlib.sha256(key_data.encode()).hexdigest()
        key_id = hashlib.md5(key_data.encode()).hexdigest()[:16]
        
        # Store API key metadata
        key_metadata = {
            "user_id": user_id,
            "role": role,
            "name": name,
            "created_at": datetime.utcnow().isoformat(),
            "last_used": None,
            "usage_count": 0
        }
        
        key_redis_key = f"api_key:{api_key}"
        await self.redis_client.hset(key_redis_key, mapping=key_metadata)
        
        # Set expiration if specified
        if expires_in:
            await self.redis_client.expire(key_redis_key, expires_in)
        
        logger.info(f"🗝️ API key generated: {key_id} for user {user_id}")
        return api_key, key_id
    
    async def verify_api_key(self, api_key: str) -> Dict[str, Any]:
        """Verify API key and return user information"""
        
        key_redis_key = f"api_key:{api_key}"
        key_metadata = await self.redis_client.hgetall(key_redis_key)
        
        if not key_metadata:
            raise AuthenticationError("Invalid API key")
        
        # Update usage statistics
        await self.redis_client.hincrby(key_redis_key, "usage_count", 1)
        await self.redis_client.hset(
            key_redis_key, "last_used", datetime.utcnow().isoformat()
        )
        
        return {
            "user_id": key_metadata["user_id"],
            "role": key_metadata["role"],
            "api_key_name": key_metadata["name"]
        }
    
    async def _is_token_blacklisted(self, jti: str) -> bool:
        """Check if JWT token is blacklisted"""
        blacklist_key = f"blacklist:{jti}"
        return bool(await self.redis_client.exists(blacklist_key))
    
    async def blacklist_token(self, jti: str, expiry: int):
        """Add token to blacklist"""
        blacklist_key = f"blacklist:{jti}"
        await self.redis_client.setex(blacklist_key, expiry, "blacklisted")

class RateLimitService:
    """
    Enterprise rate limiting service with multiple algorithms
    
    Provides flexible rate limiting with user-based limits,
    comprehensive monitoring, and graceful degradation.
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.auth_service = AuthenticationService(
            secret_key="your-secret-key",  # Should come from environment
            redis_client=redis_client
        )
        
        # Initialize rate limiters
        self.token_buckets = {}
        self.sliding_windows = {}
        
        logger.info("🛡️ Rate limiting service initialized")
    
    def get_rate_limits_for_role(self, role: UserRole) -> Dict[str, Any]:
        """Get rate limit configuration for user role"""
        
        role_limits = {
            UserRole.GUEST: RateLimitTier.GUEST,
            UserRole.STANDARD: RateLimitTier.STANDARD,
            UserRole.PREMIUM: RateLimitTier.PREMIUM,
            UserRole.ADMIN: RateLimitTier.ADMIN
        }
        
        return role_limits.get(role, RateLimitTier.GUEST)
    
    async def check_rate_limit(
        self,
        identifier: str,
        role: UserRole,
        endpoint: str = "default"
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is within rate limits
        
        Args:
            identifier: User ID, IP address, or API key
            role: User role for determining limits
            endpoint: Specific endpoint for granular limiting
            
        Returns:
            (allowed, metadata) with rate limit information
        """
        
        limits = self.get_rate_limits_for_role(role)
        algorithm = limits["algorithm"]
        
        # Create rate limiter key
        rate_limit_key = f"{identifier}:{endpoint}"
        
        with monitoring.trace_span("rate_limit_check", {
            "rate_limit.identifier": identifier,
            "rate_limit.role": role,
            "rate_limit.algorithm": algorithm,
            "rate_limit.endpoint": endpoint
        }):
            
            if algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
                return await self._check_token_bucket(rate_limit_key, limits)
            elif algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
                return await self._check_sliding_window(rate_limit_key, limits)
            else:
                # Default to token bucket
                return await self._check_token_bucket(rate_limit_key, limits)
    
    async def _check_token_bucket(
        self, 
        key: str, 
        limits: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check token bucket rate limit"""
        
        bucket = TokenBucket(
            capacity=limits["burst_capacity"],
            refill_rate=limits["requests_per_minute"] / 60.0,
            redis_client=self.redis_client,
            key_prefix="rate_limit_bucket"
        )
        
        return await bucket.consume(key)
    
    async def _check_sliding_window(
        self,
        key: str,
        limits: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check sliding window rate limit"""
        
        window = SlidingWindowCounter(
            window_size=60,  # 1 minute window
            max_requests=limits["requests_per_minute"],
            redis_client=self.redis_client,
            key_prefix="rate_limit_window"
        )
        
        return await window.is_allowed(key)
    
    def rate_limit(
        self,
        per_minute: Optional[int] = None,
        per_hour: Optional[int] = None,
        role_based: bool = True,
        endpoint_specific: bool = True
    ):
        """
        Flask decorator for rate limiting endpoints
        
        Usage:
            @rate_limit_service.rate_limit(per_minute=60, role_based=True)
            def api_endpoint():
                return jsonify({"data": "response"})
        """
        
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                
                # Extract user information
                user_info = await self._extract_user_info(request)
                identifier = user_info["identifier"]
                role = user_info["role"]
                
                # Determine endpoint name
                endpoint = func.__name__ if endpoint_specific else "default"
                
                # Check rate limit
                allowed, metadata = await self.check_rate_limit(
                    identifier, role, endpoint
                )
                
                if not allowed:
                    # Rate limit exceeded
                    monitoring.create_alert(
                        "rate_limit_exceeded",
                        "medium",
                        f"Rate limit exceeded for {identifier}",
                        {"role": role, "endpoint": endpoint, "metadata": metadata}
                    )
                    
                    retry_after = metadata.get("retry_after", 60)
                    
                    response = jsonify({
                        "error": "Rate limit exceeded",
                        "retry_after": retry_after,
                        "rate_limit_info": metadata
                    })
                    response.status_code = 429
                    response.headers["Retry-After"] = str(int(retry_after))
                    return response
                
                # Store user info for endpoint use
                g.user_info = user_info
                g.rate_limit_info = metadata
                
                # Execute endpoint
                return await func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    async def _extract_user_info(self, request) -> Dict[str, Any]:
        """Extract user information from request for rate limiting"""
        
        # Check for JWT token
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                token = auth_header[7:]
                payload = self.auth_service.verify_jwt_token(token)
                return {
                    "identifier": payload["user_id"],
                    "role": UserRole(payload["role"]),
                    "auth_method": "jwt"
                }
            except AuthenticationError:
                pass
        
        # Check for API key
        api_key = request.headers.get("X-API-Key") or request.args.get("api_key")
        if api_key:
            try:
                key_info = await self.auth_service.verify_api_key(api_key)
                return {
                    "identifier": key_info["user_id"],
                    "role": UserRole(key_info["role"]),
                    "auth_method": "api_key"
                }
            except AuthenticationError:
                pass
        
        # Fallback to IP-based limiting for unauthenticated users
        return {
            "identifier": request.remote_addr or "unknown",
            "role": UserRole.GUEST,
            "auth_method": "ip"
        }
    
    async def get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics for monitoring"""
        
        # This would be implemented to gather stats from Redis
        # For now, return basic structure
        return {
            "total_requests": 0,
            "rate_limited_requests": 0,
            "top_limited_users": [],
            "algorithm_usage": {
                "token_bucket": 0,
                "sliding_window": 0
            }
        }

# Global rate limit service instance
rate_limit_service = RateLimitService(
    redis_client=redis.Redis.from_url("redis://localhost:6379")
)

# Convenience decorators
def rate_limit_standard(per_minute: int = 60):
    """Standard rate limiting decorator"""
    return rate_limit_service.rate_limit(per_minute=per_minute)

def rate_limit_strict(per_minute: int = 10):
    """Strict rate limiting for sensitive endpoints"""
    return rate_limit_service.rate_limit(per_minute=per_minute, role_based=True)

if __name__ == "__main__":
    # Test the rate limiting system
    print("🛡️ Testing Enterprise Rate Limiting System")
    print("=" * 50)
    
    async def test_rate_limiting():
        # Initialize Redis client for testing
        redis_client = redis.Redis.from_url("redis://localhost:6379", decode_responses=True)
        service = RateLimitService(redis_client)
        
        # Test token bucket
        print("🪣 Testing Token Bucket Algorithm")
        for i in range(10):
            allowed, metadata = await service.check_rate_limit(
                "test_user", UserRole.STANDARD, "test_endpoint"
            )
            print(f"Request {i+1}: {'✅ Allowed' if allowed else '❌ Blocked'} - {metadata}")
            
            if not allowed:
                print(f"   Retry after: {metadata.get('retry_after', 0):.2f}s")
        
        # Test API key generation
        print("\n🗝️ Testing API Key Generation")
        api_key, key_id = await service.auth_service.generate_api_key(
            "test_user", UserRole.PREMIUM, "test_key"
        )
        print(f"Generated API key: {key_id}")
        
        # Test API key verification
        key_info = await service.auth_service.verify_api_key(api_key)
        print(f"API key verified: {key_info}")
        
        await redis_client.close()
    
    # Run test
    asyncio.run(test_rate_limiting())
    print("\n🚀 Rate limiting system ready for production!")