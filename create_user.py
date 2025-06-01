import argparse
import sys

from sqlalchemy.orm import Session

from app.crud.user import crud_create_user, UserAlreadyExistsError
from app.db.session import SessionLocal
from app.exceptions import UserCreateError
from app.models import User


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a new user for Basic Auth")
    parser.add_argument(
        "-u", "--username",
        type=str,
        required=True,
        help="Login of the new user (must be unique)"
    )
    parser.add_argument(
        "-p", "--password",
        type=str,
        required=True,
        help="Password for the new user"
    )
    return parser.parse_args()


def create_user(db: Session, username: str, password: str) -> None:
    if not username or not password:
        print("Error: username and password must not be empty", file=sys.stderr)
        sys.exit(1)

    try:
        new_user: User = crud_create_user(db, username=username, plain_password=password)
        print(f"New user created: username='{new_user.username}', id={new_user.id}")
    except UserAlreadyExistsError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    except UserCreateError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        db.rollback()
        print(f"Unknown error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


def main() -> None:
    args: argparse.Namespace = parse_args()
    username: str = args.username.strip()
    password: str = args.password.strip()

    db: Session = SessionLocal()
    create_user(db, username, password)


if __name__ == "__main__":
    main()
