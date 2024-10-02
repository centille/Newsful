from typing import Literal
from pydantic import BaseModel


class FactCheckResponse(BaseModel):
    label: Literal["correct", "incorrect", "misleading"]
    response: str
