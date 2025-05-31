#!/usr/bin/env python3
import sys
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings

from app.crud.user import get_user_by_username, create_user
from app.db.session import SessionLocal


def main() -> None:
    su_username: str = settings.SUPERUSER_USERNAME
    su_password: str = settings.SUPERUSER_PASSWORD

    if not su_username or not su_password:
        print("SUPERUSER_USERNAME или SUPERUSER_PASSWORD не заданы – пропуск создания суперпользователя")
        sys.exit(0)

    db: Session = SessionLocal()
    try:
        existing = get_user_by_username(db, su_username)
        if existing:
            print(f"Суперпользователь '{su_username}' уже существует (id={existing.id})")
            sys.exit(0)

        new_user = create_user(db, username=su_username, plain_password=su_password)
        sys.exit(0)
    except IntegrityError as e:
        db.rollback()
        print("Ошибка базы данных (IntegrityError):", e, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        db.rollback()
        print("Неожиданная ошибка:", e, file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
