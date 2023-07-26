from pydantic import AnyHttpUrl, BaseModel, validator


class InputData(BaseModel):
    url: AnyHttpUrl
    content: str

    @validator("content")
    def clean_summary(cls, v):
        v = v.strip()
        v = v.replace("\n", " ")
        v = v.replace("\t", " ")
        return v.lower()

    class Config:
        schema_extra = {
            "example": {
                "url": "https://www.google.com",
                "content": "This is a test",
            }
        }
