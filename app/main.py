from fastapi import FastAPI

from app.routers import documents, centres
from app.schemas import ComplianceAnswer, Question
from app.services.llm import structured_answer

app = FastAPI(title="NQS Assistant")

app.include_router(documents.router)
app.include_router(centres.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=ComplianceAnswer)
def ask_question(question: Question) -> ComplianceAnswer:
    return structured_answer(question.text)