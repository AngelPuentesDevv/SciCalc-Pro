"""
TC-INT-007: Pruebas de integración — Gestión de sesiones (B2).

Cubre POST /auth/login (registro de sesión) y POST /auth/logout (invalidación).
ISO 29119 — Test Integration 007
"""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_login_registers_session(client: AsyncClient, test_user):
    """TC-INT-007a: El login registra una sesión activa — retorna access_token."""
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": test_user["email"], "password": test_user["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


async def test_logout_invalidates_session(client: AsyncClient, test_user):
    """TC-INT-007b: POST /auth/logout con token válido retorna logged_out=True."""
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": test_user["email"], "password": test_user["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login.json()["access_token"]

    resp = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["logged_out"] is True


async def test_logout_requires_auth(client: AsyncClient):
    """TC-INT-007c: /auth/logout sin token retorna 401/403."""
    resp = await client.post("/api/v1/auth/logout")
    assert resp.status_code in (401, 403)
