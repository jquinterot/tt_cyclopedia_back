from fastapi import FastAPI
from fastapi_ratelimit import Limiter, MemoryBackend
from fastapi_ratelimit.depends import RateLimiter


class RateLimitConfig:
    # Rate limiting configurations
    LOGIN_RATE_LIMIT = "10/minute;1/hour;5/day"
    POST_RATE_LIMIT = "30/minute;100/hour;500/day"
    API_RATE_LIMIT = "60/minute;500/hour;2000/day"
    ADMIN_RATE_LIMIT = "20/minute;100/hour;400/day"


limiter = Limiter(MemoryBackend())


def create_rate_limit_middleware(app: FastAPI) -> None:
    """
    Create rate limiting middleware for the FastAPI application.

    This middleware applies rate limiting to all API endpoints based on
    different rate limit configurations for different types of operations.
    """

    @limiter.limit(RateLimitConfig.API_RATE_LIMIT, key="ip")
    async def global_rate_limit(request):
        return True

    app.add_middleware(global_rate_limit)


def create_login_rate_limit() -> RateLimiter:
    """
    Create rate limiter for login endpoints to prevent brute force attacks.

    Returns a RateLimiter instance that limits login attempts to:
    - 10 requests per minute
    - 1 request per hour
    - 5 requests per day

    This helps prevent brute force attacks on user authentication.
    """
    return RateLimiter(rate=RateLimitConfig.LOGIN_RATE_LIMIT, key="ip", scope="login")


def create_post_rate_limit() -> RateLimiter:
    """
    Create rate limiter for post creation endpoints.

    Returns a RateLimiter instance that limits post creation to:
    - 30 requests per minute
    - 100 requests per hour
    - 500 requests per day

    This prevents spam and abuse of the post creation functionality.
    """
    return RateLimiter(rate=RateLimitConfig.POST_RATE_LIMIT, key="ip", scope="post")


def create_admin_rate_limit() -> RateLimiter:
    """
    Create rate limiter for admin endpoints.

    Returns a RateLimiter instance that limits admin operations to:
    - 20 requests per minute
    - 100 requests per hour
    - 400 requests per day

    This provides additional protection for sensitive administrative operations.
    """
    return RateLimiter(rate=RateLimitConfig.ADMIN_RATE_LIMIT, key="ip", scope="admin")
