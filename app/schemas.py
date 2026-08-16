from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    body: str = Field(min_length=1)
    source_url: str | None = None
    centre_id: int | None = None


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    source_url: str | None
    created_at: datetime
    centre_id: int | None


class CentreCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    state: str = Field(min_length=2, max_length=3)


class CentreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    state: str