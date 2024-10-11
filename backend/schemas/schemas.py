from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, EmailStr, Field


class TextInputData(BaseModel):
    """input format for text fact checking endpoint"""

    url: AnyHttpUrl | None = Field(None, description="The url of the article")
    content: str = Field(None, description="The content of the article")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "url": "https://www.google.com",
                    "content": "This is a test",
                }
            ]
        }
    }


class ImageInputData(BaseModel):
    """input format for image fact checking endpoint"""

    url: AnyHttpUrl = Field(None, description="The url of the image")
    picture_url: AnyHttpUrl = Field(None, description="The url of the image")


class FactCheckLabel(str, Enum):
    """The fact check label enum"""

    CORRECT = "correct"
    INCORRECT = "incorrect"
    MISLEADING = "misleading"


class GPTFactCheckModel(BaseModel):
    """expected result format from OpenAI for fact checking"""

    label: FactCheckLabel = Field(None, description="The label of the fact check")
    explanation: str = Field(None, description="The explanation of the fact check")
    sources: list[AnyHttpUrl] = Field([], description="The sources of the fact check")


class GPTGeneratedSummary(BaseModel):
    """The model for summarization"""

    summary: str = Field(None, description="The summary of the article")


class HealthResponse(BaseModel):
    """The response model for the health check endpoint"""

    database_is_working: bool = Field(True, description="Whether the database is working")


class FactCheckResponse(BaseModel):
    """The response model for the fact check endpoint"""

    url: AnyHttpUrl | None = Field(None, description="The url of the article")
    dataType: Literal["text", "image"] = Field(description="The type of data")
    label: FactCheckLabel = Field(description="The label of the fact check")
    summary: str = Field(description="The summary of the claim")
    response: str = Field(description="The logical explanation of the fact check")
    isSafe: bool = Field(description="Whether the article is safe")
    archive: str | None = Field(None, description="The archive url of the site")
    references: list[AnyHttpUrl] = Field([], description="The references of the fact check")
    updatedAt: datetime = Field(default_factory=datetime.now, description="The time of the last update")
    isGovernmentRelated: bool = Field(False, description="Whether the claim is related to government")


class User(BaseModel):
    """The user model for fastapi security"""

    email: EmailStr
    first_name: str
    last_name: str
