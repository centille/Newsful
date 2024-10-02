from pydantic import AnyHttpUrl, BaseModel, field_validator


class TextInputData(BaseModel):
    url: AnyHttpUrl
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
                "url": "https://www.google.com",
                "content": "This is a test",
            }
        }
