from fastapi import APIRouter, status, Request, Query, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.crud.stats import crud_get_link_stats
from app.models import User
from app.schemas.stats import StatsListResponse, StatsResponse

router = APIRouter()


@router.get(
    "/",
    description="",
    response_model=StatsListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized (invalid/missing Basic Auth)"},
        status.HTTP_403_FORBIDDEN: {"description": "User is inactive"},
    }
)
def get_links_stats(
        request: Request,
        top: int = Query(100, ge=1, description=""),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> StatsListResponse:
    raw_stats: list[tuple[str, str, int, int, int]] = crud_get_link_stats(db, current_user.id, top)
    base_url: str = str(request.base_url).rstrip("/")

    items: list[StatsResponse] = []
    for orig_url, short_id, last_hour_clicks, last_day_clicks, all_clicks in raw_stats:
        items.append(
            StatsResponse(
                orig_url=orig_url,
                short_url=f"{base_url}/{short_id}",
                last_hour_clicks=last_hour_clicks,
                last_day_clicks=last_day_clicks,
                all_clicks=all_clicks
            )
        )

    return StatsListResponse(items=items)
