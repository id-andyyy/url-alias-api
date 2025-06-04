import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.user import crud_get_user_by_username, crud_create_user, crud_authenticate_user
from app.exceptions import UserAlreadyExistsError, UserCreateError
from app.models import User


def test_get_user_by_username_returns_none_if_not_exists(db: Session):
    user: User | None = crud_get_user_by_username(db, username="nonexistentuser")
    assert user is None


def test_create_user_success(db: Session):
    username: str = "andy"
    plain_password: str = "securepassword"
    user: User = crud_create_user(db, username, plain_password)

    assert isinstance(user.id, int)
    assert user.username == username
    assert user.is_active is True

    assert user.password_hash != plain_password

    fetched: User | None = crud_get_user_by_username(db, username=username)
    assert isinstance(fetched, User)
    assert fetched.id == user.id
    assert fetched.username == username


def test_create_user_raises_if_duplicate_username(db: Session):
    username: str = "alex"
    plain_password: str = "securepassword"
    user: User = crud_create_user(db, username, plain_password)

    with pytest.raises(UserAlreadyExistsError) as exc_info:
        crud_create_user(db, username, plain_password)

    assert f"User with username '{username}' already exists" in str(exc_info.value)


def test_create_user_raises_user_create_error_on_integrity_error(monkeypatch: pytest.MonkeyPatch, db: Session):
    username: str = "john"
    plain_password: str = "securepassword"

    def fake_commit():
        raise IntegrityError(statement=None, params=None, orig=None)

    monkeypatch.setattr(db, "commit", fake_commit)

    with pytest.raises(UserCreateError) as exc_info:
        crud_create_user(db, username, plain_password)

    assert "Error while creating a user" in str(exc_info.value)


@pytest.mark.parametrize(
    "stored_password, input_password, expected",
    [
        ("correct_password", "correct_password", True),
        ("correct_password", "wrong_password", False),
    ],
    ids=["password_match", "password_mismatch"]
)
def test_authenticate_user_with_real_hash(
        monkeypatch: pytest.MonkeyPatch,
        db: Session,
        stored_password: str,
        input_password: str,
        expected: bool
):
    fake_user: User = User(username="dave", password_hash="FAKE_HASH", is_active=True)
    db.add(fake_user)
    db.commit()
    db.refresh(fake_user)

    monkeypatch.setattr(
        "app.crud.user.crud_get_user_by_username",
        lambda _db, username: fake_user if username == fake_user.username else None
    )
    monkeypatch.setattr(
        "app.crud.user.verify_password",
        lambda plain_password, hashed_password: plain_password == stored_password
    )

    result = crud_authenticate_user(db, username=fake_user.username, plain_password=input_password)
    if expected:
        assert isinstance(result, User)
        assert result.username == fake_user.username
    else:
        assert result is None


def test_authenticate_user_returns_none_if_user_not_found(db: Session):
    result = crud_authenticate_user(db, username="doesnotexist", plain_password="any")
    assert result is None
