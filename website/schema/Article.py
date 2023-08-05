from pydantic import AnyHttpUrl, BaseModel, field_validator


class Article(BaseModel):
    url: AnyHttpUrl
    archive: str
    summary: str
    response: str
    label: bool | str
    confidence: int
    references: list[AnyHttpUrl]
    isPhishing: bool
    isCredible: bool

    @field_validator("label")
    def change_to_bool(cls, v: bool | str) -> bool:
        if isinstance(v, str):
            if v.lower() == "fake":
                return False
            return True
        return v
