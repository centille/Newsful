from typing import List, Literal, Optional
from pydantic import BaseModel, AnyHttpUrl


class Article(BaseModel):
    __tablename__ = "articles"

    url: AnyHttpUrl
    summary: str
    response: str
    label: Optional[Literal["Fake", "True"]] = "Fake"
    confidence: Optional[float] = 0.0
    references: Optional[List[AnyHttpUrl]] = []
    archive: str
    isPhishing: bool = False
    isCredible: bool = False
