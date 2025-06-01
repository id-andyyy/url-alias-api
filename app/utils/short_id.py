from random import choices
from string import ascii_letters, digits

from sqlalchemy.orm import Session

from app.crud.link import crud_get_link_by_short_id
from app.exceptions import ShortIdGenerationError


def generate_short_id(db: Session, length: int = 8) -> str:
    alphabet: str = ascii_letters + digits
    for _ in range(10):
        short_id: str = "".join(choices(alphabet, k=length))
        if crud_get_link_by_short_id(db, short_id) is None:
            return short_id
    raise ShortIdGenerationError("Failed to generate a unique short ID after multiple attempts")
