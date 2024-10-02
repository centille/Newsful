from datetime import datetime
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel


class Article(BaseModel):
    """The final response class"""

    __tablename__: str = "articles"

    url: AnyHttpUrl
    dataType: Literal["text", "image"]
    label: Literal["correct", "incorrect", "misleading"]

    archive: str | None = None
    summary: str
    response: str
    references: list[AnyHttpUrl] = []
    isSafe: bool = False
    updatedAt: float = datetime.now().timestamp()
    isGovernmentRelated: bool = False
