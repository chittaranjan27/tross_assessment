import json
from pathlib import Path

from app.parsers.normalizer import deduplicate_skills
from app.parsers.profile import parse_profile


def test_deduplicate_skills():
    skills = ["Python", "React", "python", "  java  ", "JAVA"]
    deduped = deduplicate_skills(skills)
    assert len(deduped) == 3
    assert set(deduped) == {"Python", "React", "java"}

def test_parse_profile():
    fixture_path = Path(__file__).parent.parent / "fixtures" / "profile.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    profile = parse_profile(raw_data, "https://linkedin.com/in/example-slug")

    assert profile.first_name == "John"
    assert profile.last_name == "Doe"
    assert profile.name == "John Doe"
    assert profile.headline == "Senior Software Engineer"

    assert profile.location is not None
    assert profile.location.city == "Bengaluru"

    assert len(profile.experience) == 1
    assert profile.experience[0].title == "Senior Software Engineer"
    assert profile.experience[0].start_date == "2023-01"

    assert len(profile.education) == 1
    assert profile.education[0].institution == "Example University"
    assert profile.education[0].start_date == "2020"

    assert len(profile.skills) == 2  # Python and React (deduped case-insensitive)
