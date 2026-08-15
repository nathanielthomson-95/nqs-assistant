from fastapi import FastAPI
from pydantic import BaseModel, Field
from app.routers import documents

app = FastAPI(title="NQS Assistant")
app.include_router(documents.router)

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
async def ask_question(question: Question) -> Answer:
    return Answer(answer=f"You asked: {question.text}", citations =[])