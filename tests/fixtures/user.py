import pytest

from app.api.deps import get_current_user
from app.main import app
from app.models import User


@pytest.fixture(autouse=True)
def override_get_current_user(monkeypatch, test_user: User):
    def _override():
        return test_user

    app.dependency_overrides[get_current_user] = _override
    yield
    app.dependency_overrides.pop(get_current_user, None)
