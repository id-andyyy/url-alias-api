from pydantic import BaseModel


class StatsResponse(BaseModel):
    orig_url: str
    short_url: str
    last_hour_clicks: int
    last_day_clicks: int
    all_clicks: int


class StatsListResponse(BaseModel):
    items: list[StatsResponse]
