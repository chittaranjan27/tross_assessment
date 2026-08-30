from typing import Optional, Dict, Any, List

def normalize_date(date_dict: Optional[Dict[str, int]]) -> Optional[str]:
    if not date_dict:
        return None
    year = date_dict.get("year")
    month = date_dict.get("month")
    if year and month:
        return f"{year}-{month:02d}"
    if year:
        return str(year)
    return None

def deduplicate_skills(skills: List[str]) -> List[str]:
    seen = set()
    deduped = []
    for skill in skills:
        s_lower = skill.strip().lower()
        if s_lower not in seen and s_lower:
            seen.add(s_lower)
            deduped.append(skill.strip())
    return deduped
