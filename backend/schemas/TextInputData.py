from pydantic import AnyHttpUrl, BaseModel


class TextInputData(BaseModel):
    url: AnyHttpUrl
    content: str

    class Config:
        schema_extra: dict[str, dict[str, str]] = {
            "example": {
                "url": "https://www.google.com",
                "content": "This is a test",
            }
        }
