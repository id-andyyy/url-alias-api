from datetime import datetime

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.crud.link import crud_create_link, crud_get_link_by_orig_url_and_user_id
from app.models import User, Link
from app.schemas.link import LinkCreate, LinkResponse
from app.utils.short_id import generate_short_id, ShortIdGenerationError

router = APIRouter()


@router.post(
    "/",
    description="Create a new link. If a link with the same original URL already exists for the user, it returns that link instead.",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Link created successfully"},
        status.HTTP_400_BAD_REQUEST: {"description": "Link creation failed"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized (invalid/missing Basic Auth)"},
    }
)
def create_link(
        link_in: LinkCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> LinkResponse:
    existing_link: Link | None = crud_get_link_by_orig_url_and_user_id(db, link_in.orig_url, current_user.id)
    if existing_link is not None:
        return LinkResponse.model_validate(existing_link)

    try:
        new_link: Link = crud_create_link(
            db=db,
            short_id=generate_short_id(db),
            orig_url=link_in.orig_url,
            user_id=current_user.id,
            expire_seconds=link_in.expire_seconds,
            is_active=True
        )
    except ShortIdGenerationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return LinkResponse.model_validate(new_link)
