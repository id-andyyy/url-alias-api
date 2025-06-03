from fastapi import APIRouter, status, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.crud.link import crud_create_link, crud_get_active_user_link_by_orig_url, crud_get_link_by_short_id, \
    crud_deactivate_link, crud_get_user_links
from app.exceptions import LinkCreateError, LinkNotFoundError, LinkUpdateError
from app.models import User, Link
from app.schemas.link import LinkCreate, LinkResponse, LinkListResponse
from app.utils.short_id import generate_short_id, ShortIdGenerationError

router = APIRouter()


@router.post(
    "/",
    description="Create a new link. If a link with the same original URL already exists for the user, it returns that link instead.",
    response_model=LinkResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Link created successfully"},
        status.HTTP_400_BAD_REQUEST: {"description": "Link creation failed"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized (invalid/missing Basic Auth)"},
        status.HTTP_403_FORBIDDEN: {"description": "User is inactive"},
    }
)
def create_link(
        request: Request,
        link_in: LinkCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> LinkResponse | None:
    base_url: str = str(request.base_url).rstrip("/")

    existing_link: Link | None = crud_get_active_user_link_by_orig_url(db, str(link_in.orig_url), current_user.id)
    if existing_link is not None:
        existing_link.short_url = f"{base_url}/{existing_link.short_id}"
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

    new_link.short_url = f"{base_url}/{new_link.short_id}"
    return LinkResponse.model_validate(new_link)


@router.patch(
    "/{short_id}/deactivate",
    description="Deactivate a link by its short ID",
    response_model=LinkResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "Link deactivated successfully"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized (invalid/missing Basic Auth)"},
        status.HTTP_403_FORBIDDEN: {"description": "User is inactive"},
        status.HTTP_404_NOT_FOUND: {"description": "Link not found"},
    }
)
def deactivate_link(
        request: Request,
        short_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> LinkResponse | None:
    base_url: str = str(request.base_url).rstrip("/")

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
        link: Link | None = crud_deactivate_link(db, link)
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

    link.short_url = f"{base_url}/{link.short_id}"
    return LinkResponse.model_validate(link)


@router.get(
    "/",
    description="Get all links for the current user with optional filters and pagination",
    response_model=LinkListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "Links retrieved successfully"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized (invalid/missing Basic Auth)"},
        status.HTTP_403_FORBIDDEN: {"description": "User is inactive"},
    }
)
def read_links(
        request: Request,
        is_valid: bool | None = Query(None,
                                      description="Filter current and outdated links. If not provided, all links are returned"),
        is_active: bool | None = Query(None, description="Filter active and inactive links. If not provided, all links are returned"),
        page: int = Query(1, ge=1, description="Page number for pagination"),
        page_size: int = Query(10, ge=1, le=100, description="Page size for pagination (1-100)"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> LinkListResponse:
    base_url: str = str(request.base_url).rstrip("/")

    offset: int = (page - 1) * page_size

    links: list[Link]
    total_items: int
    links, total_items = crud_get_user_links(db, current_user.id, is_valid, is_active, page_size, offset)

    total_pages: int = (total_items + page_size - 1) // page_size
    items = []

    for link in links:
        link.short_url = f"{base_url}/{link.short_id}"
        items.append(LinkResponse.model_validate(link))

    return LinkListResponse(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        items=items
    )
