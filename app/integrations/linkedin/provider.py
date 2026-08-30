from typing import Protocol, Dict, Any, Optional

class ProfileIdentity:
    def __init__(self, raw_url: str, slug: str):
        self.raw_url = raw_url
        self.slug = slug

class ProfileProvider(Protocol):
    async def resolve_profile(self, profile_url: str) -> ProfileIdentity:
        """Resolve a public URL to a profile identity (e.g. extracting the slug)"""
        ...

    async def get_profile_data(self, identity: ProfileIdentity) -> Dict[str, Any]:
        """Fetch all relevant profile sections from the provider"""
        ...
