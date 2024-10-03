from typing import Literal, TypedDict

from pydantic import AnyHttpUrl, BaseModel


class Article(BaseModel):
    url: AnyHttpUrl
    archive: str
    summary: str
    response: str
    label: bool
    confidence: int
    references: list[AnyHttpUrl]
    isPhishing: bool
    isCredible: bool
    isGovernmentRelated: bool
    dataType: Literal["text", "image"]
    updatedAt: float

    def display_dict(self):
        return DisplayDict(
            url=str(self.url),
            label=self.label,
            isPhishing=self.isPhishing,
            isCredible=self.isCredible,
            dataType=self.dataType,
        )


class ArticleDict(TypedDict):
    url: AnyHttpUrl
    archive: str
    summary: str
    response: str
    label: bool
    confidence: int
    references: list[AnyHttpUrl]
    isPhishing: bool
    isCredible: bool
    isGovernmentRelated: bool
    dataType: Literal["text", "image"]
    updatedAt: float


class DisplayDict(TypedDict):
    url: str
    label: bool
    isPhishing: bool
    isCredible: bool
    dataType: Literal["text", "image"]
