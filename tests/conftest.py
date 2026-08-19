import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import app.models as _models  # noqa: F401 - registers models on Base.metadata
from app.database import Base, get_db
from app.main import app
from app.schemas import ComplianceAnswer

TEST_DATABASE_URL = "postgresql+psycopg2://nqs:localdev@localhost:5432/nqs_test"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False)


@pytest.fixture
def db_session():
    """Fresh tables for every test.

    The extension is created here rather than assumed, because CI
    provisions a blank Postgres on every run.
    """
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def no_real_llm_calls(monkeypatch):
    """Stub every path that would reach the Gemini API.

    /ask calls retrieve() as well as structured_answer(), and retrieve()
    embeds the question, so both need patching or the tests hit the network.

    Patch the name where it is used, not where it is defined: main.py does
    `from app.services.retrieval import retrieve`, so the target is
    app.main.retrieve.
    """
    monkeypatch.setattr("app.main.retrieve", lambda db, question, k=8: [])
    monkeypatch.setattr(
        "app.main.structured_answer",
        lambda question, context="": ComplianceAnswer(
            answer="Stubbed answer",
            confidence="high",
            clauses=["Regulation 123"],
        ),
    )


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
