from pydantic import BaseModel, AnyHttpUrl


class InputData(BaseModel):
    url: AnyHttpUrl
    content: str
