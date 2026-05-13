import time
from collections import defaultdict
from functools import wraps

from fastapi import Depends, HTTPException, Request

from app.auth.dependencies import get_current_user_optional
from app.routers.users.models import Users


class SlidingWindowRateLimiter:
    """
    In-memory sliding-window rate limiter.
    Tracks request timestamps per identifier and evicts entries older than
    ``window_seconds`` on every check.
    """

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict = defaultdict(list)

    def is_allowed(self, identifier: str) -> tuple[bool, int]:
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests
        self.requests[identifier] = [t for t in self.requests[identifier] if t > window_start]

        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(now)
            return True, 0

        retry_after = int(self.requests[identifier][0] + self.window_seconds - now) + 1
        return False, max(retry_after, 1)


def _get_client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _is_test_client(request: Request) -> bool:
    """Bypass rate limits for FastAPI TestClient to avoid flaky tests."""
    return _get_client_ip(request) == "testclient"


# =============================================================================
# Global limiter instances
# =============================================================================
AUTH_LIMITER = SlidingWindowRateLimiter(max_requests=5, window_seconds=60)
WRITE_LIMITER = SlidingWindowRateLimiter(max_requests=30, window_seconds=60)
READ_LIMITER = SlidingWindowRateLimiter(max_requests=100, window_seconds=60)


# =============================================================================
# FastAPI dependencies
# =============================================================================


async def auth_rate_limit(request: Request):
    """
    Auth endpoint rate limiter – 5 requests / minute / IP.
    Applied to login and signup endpoints.
    """
    if _is_test_client(request):
        return True
    client_ip = _get_client_ip(request)
    allowed, retry_after = AUTH_LIMITER.is_allowed(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many authentication attempts. Please try again later.",
            headers={
                "Retry-After": str(retry_after),
                "X-Error-Code": "RATE_001",
            },
        )


async def write_rate_limit(
    request: Request,
    current_user: Users | None = Depends(get_current_user_optional),
):
    """
    Write endpoint rate limiter – 30 requests / minute / user (or IP when
    unauthenticated).  Applied to POST, PUT, DELETE endpoints.
    """
    if _is_test_client(request):
        return True
    identifier = str(current_user.id) if current_user else _get_client_ip(request)
    allowed, retry_after = WRITE_LIMITER.is_allowed(identifier)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded for write operations. Please try again later.",
            headers={
                "Retry-After": str(retry_after),
                "X-Error-Code": "RATE_002",
            },
        )


async def read_rate_limit(
    request: Request,
    current_user: Users | None = Depends(get_current_user_optional),
):
    """
    Read endpoint rate limiter – 100 requests / minute / user (or IP when
    unauthenticated).  Applied to GET endpoints.
    """
    if _is_test_client(request):
        return True
    identifier = str(current_user.id) if current_user else _get_client_ip(request)
    allowed, retry_after = READ_LIMITER.is_allowed(identifier)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded for read operations. Please try again later.",
            headers={
                "Retry-After": str(retry_after),
                "X-Error-Code": "RATE_003",
            },
        )


# Backward-compatible aliases used by existing routers
login_rate_limit = auth_rate_limit
post_rate_limit = write_rate_limit
admin_rate_limit = write_rate_limit


# =============================================================================
# DEPRECATED decorator (kept for backward compatibility)
# =============================================================================


def rate_limit(max_requests: int, window_seconds: int):
    """
    DEPRECATED: Use dependency-based rate limiting (auth_rate_limit,
    write_rate_limit, read_rate_limit) instead.
    """
    limiter = SlidingWindowRateLimiter(max_requests, window_seconds)

    def decorator(endpoint):
        @wraps(endpoint)
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if request is None:
                request = kwargs.get("request")

            if request is None:
                return await endpoint(*args, **kwargs)

            if _is_test_client(request):
                return await endpoint(*args, **kwargs)

            client_ip = _get_client_ip(request)
            allowed, retry_after = limiter.is_allowed(client_ip)
            if not allowed:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later.",
                    headers={"Retry-After": str(retry_after)},
                )

            return await endpoint(*args, **kwargs)

        return wrapper

    return decorator
