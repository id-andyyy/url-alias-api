import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.deps import get_db
from app.main import app
from app.db.base import Base

DATABASE_URL = "sqlite+pysqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture(scope="session", autouse=True)
def init_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    original = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

    if original is None:
        app.dependency_overrides.pop(get_db, None)
    else:
        app.dependency_overrides[get_db] = original



# @pytest.fixture()
# def test_user(db):
#     """
#     Создаёт в тестовой БД пользователя с правами доступа.
#     Возвращает копию объекта User для использования в тестах.
#     """
#     username = "testuser"
#     password = "testpass"
#     try:
#         user: User = crud_create_user(db, username=username, plain_password=password)
#         db.commit()
#     except UserAlreadyExistsError:
#         # Если пользователь уже есть (маловероятно в sqlite:///:memory:), просто заберём его
#         user = db.query(User).filter(User.username == username).first()
#     return {"username": username, "password": password, "id": user.id}