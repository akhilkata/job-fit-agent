import re
from typing import Dict, List

from .config import get_settings
from .models import JobIn, JobScoreCreate


def _text_tokens(text: str) -> List[str]:
    text = text.lower()
    return re.findall(r"[a-z0-9\+#\.]+", text)


def _contains(text_tokens: List[str], phrase: str) -> bool:
    phrase = phrase.lower()
    return phrase in " ".join(text_tokens)


def _guess_seniority(title: str, description: str) -> str:
    text = f"{title} {description}".lower()
    if "staff" in text or "principal" in text:
        return "staff"
    if "senior" in text or "sr " in text or "sr." in text:
        return "senior"
    if "lead" in text:
        return "senior"
    if "intern" in text or "junior" in text or "grad" in text:
        return "junior"
    return "mid"


def _guess_location_type(location: str, description: str) -> str:
    text = f"{location} {description}".lower()
    if "remote" in text:
        return "remote"
    if "hybrid" in text:
        return "hybrid"
    if "onsite" in text or "on-site" in text:
        return "onsite"
    return "unknown"


def _rule_based_score(profile: Dict, job: JobIn) -> JobScoreCreate:
    """
    Offline, zero-cost scoring based on simple rules and keyword matching.
    """

    # Combine job title + description for analysis
    combined = f"{job.title}\n{job.description}"
    tokens = _text_tokens(combined)

    must = profile.get("skills_must_have", [])
    nice = profile.get("skills_nice_to_have", [])
    preferred_locs = profile.get("locations_preferred", [])
    disliked_locs = profile.get("disliked_locations", [])
    dealbreakers = profile.get("dealbreakers", [])

    score = 0
    reasons: List[str] = []

    # 1) Must-have skills
    must_hits = [s for s in must if s.lower() in " ".join(tokens)]
    if must:
        must_ratio = len(must_hits) / len(must)
    else:
        must_ratio = 0.0

    score += int(must_ratio * 60)  # up to 60 points
    if must_hits:
        reasons.append(f"Matches core stack skills: {', '.join(must_hits)}.")
    else:
        reasons.append("No clear match to core stack skills found.")

    # 2) Nice-to-have skills
    nice_hits = [s for s in nice if s.lower() in " ".join(tokens)]
    score += min(len(nice_hits) * 5, 20)  # up to 20 points
    if nice_hits:
        reasons.append(f"Has nice-to-have skills: {', '.join(nice_hits)}.")

    # 3) Location
    loc_text = job.location.lower()
    loc_match = any(loc.lower() in loc_text for loc in preferred_locs)
    loc_disliked = any(loc.lower() in loc_text for loc in disliked_locs)

    if loc_match:
        score += 10
        reasons.append(f"Location matches your preference: {job.location}.")
    if loc_disliked:
        score -= 20
        reasons.append(f"Location is in your disliked list: {job.location}.")

    # 4) Dealbreakers
    db_hit = []
    for db in dealbreakers:
        if db.lower() in combined.lower():
            db_hit.append(db)
    if db_hit:
        score -= 30
        reasons.append("Potential dealbreakers mentioned: " + ", ".join(db_hit))

    # 5) Clamp score to 0–100
    score = max(0, min(100, score))

    # Seniority / location type
    seniority = _guess_seniority(job.title, job.description)
    location_type = _guess_location_type(job.location, job.description)

    must_have_flags = {
        "core_stack_match": must_ratio >= 0.5,
        "location_match": loc_match,
        "seniority_match": seniority in ["mid", "senior", "staff"],
    }

    # Tech stack extraction: just pick all skills mentioned
    tech_stack = list({*must_hits, *nice_hits}) or must or nice

    # Suggested bullets and paragraph using templates
    suggested_bullets = [
        f"Worked extensively with {', '.join(must_hits or must or ['your core stack'])} in production systems.",
        "Designed, implemented, and optimized backend services for high-traffic applications.",
        "Collaborated with cross-functional teams to deliver reliable, scalable software.",
    ]

    why_me_paragraph = (
        f"I am a {seniority} engineer with strong experience in technologies such as "
        f"{', '.join(tech_stack[:5])}. This role at {job.company} closely aligns with my "
        f"background and interests, particularly around building robust backend services and "
        f"working with modern cloud and data tooling. Given my experience and your requirements, "
        f"I believe I can quickly contribute to the team's goals and help deliver high-quality features."
    )

    match_summary = (
        f"Rule-based match score: {score}/100. "
        f"Good alignment with your core stack and preferences, "
        f"but this is an offline heuristic, not an LLM judgment."
    )

    return JobScoreCreate(
        fit_score=score,
        seniority=seniority,
        match_summary=match_summary,
        reasons_for_score=reasons,
        tech_stack=tech_stack,
        location_type=location_type,
        requires_relocation=False,  # you can improve this later
        must_have_flags=must_have_flags,
        suggested_resume_bullets=suggested_bullets,
        why_me_paragraph=why_me_paragraph,
    )


def score_job_with_llm(job: JobIn) -> JobScoreCreate:
    """
    Kept the same function name so the rest of the app doesn't change.

    But now it's a pure offline scorer using your profile.json.
    """
    settings = get_settings()
    return _rule_based_score(settings.profile, job)