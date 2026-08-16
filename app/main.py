from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.routers import documents, centres
from app.services.llm import answer_question

app = FastAPI(title="NQS Assistant")

app.include_router(documents.router)
app.include_router(centres.router)


class Question(BaseModel):
    text: str = Field(min_length=5, max_length=500)
    centre_id: int | None = None


class Answer(BaseModel):
    answer: str
    citations: list[str] = []


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=Answer)
def ask_question(question: Question) -> Answer:
    return Answer(answer=answer_question(question.text), citations=[])