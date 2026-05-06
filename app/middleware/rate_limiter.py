from fastapi import HTTPException, Request, Response, Depends
from typing import Callable, Dict, Optional, Tuple
import time
from collections import defaultdict
from functools import wraps
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, time.time()))
    
    def is_allowed(self, identifier: str) -> bool:
        current_time = time.time()
        count, window_start = self.requests[identifier]
        
        # Reset window if expired
        if current_time - window_start > self.window_seconds:
            self.requests[identifier] = (1, current_time)
            return True
        
        # Check if under limit
        if count < self.max_requests:
            self.requests[identifier] = (count + 1, window_start)
            return True
        
        return False

# Global rate limiters
LOGIN_LIMITER = RateLimiter(max_requests=5, window_seconds=300)  # 5 requests per 5 minutes
WRITE_LIMITER = RateLimiter(max_requests=60, window_seconds=3600)  # 60 requests per hour

class WriteRateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP address
        client_ip = request.client.host
        
        # Check rate limit
        if not WRITE_LIMITER.is_allowed(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Try again later."
            )
        
        return await call_next(request)


def create_rate_limit_dependency(max_requests: int, window_seconds: int):
    """
    Create a rate limiting dependency for FastAPI endpoints.
    
    Args:
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds
    
    Returns:
        A dependency function that enforces rate limiting
    """
    limiter = RateLimiter(max_requests, window_seconds)
    
    async def rate_limit_dependency(request: Request):
        # Get client IP address
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        if not limiter.is_allowed(client_ip):
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again later. ({max_requests}/{window_seconds} seconds)"
            )
        
        return True
    
    return rate_limit_dependency


# Pre-configured rate limit dependencies
login_rate_limit = create_rate_limit_dependency(5, 300)
post_rate_limit = create_rate_limit_dependency(30, 3600)
admin_rate_limit = create_rate_limit_dependency(20, 3600)


# Keep backward compatibility - deprecated decorator (not recommended)
def rate_limit(max_requests: int, window_seconds: int):
    """
    DEPRECATED: Rate limiting decorator for specific endpoints.
    Use create_rate_limit_dependency() instead for better FastAPI integration.
    
    Args:
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds
    
    Returns:
        Decorator that enforces rate limiting
    """
    def decorator(endpoint):
        @wraps(endpoint)
        async def wrapper(*args, **kwargs):
            # Get request from args or kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if request is None:
                request = kwargs.get('request')
            
            if request is None:
                # If no request found, allow the request through
                return await endpoint(*args, **kwargs)
            
            # Get client IP address
            client_ip = request.client.host if request.client else "unknown"
            
            # Create rate limiter for this endpoint
            limiter = RateLimiter(max_requests, window_seconds)
            
            # Check rate limit
            if not limiter.is_allowed(client_ip):
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Try again later. ({max_requests}/{window_seconds} seconds)"
                )
            
            return await endpoint(*args, **kwargs)
        return wrapper
    return decorator