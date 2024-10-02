from pydantic import BaseModel, field_validator


class ChatTextInputData(BaseModel):
    content: str

    @field_validator("content")
    def clean_summary(cls, v: str) -> str:
        v = v.strip()
        v = v.replace("\n", " ")
        v = v.replace("\t", " ")
        return v.lower()

    class Config:
        schema_extra: dict[str, dict[str, str]] = {
            "example": {
                "content": "This is a test",
            }
        }
