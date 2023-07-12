from pydantic import BaseModel


class Data(BaseModel):
    url: str
    content: str
