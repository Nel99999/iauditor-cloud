from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request


def get_user_identifier(request: Request) -> str:
    """Get user identifier for rate limiting (user_id or IP)"""
    # Try to get user from auth token
    if hasattr(request.state, "user") and request.state.user:
        return f"user:{request.state.user.get('id', 'anonymous')}"
    
    # Fallback to IP address
    return f"ip:{get_remote_address(request)}"


# Initialize rate limiter
limiter = Limiter(
    key_func=get_user_identifier,
    default_limits=["100/minute"],  # Default rate limit
    storage_uri="memory://",  # Use in-memory storage (can switch to Redis later)
)


# Rate limit configurations for different tiers
RATE_LIMITS = {
    "free": "100/minute",
    "standard": "500/minute",
    "premium": "2000/minute",
    "enterprise": "10000/minute"
}


def get_rate_limit_exceeded_handler():
    """Custom rate limit exceeded handler"""
    return _rate_limit_exceeded_handler
