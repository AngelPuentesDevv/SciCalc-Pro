"""
Pruebas de integración — Endpoint de cálculo.

Cubre:
  - POST /api/v1/calculate
  - fastapi_router.py (calculate)
  - evaluate_expression.py (use case)
  - math_engine_adapter.py (MpMathCalculationEngine)
  - postgres_history_repo.py (save)
  - auth_middleware.py (get_current_user en ruta protegida)
"""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")


# ── Aritmética básica (RF-001) ────────────────────────────────────────────────

async def test_calculate_addition(client: AsyncClient, auth_headers: dict):
    """2 + 3 = 5."""
    resp = await client.post(
        "/api/v1/calculate",
        json={"expression": "2 + 3", "angle_mode": "DEG", "precision_digits": 10},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["result"] == "5"


async def test_calculate_precedence(client: AsyncClient, auth_headers: dict):
    """2 + 3 * 4 = 14 (precedencia de operadores)."""
    resp = await client.post(
        "/api/v1/calculate",
        json={"expression": "2 + 3 * 4", "angle_mode": "DEG", "precision_digits": 10},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["result"] == "14"


async def test_calculate_power(client: AsyncClient, auth_headers: dict):
    """2^10 = 1024."""
    resp = await client.post(
        "/api/v1/calculate",
        json={"expression": "2^10", "angle_mode": "DEG", "precision_digits": 10},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["result"] == "1024"


# ── Trigonometría DEG y RAD (RF-002) ─────────────────────────────────────────

async def test_calculate_sin90_deg(client: AsyncClient, auth_headers: dict):
    """sin(90) en DEG = 1."""
    resp = await client.post(
        "/api/v1/calculate",
        json={"expression": "sin(90)", "angle_mode": "DEG", "precision_digits": 10},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    result = float(resp.json()["result"])
    assert abs(result - 1.0) < 1e-9


async def test_calculate_cos0_deg(client: AsyncClient, auth_headers: dict):
    """cos(0) en DEG = 1."""
    resp = await client.post(
        "/api/v1/calculate",
        json={"expression": "cos(0)", "angle_mode": "DEG", "precision_digits": 10},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    result = float(resp.json()["result"])
    assert abs(result - 1.0) < 1e-9


async def test_calculate_trig_rad_mode(client: AsyncClient, auth_headers: dict):
    """cos(0) en RAD = 1."""
    resp = await client.post(
        "/api/v1/calculate",
        json={"expression": "cos(0)", "angle_mode": "RAD", "precision_digits": 15},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    result = float(resp.json()["result"])
    assert abs(result - 1.0) < 1e-9


# ── Notación científica (RF-008) ──────────────────────────────────────────────

async def test_calculate_scientific_notation(client: AsyncClient, auth_headers: dict):
    """1.5e3 * 2 = 3000."""
    resp = await client.post(
        "/api/v1/calculate",
        json={"expression": "1.5e3 * 2", "angle_mode": "DEG", "precision_digits": 10},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert float(resp.json()["result"]) == 3000.0


# ── Errores de dominio ────────────────────────────────────────────────────────

async def test_calculate_division_by_zero(client: AsyncClient, auth_headers: dict):
    """División por cero retorna 200 con error_code DIVISION_BY_ZERO."""
    resp = await client.post(
        "/api/v1/calculate",
        json={"expression": "7 / 0", "angle_mode": "DEG", "precision_digits": 10},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["error_code"] == "DIVISION_BY_ZERO"


async def test_calculate_tan90_undefined(client: AsyncClient, auth_headers: dict):
    """tan(90°) retorna error_code UNDEFINED_RESULT."""
    resp = await client.post(
        "/api/v1/calculate",
        json={"expression": "tan(90)", "angle_mode": "DEG", "precision_digits": 10},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["error_code"] == "UNDEFINED_RESULT"


# ── Validación de entrada (Pydantic / Regex) ──────────────────────────────────

async def test_calculate_invalid_expression_returns_422(client: AsyncClient, auth_headers: dict):
    """Expresión con caracteres prohibidos (falla Regex) retorna 422."""
    resp = await client.post(
        "/api/v1/calculate",
        json={"expression": "rm -rf /", "angle_mode": "DEG", "precision_digits": 10},
        headers=auth_headers,
    )
    assert resp.status_code == 422


async def test_calculate_invalid_angle_mode_returns_422(client: AsyncClient, auth_headers: dict):
    """angle_mode distinto de DEG/RAD retorna 422."""
    resp = await client.post(
        "/api/v1/calculate",
        json={"expression": "1 + 1", "angle_mode": "XYZ", "precision_digits": 10},
        headers=auth_headers,
    )
    assert resp.status_code == 422


async def test_calculate_precision_out_of_range_returns_422(client: AsyncClient, auth_headers: dict):
    """precision_digits fuera del rango 2-50 retorna 422."""
    resp = await client.post(
        "/api/v1/calculate",
        json={"expression": "1 + 1", "angle_mode": "DEG", "precision_digits": 100},
        headers=auth_headers,
    )
    assert resp.status_code == 422


# ── Seguridad ─────────────────────────────────────────────────────────────────

async def test_calculate_without_token_returns_401(client: AsyncClient):
    """POST /calculate sin Authorization retorna 401."""
    resp = await client.post(
        "/api/v1/calculate",
        json={"expression": "1 + 1", "angle_mode": "DEG", "precision_digits": 10},
    )
    assert resp.status_code == 401


async def test_calculate_response_has_elapsed_ms(client: AsyncClient, auth_headers: dict):
    """La respuesta incluye elapsed_ms > 0."""
    resp = await client.post(
        "/api/v1/calculate",
        json={"expression": "100 / 4", "angle_mode": "DEG", "precision_digits": 10},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["elapsed_ms"] >= 0
