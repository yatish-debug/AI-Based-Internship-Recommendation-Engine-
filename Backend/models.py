from typing import List, Optional
from pydantic import BaseModel, Field, validator

class RecommendRequest(BaseModel):
    education: Optional[str] = Field(default=None, description="Highest education or related field of study.")
    skills: List[str] = Field(default_factory=list, description="List of user skills (e.g., ['python','ml']).")
    location: Optional[str] = Field(default=None, description="Preferred location for the internship.")
    top_k: Optional[int] = Field(default=5, ge=1, le=10, description="Number of recommendations to return (1–10).")

    @validator("skills", each_item=True)
    def validate_skill(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Skill entries cannot be empty strings.")
        return v

class InternshipOut(BaseModel):
    title: str
    description: str
    location: str
    skills: List[str]
    duration: str
    score: float

class RecommendResponse(BaseModel):
    count: int
    items: List[InternshipOut]
    note: Optional[str] = None

class HealthOut(BaseModel):
    status: str
