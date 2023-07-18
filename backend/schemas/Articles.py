from typing import List, Literal
from pydantic import BaseModel, HttpUrl


class Article(BaseModel):
    __tablename__ = "articles"

    url: HttpUrl
    content: str
    response: str
    label: Literal["Fake", "True"] = "Fake"
    confidence: float
    isPhishing: bool = False
    isCredible: bool = False
    archive: str
    references: List[HttpUrl]
