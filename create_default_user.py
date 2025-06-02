#!/usr/bin/env python3
import sys

from sqlalchemy.orm import Session

from app.core.config import settings

from app.db.session import SessionLocal
from app.exceptions import UserAlreadyExistsError
from create_user import create_user


def main() -> None:
    du_username: str = settings.DEFAULT_USER_USERNAME
    du_password: str = settings.DEFAULT_USER_PASSWORD

    db: Session = SessionLocal()
    try:
        create_user(db, du_username, du_password)
    except SystemExit as e:
        if e.code == 1:
            print(f"User '{du_username}' already exists, skipping creation")
            sys.exit(0)
        else:
            raise
    except Exception as e:
        db.rollback()
        print(f"Unknown error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
