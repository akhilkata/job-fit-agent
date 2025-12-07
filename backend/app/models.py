from typing import List, Optional, Dict, Any

from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class JobIn(BaseModel):
    """
    Incoming job posting from the frontend.
    """
    title: str
    company: str
    location: str
    description: str


class JobScoreCreate(BaseModel):
    """
    Parsed LLM scoring result (not a DB table directly).
    """
    fit_score: int
    seniority: str
    match_summary: str
    reasons_for_score: List[str]
    tech_stack: List[str]
    location_type: str
    requires_relocation: bool
    must_have_flags: Dict[str, Any]
    suggested_resume_bullets: List[str]
    why_me_paragraph: str


class Job(SQLModel, table=True):
    """
    Persisted scored job in SQLite.
    """
    id: Optional[int] = Field(default=None, primary_key=True)

    title: str
    company: str
    location: str
    description: str

    fit_score: int
    seniority: str
    match_summary: str

    tech_stack: str  # comma-separated
    location_type: str
    requires_relocation: bool

    core_stack_match: bool
    location_match: bool
    seniority_match: bool

    suggested_resume_bullets: str  # JSON string
    why_me_paragraph: str


class JobOut(BaseModel):
    """
    Response model returned to the frontend.
    """
    id: int
    title: str
    company: str
    location: str
    description: str

    fit_score: int
    seniority: str
    match_summary: str
    reasons_for_score: List[str]
    tech_stack: List[str]
    location_type: str
    requires_relocation: bool

    must_have_flags: Dict[str, Any]
    suggested_resume_bullets: List[str]
    why_me_paragraph: str

    class Config:
        orm_mode = True


class JobsBulkIn(BaseModel):
    jobs: List[JobIn]


class JobsBulkOut(BaseModel):
    jobs: List[JobOut]
