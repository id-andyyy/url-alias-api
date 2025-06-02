from datetime import datetime

from pydantic import BaseModel, HttpUrl


class LinkBase(BaseModel):
    orig_url: HttpUrl


class LinkCreate(LinkBase):
    expire_seconds: int = 86400


class LinkResponse(LinkBase):
    id: int
    short_id: str
    short_url: str
    user_id: int
    created_at: datetime
    expire_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class LinkListResponse(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    items: list[LinkResponse]
