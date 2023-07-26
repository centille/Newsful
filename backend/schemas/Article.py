from typing import List, Literal, Optional

from pydantic import AnyHttpUrl, BaseModel, validator


class Article(BaseModel):
    __tablename__ = "articles"

    url: AnyHttpUrl
    archive: Optional[str] = ""
    summary: str
    response: str
    label: Optional[bool] = False
    confidence: Optional[float] = 0.0
    references: Optional[List[AnyHttpUrl]] = []
    isPhishing: Optional[bool] = False
    isCredible: Optional[bool] = False

    @validator("label")
    def check_label(cls, v):
        if not isinstance(v, bool):
            raise ValueError("Label must be a boolean.")
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

    @validator("archive")
    def set_archive_to_url_if_empty(cls, v, values):
        if v == "":
            return values["url"]
        return v
