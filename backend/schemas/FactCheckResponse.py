from pydantic import BaseModel, validator


class FactCheckResponse(BaseModel):
    label: bool
    response: str

    @validator("label")
    def label_must_be_boolean(cls, v):
        if isinstance(v, str):
            return v.lower() == "true"
        if isinstance(v, bool):
            return v
        raise ValueError("label must be a boolean value")

    @validator("response")
    def response_must_be_string(cls, v):
        if isinstance(v, str):
            # remove the Reference of "GPT Model" from response (if any)
            if "GPT Model" in v:
                v = v[: v.find("GPT Model")]
            return v
        raise ValueError("response must be a string value")
