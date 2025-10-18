from fastapi import FastAPI
from schemas import EssaySubmission, EssayJudgment
from essay_service import EssayService

app = FastAPI(title="Essay Judging Service", version="0.0.1")
essay_service = EssayService()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/essay/judge", response_model=EssayJudgment)
async def judge_essay(submission: EssaySubmission):
    return await essay_service.judge_essay(submission)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)