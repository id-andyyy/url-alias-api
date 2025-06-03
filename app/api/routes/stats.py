from fastapi import APIRouter, status, Request, Query, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.crud.link import crud_get_link_by_short_id
from app.crud.stats import crud_get_stats_for_user_links, crud_get_stats_for_single_link
from app.models import User, Link
from app.schemas.stats import StatsListResponse, StatsResponse

router = APIRouter()


@router.get(
    "/",
    description="Get statistics for the user's links.",
    response_model=StatsListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized (invalid/missing Basic Auth)"},
        status.HTTP_403_FORBIDDEN: {"description": "User is inactive"},
    }
)
def read_top_links_stats(
        request: Request,
        top: int = Query(100, ge=1, description="Number of top links to retrieve"),
        sort_by: str = Query("all", enum=["hour", "day", "all"],
                             description="Sort by 'last_hour_clicks', 'last_day_clicks', or 'all_clicks'"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> StatsListResponse:
    raw_stats: list[tuple[str, str, int, int, int]] = crud_get_stats_for_user_links(db, current_user.id, top, sort_by)
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


@router.get(
    "/{short_id}",
    description="Get statistics for a specific link by its short ID.",
    response_model=StatsResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized (invalid/missing Basic Auth)"},
        status.HTTP_403_FORBIDDEN: {"description": "User is inactive"},
        status.HTTP_404_NOT_FOUND: {"description": "Link not found"},
    }
)
def read_link_stats(
        request: Request,
        short_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> StatsResponse | None:
    link: Link | None = crud_get_link_by_short_id(db, short_id)

    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    if link.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to deactivate this link"
        )

    result = crud_get_stats_for_single_link(db, link)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stats not found"
        )

    base_url: str = str(request.base_url).rstrip("/")
    orig_url, short_id, last_hour_clicks, last_day_clicks, all_clicks = crud_get_stats_for_single_link(db, link)
    return StatsResponse(
        orig_url=orig_url,
        short_url=f"{base_url}/{short_id}",
        last_hour_clicks=last_hour_clicks,
        last_day_clicks=last_day_clicks,
        all_clicks=all_clicks
    )
