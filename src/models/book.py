from pydantic import BaseModel

class BookModel(BaseModel):
    title: str
    pageCount: int
    authors: str
    categories: str
    created_at: str
    updated_at: str