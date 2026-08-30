import logging
import re
from typing import Any, Dict

import httpx

from app.core.config import settings
from app.core.exceptions import InvalidProfileUrlError
from app.integrations.linkedin.provider import ProfileIdentity, ProfileProvider

logger = logging.getLogger(__name__)


class LinkedInClient(ProfileProvider):
    def __init__(self) -> None:
        # Setup headers
        self.headers = {
            "User-Agent": settings.linkedin_user_agent,
            "Accept": "application/json",
            "Cookie": f"li_at={settings.linkedin_session_cookie}; JSESSIONID={settings.linkedin_csrf_token}",
            "csrf-token": settings.linkedin_csrf_token,
            "x-li-lang": "en_US",
        }
        # In a real app we would use connection pooling, but for this exercise we can use a new client or a shared one.
        self.client = httpx.AsyncClient(
            timeout=settings.upstream_timeout_seconds, headers=self.headers
        )

    async def resolve_profile(self, profile_url: str) -> ProfileIdentity:
        pattern = r"^https?:\/\/(www\.)?linkedin\.com\/in\/([a-zA-Z0-9\-_%]+)\/?$"
        match = re.match(pattern, profile_url.lower())
        if not match:
            raise InvalidProfileUrlError()
        slug = match.group(2)
        return ProfileIdentity(raw_url=profile_url, slug=slug)

    async def get_profile_data(self, identity: ProfileIdentity) -> Dict[str, Any]:
        """
        Fetches profile data from LinkedIn's Voyager API.
        Requires valid li_at and JSESSIONID credentials in .env
        """
        from app.core.exceptions import (
            ProfileNotFoundError,
            UpstreamAuthenticationError,
            UpstreamRateLimitError,
            UpstreamResponseParseError,
            UpstreamTimeoutError,
            UpstreamUnavailableError,
        )

        profile_url = (
            f"https://www.linkedin.com/voyager/api/identity/profiles"
            f"/{identity.slug}/profileView"
        )

        try:
            response = await self.client.get(profile_url)

            if response.status_code == 404:
                raise ProfileNotFoundError()
            elif response.status_code == 429:
                raise UpstreamRateLimitError()
            elif response.status_code in (401, 403):
                raise UpstreamAuthenticationError()
            elif response.status_code >= 500:
                raise UpstreamUnavailableError()

            response.raise_for_status()

            try:
                data = response.json()
            except Exception:
                raise UpstreamResponseParseError() from None

            # LinkedIn Voyager returns a nested structure — flatten it
            return self._normalize_voyager_response(data, identity.slug)

        except (
            ProfileNotFoundError,
            UpstreamRateLimitError,
            UpstreamAuthenticationError,
            UpstreamUnavailableError,
            UpstreamResponseParseError,
        ):
            raise
        except httpx.TimeoutException:
            raise UpstreamTimeoutError() from None
        except httpx.RequestError as e:
            logger.error(f"Request error for {identity.slug}: {e}")
            raise UpstreamUnavailableError() from None

    def _normalize_voyager_response(
        self, data: Dict[str, Any], slug: str
    ) -> Dict[str, Any]:
        """
        Flatten LinkedIn's Voyager profileView response into our internal schema.
        The response contains a top-level profile object + an 'included' entity graph.
        """
        # Build entity lookup from included array for future reference resolution
        included = data.get("included", [])

        # Core profile is usually the first element or in data directly
        profile = data.get("profile", {}) or (included[0] if included else {})
        if not profile:
            profile = data

        return {
            "slug": slug,
            "firstName": profile.get("firstName", ""),
            "lastName": profile.get("lastName", ""),
            "headline": profile.get("headline", ""),
            "locationName": profile.get("locationName", ""),
            "summary": profile.get("summary", ""),
            "experience": self._extract_experiences(included),
            "education": self._extract_educations(included),
            "skills": self._extract_skills(included),
        }

    def _extract_experiences(self, included: list[Any]) -> list[Dict[str, Any]]:
        experiences = []
        for item in included:
            if not isinstance(item, dict):
                continue
            if "com.linkedin.voyager.dash.identity.profile.Position" in item.get(
                "entityUrn", ""
            ):
                time_period = item.get("timePeriod", {}) or {}
                experiences.append(
                    {
                        "title": item.get("title"),
                        "companyName": item.get("companyName"),
                        "locationName": item.get("locationName"),
                        "timePeriod": time_period,
                        "description": item.get("description"),
                    }
                )
        return experiences

    def _extract_educations(self, included: list[Any]) -> list[Dict[str, Any]]:
        educations = []
        for item in included:
            if not isinstance(item, dict):
                continue
            if "com.linkedin.voyager.dash.identity.profile.Education" in item.get(
                "entityUrn", ""
            ):
                time_period = item.get("timePeriod", {}) or {}
                educations.append(
                    {
                        "schoolName": item.get("schoolName"),
                        "degreeName": item.get("degreeName"),
                        "fieldOfStudy": item.get("fieldOfStudy"),
                        "timePeriod": time_period,
                    }
                )
        return educations

    def _extract_skills(self, included: list[Any]) -> list[Dict[str, Any]]:
        skills = []
        for item in included:
            if not isinstance(item, dict):
                continue
            if "com.linkedin.voyager.dash.identity.profile.Skill" in item.get(
                "entityUrn", ""
            ):
                name = item.get("name")
                if name:
                    skills.append({"name": name})
        return skills
