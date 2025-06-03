import pytest

from app.utils.hashing import hash_password, verify_password


def test_same_password_generates_different_hashes():
    password = "secret_password"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    assert hash1 != hash2
    assert all(h.startswith("$2b$") for h in [hash1, hash2])


@pytest.mark.parametrize(
    "password",
    ["correct_password", "12345678", "another_secret123!$%^&*()_+", "", "a" * 1000],
    ids=[
        "simple_password",
        "numeric_password",
        "complex_password",
        "empty_password",
        "long_password"
    ]
)
def test_verify_password_correct(password: str):
    hashed = hash_password(password)
    assert hashed != password
    assert isinstance(hashed, str)
    assert hashed.startswith("$2b$")
    assert verify_password(password, hashed)


def test_verify_password_incorrect():
    password = "correct_password"
    hashed = hash_password(password)
    assert not verify_password("wrong_password", hashed)
