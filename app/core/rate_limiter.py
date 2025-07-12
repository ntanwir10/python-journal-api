from typing import Optional

from fastapi import Request, Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from app.core.config import settings


def get_client_ip(request: Request) -> str:
    """Get client IP address for rate limiting."""
    # Check for forwarded headers first (for proxy/load balancer scenarios)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, take the first one
        return forwarded_for.split(",")[0].strip()

    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fall back to remote address
    return get_remote_address(request)


def get_authenticated_user_id(request: Request) -> Optional[str]:
    """Get authenticated user ID from request for user-specific rate limiting."""
    # Try to get user from request state (set by auth middleware)
    user = getattr(request.state, "user", None)
    if user:
        return str(user.id)

    # Fall back to IP-based limiting
    return get_client_ip(request)


def get_rate_limit_key(request: Request) -> str:
    """Get rate limit key based on authenticated user or IP."""
    user_id = get_authenticated_user_id(request)
    if user_id and user_id != get_client_ip(request):
        return f"user:{user_id}"
    return f"ip:{get_client_ip(request)}"


# Create limiter instance
limiter = Limiter(
    key_func=get_rate_limit_key,
    default_limits=(
        []
        if not settings.RATE_LIMIT_ENABLED
        else [f"{settings.RATE_LIMIT_REQUESTS_PER_MINUTE}/minute"]
    ),
    enabled=settings.RATE_LIMIT_ENABLED,
)


# Custom rate limit exceeded handler
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Custom handler for rate limit exceeded errors."""
    response = Response(
        content='{"detail": "Rate limit exceeded. Please try again later."}',
        status_code=HTTP_429_TOO_MANY_REQUESTS,
        headers={
            "Content-Type": "application/json",
            "Retry-After": str(exc.retry_after),
            "X-RateLimit-Limit": str(exc.detail.split("/")[0]),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(exc.retry_after)),
        },
    )
    return response


# Rate limiting decorators for different endpoint types
def general_rate_limit():
    """General rate limit for most endpoints."""
    if not settings.RATE_LIMIT_ENABLED:
        return lambda func: func
    return limiter.limit(f"{settings.RATE_LIMIT_REQUESTS_PER_MINUTE}/minute")


def auth_rate_limit():
    """Stricter rate limit for authentication endpoints."""
    if not settings.RATE_LIMIT_ENABLED:
        return lambda func: func
    return limiter.limit(f"{settings.RATE_LIMIT_AUTH_REQUESTS_PER_MINUTE}/minute")


def burst_rate_limit():
    """Rate limit allowing bursts of requests."""
    if not settings.RATE_LIMIT_ENABLED:
        return lambda func: func
    return limiter.limit(f"{settings.RATE_LIMIT_BURST_SIZE}/10seconds")
