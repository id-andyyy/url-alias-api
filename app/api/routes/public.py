import logging
from datetime import datetime

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app.api.deps import get_db
from app.crud.link import crud_get_link_by_short_id
from app.crud.stats import crud_log_click
from app.exceptions import ClickLogError
from app.models import Link

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/{short_id}",
    description="Get a link by short ID.",
    status_code=status.HTTP_302_FOUND,
    responses={
        status.HTTP_302_FOUND: {"description": "Redirects to the original URL"},
        status.HTTP_404_NOT_FOUND: {"description": "Link not found or inactive/expired"},
    }
)
def redirect_to_original(
        short_id: str,
        db: Session = Depends(get_db),
):
    link: Link | None = crud_get_link_by_short_id(db, short_id)

    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
        )

    if not link.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link is inactive",
        )

    now: datetime = datetime.now()
    if link.expire_at <= now:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link has expired",
        )

    try:
        crud_log_click(db, link.id)
    except ClickLogError as e:
        logger.error(f"Error logging click for link {link.id}: {str(e)}")

    return RedirectResponse(
        url=link.orig_url,
        status_code=status.HTTP_302_FOUND
    )
