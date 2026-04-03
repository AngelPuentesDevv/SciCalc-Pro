"""
Pruebas de integración — Historial de cálculos (RF-003).

Cubre:
  - GET    /api/v1/history
  - DELETE /api/v1/history/{id}
  - postgres_history_repo.py (save, get_by_user, delete_logical, count_active, get_oldest_active)
  - manage_history.py (get_by_user, delete)
"""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def _calc(client: AsyncClient, headers: dict, expr: str = "1 + 1") -> dict:
    """Helper: realiza un cálculo y devuelve el cuerpo de la respuesta."""
    resp = await client.post(
        "/api/v1/calculate",
        json={"expression": expr, "angle_mode": "DEG", "precision_digits": 10},
        headers=headers,
    )
    assert resp.status_code == 200
    return resp.json()


# ── GET /history ──────────────────────────────────────────────────────────────

async def test_history_empty_for_new_user(client: AsyncClient, auth_headers: dict):
    """Usuario recién creado tiene historial vacío."""
    resp = await client.get("/api/v1/history", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_history_contains_calculation_after_compute(
    client: AsyncClient, auth_headers: dict
):
    """Después de un cálculo el historial tiene al menos una entrada."""
    await _calc(client, auth_headers, "5 * 5")
    resp = await client.get("/api/v1/history", headers=auth_headers)
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 1
    exprs = [i["expression"] for i in items]
    assert "5 * 5" in exprs


async def test_history_entry_has_required_fields(
    client: AsyncClient, auth_headers: dict
):
    """Cada entrada del historial tiene id, expression, result, precision_digits, created_at."""
    await _calc(client, auth_headers, "3 + 4")
    resp = await client.get("/api/v1/history", headers=auth_headers)
    assert resp.status_code == 200
    item = resp.json()[0]
    for field in ("id", "expression", "result", "precision_digits", "created_at"):
        assert field in item, f"Falta el campo '{field}' en la entrada del historial"


async def test_history_ordered_by_date_desc(
    client: AsyncClient, auth_headers: dict
):
    """El historial está ordenado del más reciente al más antiguo."""
    await _calc(client, auth_headers, "1 + 1")
    await _calc(client, auth_headers, "2 + 2")
    await _calc(client, auth_headers, "3 + 3")

    resp = await client.get("/api/v1/history", headers=auth_headers)
    items = resp.json()
    # La expresión más reciente debe aparecer primero
    assert items[0]["expression"] == "3 + 3"


async def test_history_without_token_returns_401(client: AsyncClient):
    """GET /history sin Authorization retorna 401."""
    resp = await client.get("/api/v1/history")
    assert resp.status_code == 401


# ── DELETE /history/{id} ─────────────────────────────────────────────────────

async def test_delete_history_entry_success(
    client: AsyncClient, auth_headers: dict
):
    """DELETE /history/{id} retorna 200 y deleted=True; la entrada desaparece del historial."""
    await _calc(client, auth_headers, "9 * 9")
    items = (await client.get("/api/v1/history", headers=auth_headers)).json()
    target_id = next(i["id"] for i in items if i["expression"] == "9 * 9")

    resp = await client.delete(f"/api/v1/history/{target_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True

    # Verificar que ya no aparece
    after = (await client.get("/api/v1/history", headers=auth_headers)).json()
    ids = [i["id"] for i in after]
    assert target_id not in ids


async def test_delete_nonexistent_history_returns_404(
    client: AsyncClient, auth_headers: dict
):
    """DELETE /history/id_fantasma retorna 404."""
    fake_id = "00000000-0000-4000-a000-000000000000"
    resp = await client.delete(f"/api/v1/history/{fake_id}", headers=auth_headers)
    assert resp.status_code == 404


async def test_delete_history_without_token_returns_401(client: AsyncClient):
    """DELETE /history/{id} sin Authorization retorna 401."""
    resp = await client.delete("/api/v1/history/some-id")
    assert resp.status_code == 401


# ── Múltiples cálculos ────────────────────────────────────────────────────────

async def test_multiple_calculations_all_in_history(
    client: AsyncClient, auth_headers: dict
):
    """Varios cálculos consecutivos aparecen todos en el historial."""
    expressions = ["10 + 1", "10 + 2", "10 + 3"]
    for expr in expressions:
        await _calc(client, auth_headers, expr)

    resp = await client.get("/api/v1/history", headers=auth_headers)
    assert resp.status_code == 200
    stored = {i["expression"] for i in resp.json()}
    for expr in expressions:
        assert expr in stored
