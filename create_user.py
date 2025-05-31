import argparse
import sys

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.user import get_user_by_username, create_user, UserAlreadyExistsError
from app.db.session import SessionLocal
from app.models import User

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Создание нового пользователя для Basic Auth")
    parser.add_argument(
        "-u", "--username",
        type=str,
        required=True,
        help="Логин нового пользователя (должен быть уникальным)"
    )
    parser.add_argument(
        "-p", "--password",
        type=str,
        required=True,
        help="Пароль нового пользователя"
    )
    return parser.parse_args()


def main() -> None:
    args: argparse.Namespace = parse_args()
    username: str = args.username.strip()
    password: str = args.password.strip()

    if not username or not password:
        print("Ошибка: username и password не должны быть пустыми", file=sys.stderr)
        sys.exit(1)

    db: Session = SessionLocal()
    try:
        existing_user = get_user_by_username(db, username)
        if existing_user:
            print(f"Пользователь с именем '{username}' уже существует", file=sys.stderr)
            sys.exit(1)

        new_user: User = create_user(db, username=username, plain_password=password)
        print(f"Новый пользователь создан: username='{new_user.username}', id={new_user.id}")
    except UserAlreadyExistsError as e:
        print(f"Ошибка в имени пользователя: {e}", file=sys.stderr)
        sys.exit(1)
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
