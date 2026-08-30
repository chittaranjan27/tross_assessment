import re
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.core.exceptions import InvalidProfileUrlError


class ProfileRequest(BaseModel):
    profile_url: str

    @field_validator("profile_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        # Regex to validate LinkedIn profile URLs
        # Matches: https://www.linkedin.com/in/slug, https://linkedin.com/in/slug/
        pattern = r"^https?:\/\/(www\.)?linkedin\.com\/in\/([a-zA-Z0-9\-_%]+)\/?$"
        match = re.match(pattern, v.lower())
        if not match:
            raise InvalidProfileUrlError()
        return v


class Location(BaseModel):
    raw: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None


class ProfileImage(BaseModel):
    url: Optional[str] = None


class Experience(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    company_url: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


class Education(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class Certification(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None
    credential_id: Optional[str] = None


class Language(BaseModel):
    name: Optional[str] = None
    proficiency: Optional[str] = None


class ProfileData(BaseModel):
    id: Optional[str] = None
    url: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: Optional[str] = None
    headline: Optional[str] = None
    location: Optional[Location] = None
    about: Optional[str] = None
    profile_image: Optional[ProfileImage] = None
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    languages: List[Language] = Field(default_factory=list)


class ResponseMeta(BaseModel):
    partial: bool = False
    missing_sections: List[str] = Field(default_factory=list)
    retrieved_at: str


class ProfileResponse(BaseModel):
    success: bool = True
    data: Optional[ProfileData] = None
    meta: Optional[ResponseMeta] = None
