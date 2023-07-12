from pydantic import BaseModel


class FactCheckData(BaseModel):
    url: str
    summary: str
    response: str
    confidence: float
