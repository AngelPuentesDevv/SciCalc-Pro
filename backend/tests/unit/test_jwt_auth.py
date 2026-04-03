"""Prueba 6: Generación, validación y expiración de tokens JWT."""
import pytest
from datetime import timedelta
from freezegun import freeze_time
from fastapi import HTTPException

from src.infrastructure.security.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from src.infrastructure.security.password_hasher import hash_password, verify_password


# ── Access Token ──────────────────────────────────────────────────────────────

def test_access_token_is_decodable():
    token = create_access_token({"sub": "user-123", "email": "test@mail.com"})
    payload = decode_token(token)
    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"


def test_refresh_token_type():
    token = create_refresh_token({"sub": "user-123"})
    payload = decode_token(token)
    assert payload["type"] == "refresh"


def test_access_token_expires_after_15_minutes():
    """El access token debe expirar exactamente a los 15 minutos."""
    with freeze_time("2026-01-01 00:00:00"):
        token = create_access_token({"sub": "user-123"})

    # Justo antes de expirar: válido
    with freeze_time("2026-01-01 00:14:59"):
        payload = decode_token(token)
        assert payload["sub"] == "user-123"

    # Justo después de expirar: inválido
    with freeze_time(f"2026-01-01 00:{ACCESS_TOKEN_EXPIRE_MINUTES}:01"):
        with pytest.raises(HTTPException) as exc_info:
            decode_token(token)
        assert exc_info.value.status_code == 401


def test_refresh_token_expires_after_7_days():
    """El refresh token debe expirar a los 7 días."""
    with freeze_time("2026-01-01 00:00:00"):
        token = create_refresh_token({"sub": "user-123"})

    # En día 6: válido
    with freeze_time("2026-01-07 23:59:59"):
        payload = decode_token(token)
        assert payload["sub"] == "user-123"

    # En día 8: expirado
    with freeze_time("2026-01-09 00:00:01"):
        with pytest.raises(HTTPException) as exc_info:
            decode_token(token)
        assert exc_info.value.status_code == 401


def test_tampered_token_raises_401():
    """Un token manipulado debe retornar 401."""
    token = create_access_token({"sub": "user-123"})
    tampered = token[:-5] + "XXXXX"
    with pytest.raises(HTTPException) as exc_info:
        decode_token(tampered)
    assert exc_info.value.status_code == 401


# ── Password Hasher ───────────────────────────────────────────────────────────

def test_password_hash_is_not_plaintext():
    plain = "Passw0rd!"
    hashed = hash_password(plain)
    assert hashed != plain
    assert len(hashed) > 20


def test_verify_password_correct():
    plain = "Passw0rd!"
    hashed = hash_password(plain)
    assert verify_password(plain, hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("Passw0rd!")
    assert verify_password("WrongPassword1", hashed) is False
