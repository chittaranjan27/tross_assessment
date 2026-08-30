import logging
from datetime import datetime

from app.integrations.linkedin.client import LinkedInClient
from app.parsers.profile import parse_profile
from app.schemas.profile import ProfileResponse, ResponseMeta
from app.services.cache import cache_service

logger = logging.getLogger(__name__)

class ProfileService:
    def __init__(self):
        self.provider = LinkedInClient()
        self.cache = cache_service

    async def get_profile(self, profile_url: str) -> ProfileResponse:
        # 1. Resolve Identity
        identity = await self.provider.resolve_profile(profile_url)

        # 2. Check Cache
        cache_key = f"linkedin:profile:{identity.slug}"
        cached_data = await self.cache.get(cache_key)

        if cached_data:
            logger.info(f"Cache hit for {identity.slug}")
            # Ensure proper schema serialization/deserialization happens
            # For simplicity, returning cached response assuming it's valid JSON matched to schema
            return ProfileResponse(**cached_data)

        logger.info(f"Cache miss for {identity.slug}. Fetching upstream.")

        # 3. Fetch Provider Data
        raw_data = await self.provider.get_profile_data(identity)

        # 4. Parse & Normalize
        profile_data = parse_profile(raw_data, profile_url)

        # 5. Build Response
        meta = ResponseMeta(
            partial=False,
            missing_sections=[],
            retrieved_at=datetime.utcnow().isoformat() + "Z"
        )

        response = ProfileResponse(
            success=True,
            data=profile_data,
            meta=meta
        )

        # 6. Cache Response
        # Pydantic v2 dump
        response_dict = response.model_dump(mode='json')
        await self.cache.set(cache_key, response_dict)

        return response

profile_service = ProfileService()
