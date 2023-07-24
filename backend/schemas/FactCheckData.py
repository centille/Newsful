from pydantic import BaseModel, AnyHttpUrl, validator


class FactCheckData(BaseModel):
    url: AnyHttpUrl
    summary: str
    response: str
    confidence: float

    @validator("confidence")
    def confidence_range(cls, v):
        if v < 0 or v > 100:
            raise ValueError("Confidence must be between 0 and 1")
        return v

    @validator("summary")
    def clean_summary(cls, v):
        v = v.strip()
        v = v.replace("\n", " ")
        v = v.replace("\t", " ")
        return v.lower()
