from pydantic import BaseModel, AnyHttpUrl


class FactCheckData(BaseModel):
    url: AnyHttpUrl
    summary: str
    response: str
    confidence: float
