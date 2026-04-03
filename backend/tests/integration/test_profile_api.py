"""
TC-INT-006: Pruebas de integración — CRUD de perfil de usuario (B1).

Cubre GET /api/v1/profile y PUT /api/v1/profile con PostgreSQL real.
ISO 29119 — Test Integration 006
"""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_profile_get_defaults(client: AsyncClient, test_user, auth_headers):
    """TC-INT-006a: GET /profile retorna valores por defecto (precision=10, DEG, LIGHT)."""
    resp = await client.get("/api/v1/profile", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["preferred_precision"] == 10
    assert body["angle_mode"] == "DEG"
    assert body["theme"] == "LIGHT"
    assert body["user_id"] == test_user["id"]


async def test_profile_update_precision(client: AsyncClient, test_user, auth_headers):
    """TC-INT-006b: PUT /profile actualiza preferred_precision."""
    resp = await client.put(
        "/api/v1/profile",
        json={"preferred_precision": 25},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["preferred_precision"] == 25


async def test_profile_update_angle_mode(client: AsyncClient, test_user, auth_headers):
    """TC-INT-006c: PUT /profile actualiza angle_mode a RAD."""
    resp = await client.put("/api/v1/profile", json={"angle_mode": "RAD"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["angle_mode"] == "RAD"


async def test_profile_update_theme(client: AsyncClient, test_user, auth_headers):
    """TC-INT-006d: PUT /profile actualiza theme a DARK."""
    resp = await client.put("/api/v1/profile", json={"theme": "DARK"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["theme"] == "DARK"


async def test_profile_invalid_precision_returns_400(client: AsyncClient, test_user, auth_headers):
    """TC-INT-006e: precision fuera de rango [2-50] retorna 400."""
    resp = await client.put("/api/v1/profile", json={"preferred_precision": 100}, headers=auth_headers)
    assert resp.status_code == 400


async def test_profile_invalid_angle_mode_returns_400(client: AsyncClient, test_user, auth_headers):
    """TC-INT-006f: angle_mode inválido retorna 400."""
    resp = await client.put("/api/v1/profile", json={"angle_mode": "GRAD"}, headers=auth_headers)
    assert resp.status_code == 400


async def test_profile_requires_auth(client: AsyncClient):
    """TC-INT-006g: Sin token retorna 401/403."""
    resp = await client.get("/api/v1/profile")
    assert resp.status_code in (401, 403)
