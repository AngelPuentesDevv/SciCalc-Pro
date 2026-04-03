"""TC-UNIT-008: Gestión de sesiones web — creación, validación y expiración de tokens JWT.

Cubre la lógica de jwt_handler.py: access token (15 min) y refresh token (7 días).
ISO 29119 — Test Unit 008
"""
import os
import time
import pytest
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-session-tests-min32!!")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_DAYS", "7")

from src.infrastructure.security.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


# ── TC-UNIT-008a: creación de access token ───────────────────────────────────

def test_create_access_token_returns_string():
    """TC-UNIT-008a: create_access_token retorna un string JWT no vacío."""
    token = create_access_token({"user_id": "u1", "email": "test@example.com"})
    assert isinstance(token, str)
    assert len(token) > 10


# ── TC-UNIT-008b: access token decodificable ─────────────────────────────────

def test_access_token_decode_contains_user_id():
    """TC-UNIT-008b: El payload del access token contiene user_id y type='access'."""
    token = create_access_token({"user_id": "u2"})
    payload = decode_token(token)
    assert payload["user_id"] == "u2"
    assert payload["type"] == "access"


# ── TC-UNIT-008c: refresh token type ────────────────────────────────────────

def test_refresh_token_type_is_refresh():
    """TC-UNIT-008c: El refresh token tiene type='refresh' en el payload."""
    token = create_refresh_token({"user_id": "u3"})
    payload = decode_token(token)
    assert payload["type"] == "refresh"


# ── TC-UNIT-008d: access y refresh tokens son distintos ─────────────────────

def test_access_and_refresh_tokens_differ():
    """TC-UNIT-008d: Los tokens de acceso y refresco son diferentes para el mismo usuario."""
    data = {"user_id": "u4"}
    access = create_access_token(data)
    refresh = create_refresh_token(data)
    assert access != refresh


# ── TC-UNIT-008e: token expirado lanza 401 ───────────────────────────────────

def test_expired_token_raises_401():
    """TC-UNIT-008e: Un token con exp en el pasado lanza HTTPException 401."""
    from jose import jwt as jose_jwt
    secret = os.environ["SECRET_KEY"]
    algorithm = os.environ["ALGORITHM"]
    expired_payload = {
        "user_id": "u5",
        "type": "access",
        "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
    }
    expired_token = jose_jwt.encode(expired_payload, secret, algorithm=algorithm)
    with pytest.raises(HTTPException) as exc_info:
        decode_token(expired_token)
    assert exc_info.value.status_code == 401


# ── TC-UNIT-008f: token manipulado lanza 401 ─────────────────────────────────

def test_tampered_token_raises_401():
    """TC-UNIT-008f: Un token con firma inválida lanza HTTPException 401."""
    token = create_access_token({"user_id": "u6"})
    tampered = token[:-5] + "XXXXX"
    with pytest.raises(HTTPException) as exc_info:
        decode_token(tampered)
    assert exc_info.value.status_code == 401


# ── TC-UNIT-008g: token vacío lanza 401 ─────────────────────────────────────

def test_empty_token_raises_401():
    """TC-UNIT-008g: Un string vacío como token lanza HTTPException 401."""
    with pytest.raises(HTTPException) as exc_info:
        decode_token("")
    assert exc_info.value.status_code == 401
