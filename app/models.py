from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Centre(Base):
    __tablename__ = "centres"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True)
    state: Mapped[str]
    documents: Mapped[list["Document"]] = relationship(back_populates="centre")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    body: Mapped[str]
    source_url: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    centre_id: Mapped[int | None] = mapped_column(ForeignKey("centres.id"))
    centre: Mapped["Centre | None"] = relationship(back_populates="documents")