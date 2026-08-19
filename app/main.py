import logging

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers import centres, documents
from app.schemas import ComplianceAnswer, Question
from app.services.llm import structured_answer
from app.services.retrieval import format_context, retrieve

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("google_genai.models").setLevel(logging.WARNING)

app = FastAPI(title="NQS Assistant")

app.include_router(documents.router)
app.include_router(centres.router)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=ComplianceAnswer, tags=["ask"])
def ask_question(question: Question, db: Session = Depends(get_db)) -> ComplianceAnswer:
    """Answer a compliance question from the ingested source documents."""
    chunks = retrieve(db, question.text)
    return structured_answer(question.text, format_context(chunks))