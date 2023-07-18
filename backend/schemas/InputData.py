from pydantic import BaseModel, HttpUrl


class InputData(BaseModel):
    url: HttpUrl
    content: str
