from fastapi import FastAPI

from app.routers import documents, centres
from app.schemas import ComplianceAnswer, Question
from app.services.llm import structured_answer

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.retrieval import format_context, retrieve

app = FastAPI(title="NQS Assistant")

app.include_router(documents.router)
app.include_router(centres.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=ComplianceAnswer)
def ask_question(question: Question) -> ComplianceAnswer:
    return structured_answer(question.text)



@app.post("/ask", response_model=ComplianceAnswer)
def ask_question(question: Question, db: Session = Depends(get_db)) -> ComplianceAnswer:
    chunks = retrieve(db, question.text)
    return structured_answer(question.text, format_context(chunks))