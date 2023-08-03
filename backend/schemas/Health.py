from pydantic import BaseModel


class Health(BaseModel):
    status: str = "ok"
    database: bool = True
    status_code: int = 200
