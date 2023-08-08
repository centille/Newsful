from pydantic import AnyHttpUrl, BaseModel


class ImageInputData(BaseModel):
    url: AnyHttpUrl
    picture_url: AnyHttpUrl
