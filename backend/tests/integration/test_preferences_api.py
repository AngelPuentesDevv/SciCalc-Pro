"""
TC-INT-005: Pruebas de integración — Endpoints de memoria de usuario (RF-004).

Cubre GET/POST/DELETE /api/v1/preferences/memory con autenticación JWT real
y PostgreSQL (tabla user_preferences, upsert ON CONFLICT DO UPDATE).
ISO 29119 — Test Integration 005
"""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")


# ── TC-INT-005a: memoria vacía por defecto ────────────────────────────────────

async def test_memory_get_empty_by_default(client: AsyncClient, test_user, auth_headers):
    """TC-INT-005a: Un usuario nuevo tiene memoria nula por defecto."""
    resp = await client.get("/api/v1/preferences/memory", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["value"] is None


# ── TC-INT-005b: guardar valor de memoria ────────────────────────────────────

async def test_memory_set_value(client: AsyncClient, test_user, auth_headers):
    """TC-INT-005b: POST /preferences/memory guarda el valor y lo retorna."""
    resp = await client.post(
        "/api/v1/preferences/memory",
        json={"value": 42.5},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["value"] == 42.5


# ── TC-INT-005c: recuperar valor guardado ────────────────────────────────────

async def test_memory_get_after_set(client: AsyncClient, test_user, auth_headers):
    """TC-INT-005c: GET /preferences/memory retorna el valor guardado previamente."""
    await client.post(
        "/api/v1/preferences/memory",
        json={"value": 99.0},
        headers=auth_headers,
    )
    resp = await client.get("/api/v1/preferences/memory", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["value"] == 99.0


# ── TC-INT-005d: upsert — sobreescribe valor existente ───────────────────────

async def test_memory_upsert_overwrites(client: AsyncClient, test_user, auth_headers):
    """TC-INT-005d: Llamar POST dos veces sobreescribe el valor (upsert, no duplicado)."""
    await client.post("/api/v1/preferences/memory", json={"value": 10.0}, headers=auth_headers)
    await client.post("/api/v1/preferences/memory", json={"value": 20.0}, headers=auth_headers)
    resp = await client.get("/api/v1/preferences/memory", headers=auth_headers)
    assert resp.json()["value"] == 20.0


# ── TC-INT-005e: limpiar memoria ─────────────────────────────────────────────

async def test_memory_clear(client: AsyncClient, test_user, auth_headers):
    """TC-INT-005e: DELETE /preferences/memory borra el valor; GET retorna null."""
    await client.post("/api/v1/preferences/memory", json={"value": 5.0}, headers=auth_headers)
    del_resp = await client.delete("/api/v1/preferences/memory", headers=auth_headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["cleared"] is True

    get_resp = await client.get("/api/v1/preferences/memory", headers=auth_headers)
    assert get_resp.json()["value"] is None


# ── TC-INT-005f: valor no numérico retorna 422 ───────────────────────────────

async def test_memory_set_invalid_value(client: AsyncClient, test_user, auth_headers):
    """TC-INT-005f: POST con value no numérico retorna 422 Unprocessable Entity."""
    resp = await client.post(
        "/api/v1/preferences/memory",
        json={"value": "not-a-number"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


# ── TC-INT-005g: sin autenticación retorna 401/403 ───────────────────────────

async def test_memory_requires_auth(client: AsyncClient):
    """TC-INT-005g: GET sin token retorna 401 o 403."""
    resp = await client.get("/api/v1/preferences/memory")
    assert resp.status_code in (401, 403)
