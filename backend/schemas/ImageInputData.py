from typing import Optional

from pydantic import AnyHttpUrl, BaseModel, validator


class ImageInputData(BaseModel):
    url: AnyHttpUrl
    picture_url: AnyHttpUrl

    @validator("picture_url")
    def check_image_type(cls, v):
        v = v.split("?", 1)[0]
        allowed_file_extensions = [".jpg", ".png", ".jpeg"]
        if any(v.endswith(extension) for extension in allowed_file_extensions):
            return v
        raise Exception("Unsupported file extension. This file extension is not yet supported.")
