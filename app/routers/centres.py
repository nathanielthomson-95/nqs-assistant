from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CentreCreate, CentreRead
from app.services import centres as service

router = APIRouter(prefix="/centres", tags=["centres"])


@router.post("", response_model=CentreRead, status_code=status.HTTP_201_CREATED)
def create_centre(payload: CentreCreate, db: Session = Depends(get_db)):
    return service.create(db, payload)


@router.get("", response_model=list[CentreRead])
def list_centres(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    return service.list_all(db, limit, offset)


@router.get("/{centre_id}", response_model=CentreRead)
def get_centre(centre_id: int, db: Session = Depends(get_db)):
    centre = service.get(db, centre_id)
    if centre is None:
        raise HTTPException(status_code=404, detail="Centre not found")
    return centre