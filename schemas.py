from pydantic import BaseModel, Field
from typing import List

class AnswerEvaluation(BaseModel):
    score: float = Field(ge=0, le=10, description="Score from 0 to 10")
    strengths: List[str] = Field(default_factory=list)
    missing_points: List[str] = Field(default_factory=list)
    feedback: str
    source_ids: List[str] = Field(default_factory=list)

class WeaknessReport(BaseModel):
    summary: str
    recurring_gaps: List[str] = Field(default_factory=list)
    study_plan: List[str] = Field(default_factory=list)
