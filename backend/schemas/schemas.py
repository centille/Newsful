from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import AnyHttpUrl, BaseModel, Field


class TextInputData(BaseModel):
    """input format for text fact checking endpoint"""

    url: Optional[AnyHttpUrl] = Field(None, description="The url of the article")
    content: str = Field("", description="The content of the article")



class FactCheckLabel(str, Enum):
    """The fact check label enum"""

    CORRECT = "correct"
    INCORRECT = "incorrect"
    MISLEADING = "misleading"


class GPTFactCheckModel(BaseModel):
    """expected result format from OpenAI for fact checking"""

    label: FactCheckLabel = Field(None, description="The result of the fact check")
    explanation: str = Field("", description="The explanation of the fact check")
    sources: list[AnyHttpUrl] = Field(list(), description="The sources of the fact check")


class HealthResponse(BaseModel):
    """The response model for the health check endpoint"""

    database_is_working: bool = Field(True, description="Whether the database is working")


class FactCheckResponse(BaseModel):
    """The response model for the fact check endpoint"""

    url: AnyHttpUrl | None = Field(None, description="The url of the article")
    label: FactCheckLabel = Field(description="The label of the fact check")
    summary: str = Field(description="The summary of the claim")
    response: str = Field(description="The logical explanation of the fact check")
    isSafe: bool = Field(description="Whether the article is safe")
    archive: str | None = Field(None, description="The archive url of the site")
    references: list[AnyHttpUrl] = Field([], description="The references of the fact check")
    updatedAt: datetime = Field(default_factory=datetime.now, description="The time of the last update")
