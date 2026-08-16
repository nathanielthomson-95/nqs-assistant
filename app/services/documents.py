from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Document
from app.schemas import DocumentCreate


def create(db: Session, payload: DocumentCreate) -> Document:
    document = Document(**payload.model_dump())
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def list_all(db: Session, limit: int = 20, offset: int = 0) -> list[Document]:
    stmt = select(Document).offset(offset).limit(limit)
    return list(db.scalars(stmt).all())


def get(db: Session, document_id: int) -> Document | None:
    return db.get(Document, document_id)


def delete(db: Session, document: Document) -> None:
    db.delete(document)
    db.commit()