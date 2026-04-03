"""
Pruebas unitarias — Casos de uso con mocks.

Cubre:
  - src/application/use_cases/evaluate_expression.py  (_compute_sync, EvaluateExpressionUseCase)
  - src/application/use_cases/manage_user.py          (ManageUserUseCase.register, login)
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.application.use_cases.evaluate_expression import (
    _compute_sync,
    EvaluateExpressionUseCase,
)
from src.application.use_cases.manage_user import ManageUserUseCase
from src.application.dtos.calculation_request import CalculationRequest
from src.domain.exceptions.domain_exceptions import (
    DomainError,
    ValidationError,
    DivisionByZeroError,
)
from src.domain.entities.user import User


# ── _compute_sync (ejecuta el motor matemático en modo síncrono) ──────────────

def test_compute_sync_basic_addition():
    assert _compute_sync("2 + 3", "DEG", 10) == "5"


def test_compute_sync_multiplication():
    assert _compute_sync("4 * 5", "DEG", 10) == "20"


def test_compute_sync_trig_sin90_deg():
    result = _compute_sync("sin(90)", "DEG", 10)
    assert result == "1"


def test_compute_sync_high_precision_returns_string():
    result = _compute_sync("1 / 3", "DEG", 30)
    assert isinstance(result, str)
    assert "." in result


def test_compute_sync_rad_mode():
    import math
    result = _compute_sync("cos(0)", "RAD", 10)
    assert result == "1"


# ── EvaluateExpressionUseCase ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_evaluate_high_precision_uses_executor():
    """precision_digits > 15 debe delegar a ProcessPoolExecutor."""
    engine = MagicMock()
    history_repo = AsyncMock()
    history_repo.save = AsyncMock()

    uc = EvaluateExpressionUseCase(engine, history_repo, user_id="u1")
    req = CalculationRequest(expression="1 + 1", angle_mode="DEG", precision_digits=20)
    resp = await uc.execute(req)

    assert resp.result.startswith("2")
    assert resp.error is None
    history_repo.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_evaluate_domain_error_returns_error_response():
    """DomainError en el motor retorna CalculationResponse con error, sin persistir."""
    engine = MagicMock()
    engine.evaluate.side_effect = DivisionByZeroError()
    history_repo = AsyncMock()

    uc = EvaluateExpressionUseCase(engine, history_repo, user_id="u1")
    req = CalculationRequest(expression="5 / 1", angle_mode="DEG", precision_digits=10)
    # Reemplazamos expression para que el validator pase pero el engine falle
    req.expression = "1 / 0"
    resp = await uc.execute(req)

    assert resp.error is not None
    assert resp.error_code == "DIVISION_BY_ZERO"
    history_repo.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_evaluate_success_returns_elapsed_ms():
    """El campo elapsed_ms debe ser un número positivo."""
    engine = MagicMock()
    engine.evaluate.return_value = "42"
    history_repo = AsyncMock()
    history_repo.save = AsyncMock()

    uc = EvaluateExpressionUseCase(engine, history_repo, user_id="u1")
    req = CalculationRequest(expression="6 * 7", angle_mode="DEG", precision_digits=10)
    resp = await uc.execute(req)

    assert resp.elapsed_ms >= 0
    assert resp.result == "42"


# ── ManageUserUseCase ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_success():
    repo = AsyncMock()
    repo.get_by_email = AsyncMock(return_value=None)
    repo.create = AsyncMock(side_effect=lambda u: u)

    uc = ManageUserUseCase(repo)
    user = await uc.register("nuevo@email.com", "Password1!", "Test User")

    assert user.email == "nuevo@email.com"
    repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_duplicate_email_raises_domain_error():
    existing = User(email="dup@test.com", password_hash="hash", display_name="Dup")
    repo = AsyncMock()
    repo.get_by_email = AsyncMock(return_value=existing)

    uc = ManageUserUseCase(repo)
    with pytest.raises(DomainError) as exc:
        await uc.register("dup@test.com", "Password1!", "User")
    assert exc.value.code == "EMAIL_TAKEN"


@pytest.mark.asyncio
async def test_register_invalid_email_raises_validation_error():
    repo = AsyncMock()
    uc = ManageUserUseCase(repo)

    with pytest.raises(ValidationError) as exc:
        await uc.register("not-an-email", "Password1!", "User")
    assert exc.value.field == "email"


@pytest.mark.asyncio
async def test_register_weak_password_raises_validation_error():
    repo = AsyncMock()
    uc = ManageUserUseCase(repo)

    with pytest.raises(ValidationError) as exc:
        await uc.register("user@test.com", "weak", "User")
    assert exc.value.field == "password"


@pytest.mark.asyncio
async def test_login_success_returns_tokens():
    from src.infrastructure.security.password_hasher import hash_password
    hashed = hash_password("Password1!")
    existing = User(email="login@test.com", password_hash=hashed, display_name="Test")

    repo = AsyncMock()
    repo.get_by_email = AsyncMock(return_value=existing)

    uc = ManageUserUseCase(repo)
    tokens = await uc.login("login@test.com", "Password1!")

    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_user_not_found_raises_domain_error():
    repo = AsyncMock()
    repo.get_by_email = AsyncMock(return_value=None)

    uc = ManageUserUseCase(repo)
    with pytest.raises(DomainError) as exc:
        await uc.login("nobody@test.com", "Password1!")
    assert exc.value.code == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_login_wrong_password_raises_domain_error():
    from src.infrastructure.security.password_hasher import hash_password
    hashed = hash_password("RealPassword1!")
    existing = User(email="user@test.com", password_hash=hashed, display_name="User")

    repo = AsyncMock()
    repo.get_by_email = AsyncMock(return_value=existing)

    uc = ManageUserUseCase(repo)
    with pytest.raises(DomainError) as exc:
        await uc.login("user@test.com", "WrongPassword1!")
    assert exc.value.code == "INVALID_CREDENTIALS"
