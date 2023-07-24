from pydantic import BaseModel


class Health(BaseModel):
    status: str = "ok"
    database: bool = True
    status_code: int = 200

    class Config:
        schema_extra = {
            "example": {
                "status": "ok",
                "database": True,
                "status_code": 200,
            }
        }


# Path: backend\schemas\Health.py
