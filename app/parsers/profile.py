from typing import Dict, Any
from app.schemas.profile import ProfileData, Location, Experience, Education
from app.parsers.normalizer import normalize_date, deduplicate_skills

def parse_profile(raw_data: Dict[str, Any], url: str) -> ProfileData:
    """Parses raw provider data into internal typed structures."""
    
    first_name = raw_data.get("firstName", "")
    last_name = raw_data.get("lastName", "")
    name = f"{first_name} {last_name}".strip()
    
    # Location
    loc_name = raw_data.get("locationName")
    location = None
    if loc_name:
        parts = [p.strip() for p in loc_name.split(",")]
        location = Location(
            raw=loc_name,
            city=parts[0] if len(parts) > 0 else None,
            region=parts[1] if len(parts) > 1 else None,
            country=parts[-1] if len(parts) > 2 else None
        )

    # Experience
    experiences = []
    for exp in raw_data.get("experience", []):
        time_period = exp.get("timePeriod", {})
        start_date = normalize_date(time_period.get("startDate"))
        end_date = normalize_date(time_period.get("endDate"))
        
        experiences.append(
            Experience(
                title=exp.get("title"),
                company=exp.get("companyName"),
                location=exp.get("locationName"),
                start_date=start_date,
                end_date=end_date,
            )
        )

    # Education
    educations = []
    for edu in raw_data.get("education", []):
        time_period = edu.get("timePeriod", {})
        start_date = normalize_date(time_period.get("startDate"))
        end_date = normalize_date(time_period.get("endDate"))
        
        educations.append(
            Education(
                institution=edu.get("schoolName"),
                degree=edu.get("degreeName"),
                field_of_study=edu.get("fieldOfStudy"),
                start_date=start_date,
                end_date=end_date,
            )
        )

    # Skills
    raw_skills = [s.get("name", "") for s in raw_data.get("skills", [])]
    skills = deduplicate_skills(raw_skills)

    return ProfileData(
        id=raw_data.get("slug"),
        url=url,
        first_name=first_name,
        last_name=last_name,
        name=name,
        headline=raw_data.get("headline"),
        location=location,
        about=raw_data.get("summary"),
        experience=experiences,
        education=educations,
        skills=skills
    )
