from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, EmailStr


class TextInputData(BaseModel):
    """input format for text fact checking endpoint"""

    url: AnyHttpUrl | None
    content: str

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.google.com",
                "content": "This is a test",
            }
        }


class ImageInputData(BaseModel):
    """input format for image fact checking endpoint"""

    url: AnyHttpUrl
    picture_url: AnyHttpUrl


class FactCheckLabel(str, Enum):
    """The fact check label enum"""

    CORRECT = "correct"
    INCORRECT = "incorrect"
    MISLEADING = "misleading"


class GPTFactCheckModel(BaseModel):
    """expected resulkt format from OpenAI for fact checking"""

    label: FactCheckLabel
    explanation: str
    sources: list[AnyHttpUrl] = []


class GPTGeneratedSummary(BaseModel):
    summary: str


class HealthResponse(BaseModel):
    """The response model for the health check endpoint"""

    database_is_working: bool = True


class FactCheckResponse(BaseModel):
    """The response model for the fact check endpoint"""

    url: AnyHttpUrl | None
    dataType: Literal["text", "image"]
    label: FactCheckLabel
    archive: str | None = None
    summary: str
    response: str
    references: list[AnyHttpUrl] = []
    isSafe: bool = False
    updatedAt: float = datetime.now().timestamp()
    isGovernmentRelated: bool = False
    response: str


class User(BaseModel):
    """The user model for fastapi security"""

    email: EmailStr
    first_name: str
    last_name: str
