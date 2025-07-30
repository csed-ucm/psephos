from pydantic import BaseModel
from typing import Optional


class Message(BaseModel):
    action: str
    data: Optional[dict]
