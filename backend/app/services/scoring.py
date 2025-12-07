import json
from typing import List, Dict, Any

from sqlmodel import select

from ..db import get_session
from ..llm_client import score_job_with_llm
from ..models import Job, JobIn, JobOut, JobScoreCreate


def _job_and_score_to_entity(job_in: JobIn, score: JobScoreCreate) -> Job:
    """
    Convert a JobIn + JobScoreCreate into a Job DB entity.
    """
    tech_stack_str = ",".join(score.tech_stack)
    suggested_bullets_str = json.dumps(score.suggested_resume_bullets)

    return Job(
        title=job_in.title,
        company=job_in.company,
        location=job_in.location,
        description=job_in.description,
        fit_score=score.fit_score,
        seniority=score.seniority,
        match_summary=score.match_summary,
        tech_stack=tech_stack_str,
        location_type=score.location_type,
        requires_relocation=score.requires_relocation,
        core_stack_match=bool(score.must_have_flags.get("core_stack_match")),
        location_match=bool(score.must_have_flags.get("location_match")),
        seniority_match=bool(score.must_have_flags.get("seniority_match")),
        suggested_resume_bullets=suggested_bullets_str,
        why_me_paragraph=score.why_me_paragraph,
    )


def _entity_to_out(
    job: Job, reasons_for_score: List[str], must_have_flags: Dict[str, Any]
) -> JobOut:
    """
    Convert a Job DB entity plus extra LLM metadata into a JobOut.
    """
    tech_stack = [t for t in job.tech_stack.split(",") if t]
    suggested_bullets = json.loads(job.suggested_resume_bullets)

    return JobOut(
        id=job.id,
        title=job.title,
        company=job.company,
        location=job.location,
        description=job.description,
        fit_score=job.fit_score,
        seniority=job.seniority,
        match_summary=job.match_summary,
        reasons_for_score=reasons_for_score,
        tech_stack=tech_stack,
        location_type=job.location_type,
        requires_relocation=job.requires_relocation,
        must_have_flags=must_have_flags,
        suggested_resume_bullets=suggested_bullets,
        why_me_paragraph=job.why_me_paragraph,
    )


def score_single_job(job_in: JobIn) -> JobOut:
    """
    Score one job, save it to DB, and return a full JobOut.
    """
    score = score_job_with_llm(job_in)

    reasons = score.reasons_for_score
    flags = score.must_have_flags

    entity = _job_and_score_to_entity(job_in, score)

    with get_session() as session:
        session.add(entity)
        session.commit()
        session.refresh(entity)

    return _entity_to_out(entity, reasons_for_score=reasons, must_have_flags=flags)


def score_jobs_bulk(jobs_in: List[JobIn]) -> List[JobOut]:
    """
    Score multiple jobs and return them sorted by fit_score descending.
    """
    results: List[JobOut] = []
    for job in jobs_in:
        results.append(score_single_job(job))
    return sorted(results, key=lambda j: j.fit_score, reverse=True)


def list_jobs(min_score: int = 0, location_contains: str | None = None) -> List[Job]:
    """
    List jobs from DB with optional filters.
    """
    with get_session() as session:
        query = select(Job).where(Job.fit_score >= min_score)

        if location_contains:
            like_expr = f"%{location_contains}%"
            query = query.where(Job.location.ilike(like_expr))

        query = query.order_by(Job.fit_score.desc())
        results = session.exec(query).all()
        return results
