import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
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
    Base.metadata.create_all(engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session


    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()   



@pytest.fixture(autouse=True)
def no_real_llm_calls(monkeypatch):
    monkeypatch.setattr(
        "app.main.answer_question",
        lambda question, context="": "Stubbed answer",
    )             



@pytest.fixture(autouse=True)
def no_real_llm_calls(monkeypatch):
    monkeypatch.setattr(
        "app.main.structured_answer",
        lambda question, context="": ComplianceAnswer(
            answer="Stubbed answer",
            confidence="high",
            clauses=["Regulation 123"],
        ),
    )    