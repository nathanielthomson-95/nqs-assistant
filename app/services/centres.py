from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Centre
from app.schemas import CentreCreate


def create(db: Session, payload: CentreCreate) -> Centre:
    centre = Centre(**payload.model_dump())
    db.add(centre)
    db.commit()
    db.refresh(centre)
    return centre


def list_all(db: Session, limit: int = 20, offset: int = 0) -> list[Centre]:
    stmt = select(Centre).offset(offset).limit(limit)
    return list(db.scalars(stmt).all())


def get(db: Session, centre_id: int) -> Centre | None:
    return db.get(Centre, centre_id)