"""Prueba 4: Validación con Regex — regex_validators.py."""
import pytest
from src.application.validators.regex_validators import (
    validate_expression,
    validate_email,
    validate_password,
    validate_uuid_v4,
    validate_preference_key,
    validate_device_id,
    validate_number,
)


# ── Email ─────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("email", [
    "user@mail.com",
    "angel.puentes@uni.edu.co",
    "test+tag@example.org",
])
def test_email_valid(email):
    assert validate_email(email) is True


@pytest.mark.parametrize("email", [
    "user@@mail.com",
    "user@",
    "@mail.com",
    "plaintext",
    "",
])
def test_email_invalid(email):
    assert validate_email(email) is False


# ── Password ──────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("password", [
    "Passw0rd!",
    "Secret1234",
    "MyP4ssword",
])
def test_password_valid(password):
    assert validate_password(password) is True


@pytest.mark.parametrize("password", [
    "short1A",      # < 8 chars
    "nouppercase1",
    "NONUMBER!",
    "simple",
])
def test_password_invalid(password):
    assert validate_password(password) is False


# ── Expression ────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("expr", [
    "5+3",
    "sin(45)+cos(30)",
    "2^3",
    "3.14*2",
])
def test_expression_valid(expr):
    assert validate_expression(expr) is True


@pytest.mark.parametrize("expr", [
    "rm -rf /",
    "abc; DROP TABLE",
    "",
    "12..5",
])
def test_expression_invalid(expr):
    assert validate_expression(expr) is False


# ── UUID v4 ───────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("uid", [
    "550e8400-e29b-41d4-a716-446655440000",
    "f47ac10b-58cc-4372-a567-0e02b2c3d479",
])
def test_uuid_v4_valid(uid):
    assert validate_uuid_v4(uid) is True


@pytest.mark.parametrize("uid", [
    "not-a-uuid",
    "550e8400-e29b-31d4-a716-446655440000",  # versión 3, no 4
    "",
])
def test_uuid_v4_invalid(uid):
    assert validate_uuid_v4(uid) is False


# ── Preference Key ────────────────────────────────────────────────────────────

@pytest.mark.parametrize("key", ["dark_mode", "angle_mode", "precision"])
def test_preference_key_valid(key):
    assert validate_preference_key(key) is True


@pytest.mark.parametrize("key", ["a", "ab", "key with spaces", "123key"])
def test_preference_key_invalid(key):
    assert validate_preference_key(key) is False
