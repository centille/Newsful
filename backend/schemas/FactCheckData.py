from pydantic import BaseModel, HttpUrl


class FactCheckData(BaseModel):
    url: HttpUrl
    summary: str
    response: str
    confidence: float
