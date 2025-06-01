from datetime import datetime

from pydantic import BaseModel, HttpUrl


class LinkBase(BaseModel):
    orig_url: HttpUrl


class LinkCreate(LinkBase):
    expire_seconds: int | None = 86400


class LinkResponse(LinkBase):
    id: int
    short_id: str
    user_id: int
    created_at: datetime
    expire_at: datetime
    is_active: bool

    class Config:
        from_attributes = True
