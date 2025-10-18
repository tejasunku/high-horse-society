from schemas import EssaySubmission, EssayJudgment
from essay_judge import EssayJudge
import uuid


class EssayService:
    async def judge_essay(self, submission: EssaySubmission) -> EssayJudgment:
        # Use provided idempotency key or generate one
        idempotency_key = submission.idempotency_key or str(uuid.uuid4())

        # Generate essay_id (for now, just a UUID)
        essay_id = str(uuid.uuid4())

        # Create essay judge instance
        judge = EssayJudge(submission.title, submission.body)

        # Initialize LLM validations asynchronously
        await judge.initialize_validations()

        # Overall validity: all validations must pass
        overall_valid = judge.length.isValid and judge.density.isValid and judge.logical_validity.isValid

        return EssayJudgment(
            isValid=overall_valid,
            length=judge.length,
            density=judge.density,
            logical_validity=judge.logical_validity,
            sources=submission.sources or [],
            essay_id=essay_id,
            idempotency_key=idempotency_key
        )