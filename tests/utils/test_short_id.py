import pytest

from app.exceptions import ShortIdGenerationError
from app.utils.short_id import generate_short_id


@pytest.mark.parametrize(
    "length",
    [4, 6, 8],
    ids=["length_4", "length_6", "length_8"]
)
def test_generate_short_id(monkeypatch: pytest.MonkeyPatch, length: int):
    monkeypatch.setattr(
        "app.utils.short_id.crud_get_link_by_short_id",
        lambda db, s_id: None
    )

    short_id: str = generate_short_id(db=None, length=length)
    assert isinstance(short_id, str)
    assert len(short_id) == length
    assert short_id.isalnum()


def test_generate_short_id_handles_few_collisions(monkeypatch: pytest.MonkeyPatch):
    attempts: dict[str, int] = {"attempts": 0}

    class DummyLink:
        pass

    def fake_crud_get_link_by_short_id(db: None, s_id: str) -> DummyLink | None:
        if attempts["attempts"] < 3:
            attempts["attempts"] += 1
            return DummyLink()
        return None

    monkeypatch.setattr(
        "app.utils.short_id.crud_get_link_by_short_id",
        fake_crud_get_link_by_short_id
    )
    short_id: str = generate_short_id(db=None)

    assert isinstance(short_id, str)
    assert len(short_id) == 8
    assert short_id.isalnum()
    assert attempts["attempts"] == 3


def test_generate_short_id_raises_if_all_attempts_collide(monkeypatch: pytest.MonkeyPatch):
    class DummyLink:
        pass

    monkeypatch.setattr(
        "app.utils.short_id.crud_get_link_by_short_id",
        lambda db, s_id: DummyLink()
    )
    with pytest.raises(ShortIdGenerationError) as exc_info:
        generate_short_id(db=None)

    assert "Failed to generate a unique short ID" in str(exc_info.value)