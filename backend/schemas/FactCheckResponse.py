from pydantic import BaseModel, field_validator


class FactCheckResponse(BaseModel):
    label: bool
    response: str

    @field_validator("label")
    def label_must_be_boolean(cls, v: str | bool) -> bool:
        if isinstance(v, str):
            return v.lower() == "true"
        return v

    @field_validator("response")
    def response_must_be_string(cls, v: str) -> str:
        # remove the Reference of "GPT Model" from response (if any)
        if "GPT Model" in v:
            v = v[: v.find("GPT Model")]
        return v
