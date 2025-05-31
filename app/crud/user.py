from sqlalchemy.orm import Session

from app.models.user import User
from app.utils.hashing import hash_password, verify_password


class UserAlreadyExistsError(Exception):
    pass


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, username: str, plain_password: str) -> User:
    if db.query(User).filter(User.username == username).first() is not None:
        raise UserAlreadyExistsError(f"Пользователь с именем {username} уже существует")
    hashed_password: str = hash_password(plain_password)
    new_user: User = User(username=username, password_hash=hashed_password, is_active=True)
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except InterruptedError:
        db.rollback()
        raise
    return new_user


def authenticate_user(db: Session, username: str, plain_password: str) -> User | None:
    user: User | None = get_user_by_username(db, username)
    if user is not None and verify_password(plain_password, user.password_hash):
        return user
    return None
