"""Rate limiting middleware for FastAPI."""

import time
import logging
from typing import Dict, Optional
from collections import defaultdict
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, requests_per_hour: int = 1000):
        self.requests_per_hour = requests_per_hour
        self.requests: Dict[str, list] = defaultdict(list)
        self.window_size = 3600  # 1 hour in seconds

    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for the client."""
        now = time.time()

        # Clean old requests
        self.requests[client_id] = [
            req_time
            for req_time in self.requests[client_id]
            if now - req_time < self.window_size
        ]

        # Check if under limit
        if len(self.requests[client_id]) < self.requests_per_hour:
            self.requests[client_id].append(now)
            return True

        return False

    def get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for the client."""
        now = time.time()
        self.requests[client_id] = [
            req_time
            for req_time in self.requests[client_id]
            if now - req_time < self.window_size
        ]
        return max(0, self.requests_per_hour - len(self.requests[client_id]))

    def get_reset_time(self, client_id: str) -> int:
        """Get time until reset for the client."""
        if not self.requests[client_id]:
            return 0
        now = time.time()
        oldest_request = min(self.requests[client_id])
        return max(0, int(self.window_size - (now - oldest_request)))


# Global rate limiter instances
api_limiter = RateLimiter(requests_per_hour=1000)  # General API limit
video_generation_limiter = RateLimiter(requests_per_hour=10)  # Video generation limit


def get_client_id(request: Request) -> str:
    """Extract client identifier from request."""
    # Use IP address as client ID (in production, consider user ID or API key)
    client_ip = request.client.host if request.client else "unknown"
    return client_ip


async def rate_limiting_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    client_id = get_client_id(request)

    # Special limits for video generation
    if request.url.path == "/api/v1/videos/generate" and request.method == "POST":
        limiter = video_generation_limiter
        limit_name = "video_generation"
    else:
        limiter = api_limiter
        limit_name = "api"

    if not limiter.is_allowed(client_id):
        remaining = limiter.get_remaining_requests(client_id)
        reset_time = limiter.get_reset_time(client_id)

        logger.warning(
            f"Rate limit exceeded for {limit_name}",
            client_id=client_id,
            path=request.url.path,
            remaining=remaining,
            reset_in=reset_time,
        )

        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Too Many Requests",
                "message": f"Rate limit exceeded for {limit_name} operations",
                "limit": limiter.requests_per_hour,
                "remaining": remaining,
                "reset_in_seconds": reset_time,
                "retry_after": reset_time,
            },
            headers={
                "X-RateLimit-Limit": str(limiter.requests_per_hour),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(int(time.time()) + reset_time),
                "Retry-After": str(reset_time),
            },
        )

    # Add rate limit headers to successful responses
    response = await call_next(request)

    if hasattr(response, "headers"):
        remaining = limiter.get_remaining_requests(client_id)
        reset_time = limiter.get_reset_time(client_id)

        response.headers["X-RateLimit-Limit"] = str(limiter.requests_per_hour)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + reset_time)

    return response


def setup_rate_limiting(app):
    """Setup rate limiting for FastAPI app."""
    app.middleware("http")(rate_limiting_middleware)
    logger.info("Rate limiting middleware enabled")
