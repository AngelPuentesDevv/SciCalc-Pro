"""
Pruebas unitarias — Value Objects y Entidades de Dominio.

Cubre:
  - src/domain/value_objects/expression.py   (Expression)
  - src/domain/value_objects/precision.py    (Precision)
  - src/domain/entities/profile.py           (Profile)
"""
import pytest

from src.domain.value_objects.expression import Expression
from src.domain.value_objects.precision import Precision
from src.domain.entities.profile import Profile
from src.domain.exceptions.domain_exceptions import ValidationError


# ── Expression ────────────────────────────────────────────────────────────────

def test_expression_valid_arithmetic():
    e = Expression("2 + 3")
    assert e == "2 + 3"


def test_expression_valid_trig():
    e = Expression("sin(30)")
    assert "sin" in e


def test_expression_valid_constants():
    e = Expression("pi * 2")
    assert "pi" in e


def test_expression_strips_whitespace():
    e = Expression("  5 * 5  ")
    assert e == "5 * 5"


def test_expression_empty_raises_validation_error():
    with pytest.raises(ValidationError) as exc:
        Expression("   ")
    assert exc.value.field == "expression"


def test_expression_invalid_chars_raises():
    with pytest.raises(ValidationError) as exc:
        Expression("2 & 3")
    assert exc.value.field == "expression"


def test_expression_valid_power():
    e = Expression("2^10")
    assert e == "2^10"


def test_expression_valid_nested_parens():
    e = Expression("(2 + 3) * (4 - 1)")
    assert "(" in e


# ── Precision ─────────────────────────────────────────────────────────────────

def test_precision_valid_mid():
    p = Precision(10)
    assert int(p) == 10


def test_precision_boundary_min():
    p = Precision(2)
    assert int(p) == 2


def test_precision_boundary_max():
    p = Precision(50)
    assert int(p) == 50


def test_precision_below_min_raises():
    with pytest.raises(ValidationError) as exc:
        Precision(1)
    assert exc.value.field == "precision"


def test_precision_above_max_raises():
    with pytest.raises(ValidationError) as exc:
        Precision(51)
    assert exc.value.field == "precision"


def test_precision_zero_raises():
    with pytest.raises(ValidationError):
        Precision(0)


# ── Profile ───────────────────────────────────────────────────────────────────

def test_profile_defaults():
    p = Profile(user_id="user-123")
    assert p.user_id == "user-123"
    assert p.preferred_precision == 10
    assert p.angle_mode == "DEG"
    assert p.theme == "LIGHT"
    assert p.is_deleted is False
    assert p.avatar_url is None


def test_profile_has_auto_generated_id():
    p = Profile(user_id="u1")
    assert p.id is not None
    assert len(p.id) > 10


def test_profile_has_updated_at():
    p = Profile(user_id="u1")
    assert p.updated_at is not None


def test_profile_custom_values():
    p = Profile(
        user_id="u1",
        angle_mode="RAD",
        preferred_precision=20,
        theme="DARK",
        avatar_url="https://example.com/avatar.png",
    )
    assert p.angle_mode == "RAD"
    assert p.preferred_precision == 20
    assert p.theme == "DARK"
    assert p.avatar_url == "https://example.com/avatar.png"


def test_profile_soft_delete_flag():
    p = Profile(user_id="u1", is_deleted=True)
    assert p.is_deleted is True
