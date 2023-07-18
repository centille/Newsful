from typing import List, Literal, Optional
from pydantic import BaseModel, AnyHttpUrl


class Article(BaseModel):
    __tablename__ = "articles"

    url: AnyHttpUrl
    content: str
    response: str
    label: Literal["Fake", "True"] = "Fake"
    confidence: float
    isPhishing: bool = False
    isCredible: bool = False
    archive: str
    references: Optional[List[AnyHttpUrl]] = []
