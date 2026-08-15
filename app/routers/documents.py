from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Document
from app.schemas import DocumentCreate, DocumentRead

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
def create_document(payload: DocumentCreate, db: Session = Depends(get_db)) -> DocumentRead:
    document = Document(**payload.model_dump())
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("", response_model=list[DocumentRead])
def list_documents(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    stmt = select(Document).offset(offset).limit(limit)
    return db.scalars(stmt).all()


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(document_id: int, db: Session = Depends(get_db)) -> Document:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db)) -> None:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(document)
    db.commit()