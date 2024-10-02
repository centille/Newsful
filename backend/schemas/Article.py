from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import AnyHttpUrl, BaseModel, validator


class Article(BaseModel):
    __tablename__: str = "articles"

    url: AnyHttpUrl
    archive: Optional[str] = ""
    summary: str
    response: str
    dataType: Literal["text", "image"]
    label: Optional[bool] = False
    references: Optional[list[AnyHttpUrl]] = []
    isSafe: Optional[bool] = False
    updatedAt: float = datetime.now().timestamp()
    isGovernmentRelated: Optional[bool] = False

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
