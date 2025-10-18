from pydantic import BaseModel
from typing import Optional, List


class EssaySubmission(BaseModel):
    idempotency_key: Optional[str] = None
    essay_id: Optional[str] = None
    title: str
    body: str
    sources: Optional[List[str]] = None


class ValidationResult(BaseModel):
    isValid: bool
    rationale: str


class EssayJudgment(BaseModel):
    isValid: bool
    length: ValidationResult
    density: ValidationResult
    logical_validity: ValidationResult
    sources: List[str] = []
    essay_id: str
    idempotency_key: str