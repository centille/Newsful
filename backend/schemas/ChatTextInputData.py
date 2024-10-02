from pydantic import BaseModel


class ChatTextInputData(BaseModel):
    content: str

    class Config:
        schema_extra: dict[str, dict[str, str]] = {
            "example": {
                "content": "This is a test",
            }
        }
