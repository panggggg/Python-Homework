from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class CreateBook(BaseModel):
    title: str
    pageCount: int
    authors: str
    categories: str
    created_at: str
    updated_at: str

class UpdateBook(BaseModel):
    title: Optional[str]
    pageCount: Optional[int]
    authors: Optional[str]
    categories: Optional[str]
    updated_at: datetime = Field(default_factory=datetime.now)