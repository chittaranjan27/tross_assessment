from fastapi import APIRouter, Request

from app.core.config import settings
from app.core.exceptions import RateLimitExceededError
from app.schemas.profile import ProfileRequest, ProfileResponse
from app.services.cache import cache_service
from app.services.profile_service import profile_service

router = APIRouter()

@router.post("", response_model=ProfileResponse)
async def get_profile(
    request: Request,
    profile_req: ProfileRequest
) -> ProfileResponse:

    # Simple IP-based rate limiting
    client_ip = request.client.host if request.client else "unknown"
    is_limited = await cache_service.is_rate_limited(
        client_ip,
        settings.rate_limit_requests_per_minute
    )

    if is_limited:
        raise RateLimitExceededError()

    return await profile_service.get_profile(profile_req.profile_url)
