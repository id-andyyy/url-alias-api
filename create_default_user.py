#!/usr/bin/env python3
import sys

from sqlalchemy.orm import Session

from app.core.config import settings

from app.db.session import SessionLocal
from create_user import create_user


def main() -> None:
    su_username: str = settings.SUPERUSER_USERNAME
    su_password: str = settings.SUPERUSER_PASSWORD

    db: Session = SessionLocal()
    try:
        create_user(db, su_username, su_password)
    except Exception as e:
        db.rollback()
        print(f"Unknown error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
