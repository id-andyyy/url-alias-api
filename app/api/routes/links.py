from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.crud.link import crud_create_link, crud_get_link_by_orig_url_and_user_id, crud_get_link_by_short_id, \
    crud_deactivate_link
from app.exceptions import LinkCreateError, LinkNotFoundError, LinkUpdateError
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
        status.HTTP_403_FORBIDDEN: {"description": "User is inactive"},
    }
)
def create_link(
        link_in: LinkCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> LinkResponse:
    existing_link: Link | None = crud_get_link_by_orig_url_and_user_id(db, str(link_in.orig_url), current_user.id)
    if existing_link is not None:
        return LinkResponse.model_validate(existing_link)

    try:
        new_link: Link = crud_create_link(
            db=db,
            short_id=generate_short_id(db),
            orig_url=str(link_in.orig_url),
            user_id=current_user.id,
            expire_seconds=link_in.expire_seconds,
            is_active=True
        )
    except ShortIdGenerationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except LinkCreateError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return LinkResponse.model_validate(new_link)


@router.patch(
    "/{short_id}/deactivate",
    description="Deactivate a link by its short ID.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "Link deactivated successfully"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized (invalid/missing Basic Auth)"},
        status.HTTP_403_FORBIDDEN: {"description": "User is inactive"},
        status.HTTP_404_NOT_FOUND: {"description": "Link not found"},
    }
)
def deactivate_link(
        short_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> LinkResponse:
    try:
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
        link = crud_deactivate_link(db, short_id)
    except LinkNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except LinkUpdateError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return LinkResponse.model_validate(link)
