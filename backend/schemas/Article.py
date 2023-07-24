from typing import List, Literal, Optional
from pydantic import BaseModel, AnyHttpUrl, validator


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

    @validator("label")
    def check_label(cls, v):
        if v not in ["Fake", "True"]:
            raise ValueError("Label must be either 'Fake' or 'True'")
        return v

    @validator("confidence")
    def check_confidence(cls, v):
        if v < 0 or v > 100:
            raise ValueError("Confidence must be between 0 and 1")
        return v

    @validator("summary")
    def clean_summary(cls, v):
        v = v.strip()
        v = v.replace("\n", " ")
        v = v.replace("\t", " ")
        return v.lower()

    @validator("references")
    def check_references(cls, v):
        if not isinstance(v, list):
            raise ValueError("References must be a list")
        return v
