from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import init_db
from .models import JobIn, JobOut, JobsBulkIn, JobsBulkOut
from .services.scoring import list_jobs, score_jobs_bulk, score_single_job

app = FastAPI(
    title="Job Fit Agent API",
    version="0.1.0",
    description="LLM-powered job fit scorer for software roles.",
)

# CORS configuration (Angular dev server will be on http://localhost:4200)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/api/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.post("/api/jobs/score", response_model=JobOut)
def api_score_job(job: JobIn) -> JobOut:
    return score_single_job(job)


@app.post("/api/jobs/score-bulk", response_model=JobsBulkOut)
def api_score_jobs_bulk(payload: JobsBulkIn) -> JobsBulkOut:
    jobs_out = score_jobs_bulk(payload.jobs)
    return JobsBulkOut(jobs=jobs_out)


@app.get("/api/jobs", response_model=List[JobOut])
def api_list_jobs(
    min_score: int = 0,
    location_contains: Optional[str] = None,
) -> List[JobOut]:
    jobs = list_jobs(min_score=min_score, location_contains=location_contains)

    # For GET list, we don't have reasons_for_score stored; return minimal view.
    out: List[JobOut] = []
    for job in jobs:
        out.append(
            JobOut(
                id=job.id,
                title=job.title,
                company=job.company,
                location=job.location,
                description=job.description,
                fit_score=job.fit_score,
                seniority=job.seniority,
                match_summary=job.match_summary,
                reasons_for_score=[],  # could be enhanced later
                tech_stack=[t for t in job.tech_stack.split(",") if t],
                location_type=job.location_type,
                requires_relocation=job.requires_relocation,
                must_have_flags={
                    "core_stack_match": job.core_stack_match,
                    "location_match": job.location_match,
                    "seniority_match": job.seniority_match,
                },
                suggested_resume_bullets=[],
                why_me_paragraph=job.why_me_paragraph,
            )
        )
    return out
