from fastapi import FastAPI
import uuid
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Essay Judging Service", version="0.1.0")

class EssaySubmission(BaseModel):
    idempotency_key: Optional[str] = None
    essay_id: Optional[str] = None
    title: str
    body: str
    sources: Optional[list] = None

class ValidationResult(BaseModel):
    isValid: bool
    rationale: str

class EssayJudgment(BaseModel):
    isValid: bool
    length: ValidationResult
    density: ValidationResult
    logical_validity: ValidationResult
    sources: list = []
    essay_id: str = ""
    idempotency_key: str

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/essay/judge", response_model=EssayJudgment)
async def judge_essay(submission: EssaySubmission):
    # Generate idempotency key if not provided
    idempotency_key = submission.idempotency_key or str(uuid.uuid4())

    # Count words in the essay body
    word_count = len(submission.body.split())

    # Length validation: must be at least 1000 words
    length_valid = word_count >= 1000
    length_rationale = f"Essay has {word_count} words. Minimum required is 1000 words." if not length_valid else f"Essay has {word_count} words, which meets the minimum requirement."

    # Density validation: always pass for now (dummy implementation)
    density_valid = True
    density_rationale = "Information density validation passed."

    # Logical validity: always pass for now (dummy implementation)
    logical_valid = True
    logical_validity_rationale = "Logical validity validation passed."

    # Overall validity: all validations must pass
    overall_valid = length_valid and density_valid and logical_valid

    return EssayJudgment(
        isValid=overall_valid,
        length=ValidationResult(isValid=length_valid, rationale=length_rationale),
        density=ValidationResult(isValid=density_valid, rationale=density_rationale),
        logical_validity=ValidationResult(isValid=logical_valid, rationale=logical_validity_rationale),
        sources=[],  # Always empty for now
        essay_id="",  # Always empty for now
        idempotency_key=idempotency_key
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)