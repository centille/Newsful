from pydantic import AnyHttpUrl, BaseModel, validator


class ImageInputData(BaseModel):
    url: AnyHttpUrl
    picture_url: AnyHttpUrl

    @validator("picture_url")
    def check_image_type(cls, v: AnyHttpUrl) -> AnyHttpUrl:
        str_v: str = v.split("?", 1)[0]
        allowed_file_extensions: list[str] = [".jpg", ".png", ".jpeg"]
        if any(str_v.endswith(extension) for extension in allowed_file_extensions):
            return v
        raise Exception("Unsupported file extension. This file extension is not yet supported.")
