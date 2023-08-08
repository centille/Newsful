from pydantic import BaseModel, validator  # type: ignore


class ChatTextInputData(BaseModel):
    content: str

    @validator("content")
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
