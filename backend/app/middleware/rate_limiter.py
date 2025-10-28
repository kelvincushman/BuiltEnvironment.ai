"""
Rate limiting middleware using Redis for API protection.

Implements:
- Token bucket algorithm for smooth rate limiting
- Different limits for authenticated vs. anonymous users
- Endpoint-specific rate limits (e.g., stricter for auth endpoints)
- Redis-based distributed rate limiting
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Callable
import logging
import redis.asyncio as aioredis
import time
from functools import wraps

from ..core.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Redis-based rate limiter using token bucket algorithm.

    Rate limit tiers:
    - Anonymous users: 100 requests/minute, 1000/hour
    - Authenticated users: 1000 requests/minute, 10000/hour
    - Auth endpoints: 10 requests/minute (brute force protection)
    """

    def __init__(self):
        self.redis_client: Optional[aioredis.Redis] = None
        self.enabled = bool(settings.REDIS_URL)

        if not self.enabled:
            logger.warning("Redis not configured. Rate limiting disabled.")

    async def initialize(self):
        """Initialize Redis connection."""
        if not self.enabled:
            return

        try:
            self.redis_client = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
            await self.redis_client.ping()
            logger.info("Rate limiter initialized with Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis for rate limiting: {e}")
            self.enabled = False

    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()

    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> tuple[bool, Dict[str, any]]:
        """
        Check if request is within rate limit.

        Args:
            key: Unique identifier for rate limit bucket (e.g., user ID, IP)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            Tuple of (is_allowed, info_dict)
            info_dict contains: remaining, reset_time, limit
        """
        if not self.enabled:
            # Rate limiting disabled - allow all requests
            return True, {
                "limit": max_requests,
                "remaining": max_requests,
                "reset": int(time.time()) + window_seconds,
            }

        try:
            # Token bucket implementation with Redis
            now = int(time.time())
            bucket_key = f"ratelimit:{key}:{window_seconds}"

            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()

            # Get current bucket state
            pipe.get(f"{bucket_key}:tokens")
            pipe.get(f"{bucket_key}:last_update")

            results = await pipe.execute()
            current_tokens = int(results[0]) if results[0] else max_requests
            last_update = int(results[1]) if results[1] else now

            # Calculate token refill
            elapsed = now - last_update
            tokens_to_add = (elapsed / window_seconds) * max_requests
            current_tokens = min(max_requests, current_tokens + tokens_to_add)

            # Check if request is allowed
            if current_tokens >= 1:
                # Allow request, consume 1 token
                new_tokens = current_tokens - 1
                allowed = True
            else:
                # Rate limit exceeded
                new_tokens = current_tokens
                allowed = False

            # Update bucket state
            pipe = self.redis_client.pipeline()
            pipe.setex(f"{bucket_key}:tokens", window_seconds * 2, int(new_tokens))
            pipe.setex(f"{bucket_key}:last_update", window_seconds * 2, now)
            await pipe.execute()

            # Calculate reset time
            reset_time = now + int((1 - new_tokens) * (window_seconds / max_requests))

            return allowed, {
                "limit": max_requests,
                "remaining": int(new_tokens),
                "reset": reset_time,
            }

        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # On error, allow request (fail open)
            return True, {
                "limit": max_requests,
                "remaining": max_requests,
                "reset": int(time.time()) + window_seconds,
            }

    def get_rate_limit_key(self, request: Request) -> str:
        """
        Get unique identifier for rate limiting.

        Uses user ID if authenticated, otherwise IP address.
        """
        # Check if user is authenticated (from JWT token in state)
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"

        # Fall back to IP address for anonymous users
        client_ip = request.client.host
        # Handle proxy headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        return f"ip:{client_ip}"

    def get_rate_limits(self, request: Request) -> tuple[int, int]:
        """
        Get rate limits for request based on authentication and endpoint.

        Returns:
            Tuple of (max_requests, window_seconds)
        """
        path = request.url.path

        # Auth endpoints - strict limits (brute force protection)
        if "/auth/login" in path or "/auth/forgot-password" in path:
            return 10, 60  # 10 requests per minute

        # Upload endpoints - moderate limits
        if "/documents/upload" in path:
            if hasattr(request.state, "user_id"):
                return 50, 60  # 50 uploads per minute for authenticated
            return 10, 60  # 10 uploads per minute for anonymous

        # Authenticated users - higher limits
        if hasattr(request.state, "user_id"):
            return 1000, 60  # 1000 requests per minute

        # Anonymous users - lower limits
        return 100, 60  # 100 requests per minute


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitMiddleware:
    """FastAPI middleware for rate limiting."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Create request object
        from fastapi import Request

        request = Request(scope, receive)

        # Skip rate limiting for health checks
        if request.url.path in ["/", "/health"]:
            await self.app(scope, receive, send)
            return

        # Check rate limit
        rate_limit_key = rate_limiter.get_rate_limit_key(request)
        max_requests, window_seconds = rate_limiter.get_rate_limits(request)

        allowed, info = await rate_limiter.check_rate_limit(
            rate_limit_key, max_requests, window_seconds
        )

        if not allowed:
            # Rate limit exceeded - return 429
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please try again later.",
                        "details": {
                            "limit": info["limit"],
                            "retry_after": info["reset"] - int(time.time()),
                        },
                    }
                },
                headers={
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": str(info["remaining"]),
                    "X-RateLimit-Reset": str(info["reset"]),
                    "Retry-After": str(info["reset"] - int(time.time())),
                },
            )

            await response(scope, receive, send)
            return

        # Add rate limit headers to request state
        request.state.rate_limit_info = info

        # Continue with request
        await self.app(scope, receive, send)


def rate_limit(max_requests: int, window_seconds: int = 60):
    """
    Decorator for endpoint-specific rate limiting.

    Usage:
        @router.get("/endpoint")
        @rate_limit(max_requests=5, window_seconds=60)
        async def my_endpoint():
            ...
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs
            request: Optional[Request] = kwargs.get("request")

            if not request:
                # Try to find request in args
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if request:
                # Check rate limit
                rate_limit_key = rate_limiter.get_rate_limit_key(request)
                allowed, info = await rate_limiter.check_rate_limit(
                    rate_limit_key, max_requests, window_seconds
                )

                if not allowed:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Too many requests. Please try again later.",
                        headers={
                            "X-RateLimit-Limit": str(info["limit"]),
                            "X-RateLimit-Remaining": str(info["remaining"]),
                            "X-RateLimit-Reset": str(info["reset"]),
                            "Retry-After": str(info["reset"] - int(time.time())),
                        },
                    )

            # Call original function
            return await func(*args, **kwargs)

        return wrapper

    return decorator
