from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import AnyHttpUrl, BaseModel, validator  # type: ignore


class Article(BaseModel):
    __tablename__: str = "articles"

    url: AnyHttpUrl
    archive: Optional[str] = ""
    summary: str
    response: str
    dataType: Literal["text", "image"]
    label: Optional[bool] = False
    confidence: Optional[int] = 0
    references: Optional[list[AnyHttpUrl]] = []
    isSafe: Optional[bool] = False
    updatedAt: float = datetime.utcnow().timestamp()
    isGovernmentRelated: Optional[bool] = False

    @validator("confidence")
    def check_confidence(cls, v: int) -> int:
        if v < 0 or v > 100:
            raise ValueError("Confidence must be between 0 and 1")
        return v

    @validator("summary")
    def clean_summary(cls, v: str) -> str:
        v = v.strip()
        v = v.replace("\n", " ")
        v = v.replace("\t", " ")
        return v.lower()

    @validator("archive")
    def set_archive_to_url_if_empty(cls, v: AnyHttpUrl, values: dict[str, Any]) -> AnyHttpUrl:
        if v == "":
            return values["url"]
        return v
