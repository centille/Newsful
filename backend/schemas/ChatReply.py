from typing import Literal, Optional

from pydantic import AnyHttpUrl, BaseModel


class ChatReply(BaseModel):
    label: Literal["correct", "incorrect", "misleading"]
    response: Optional[str]
    references: Optional[list[AnyHttpUrl]] = []
