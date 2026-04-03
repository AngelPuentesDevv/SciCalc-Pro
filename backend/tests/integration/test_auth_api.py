"""
Pruebas de integración — Endpoints de autenticación.

Cubre:
  - POST /api/v1/auth/register
  - POST /api/v1/auth/login
  - GET  /api/v1/users/me
  - DELETE /api/v1/users/{user_id}

Clases ejercidas:
  - fastapi_router.py (register, login, get_me, delete_user)
  - auth_middleware.py (get_current_user)
  - postgres_user_repo.py (create, get_by_email, get_by_id, delete_logical)
  - manage_user.py (register, login)
  - jwt_handler.py (create_access_token, decode_token)
  - password_hasher.py (hash_password, verify_password)
  - regex_validators.py (validate_email, validate_password)
"""
import uuid
import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")
from httpx import AsyncClient


def _email():
    return f"auth_{uuid.uuid4().hex[:8]}@scicalc.test"


# ── Registro ──────────────────────────────────────────────────────────────────

async def test_register_success(client: AsyncClient):
    """Registro con datos válidos devuelve 201 con id, email y display_name."""
    email = _email()
    resp = await client.post(
        "/api/v1/auth/register",
        params={"email": email, "password": "Valid1234!", "display_name": "Tester"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == email
    assert "id" in body
    assert "display_name" in body


async def test_register_duplicate_email_returns_400(client: AsyncClient):
    """Registrar el mismo email dos veces debe retornar 400."""
    email = _email()
    params = {"email": email, "password": "Valid1234!", "display_name": "X"}
    await client.post("/api/v1/auth/register", params=params)
    resp = await client.post("/api/v1/auth/register", params=params)
    assert resp.status_code == 400
    assert "EMAIL_TAKEN" in resp.text


async def test_register_invalid_email_returns_400(client: AsyncClient):
    """Email malformado (falla Regex) devuelve 400."""
    resp = await client.post(
        "/api/v1/auth/register",
        params={"email": "no-es-un-email", "password": "Valid1234!", "display_name": "X"},
    )
    assert resp.status_code == 400


async def test_register_weak_password_returns_400(client: AsyncClient):
    """Contraseña sin mayúscula ni número devuelve 400."""
    resp = await client.post(
        "/api/v1/auth/register",
        params={"email": _email(), "password": "sinmayus", "display_name": "X"},
    )
    assert resp.status_code == 400


# ── Login ─────────────────────────────────────────────────────────────────────

async def test_login_success_returns_tokens(client: AsyncClient):
    """Login exitoso retorna access_token, refresh_token y token_type='bearer'."""
    email = _email()
    password = "Login1234!"
    await client.post(
        "/api/v1/auth/register",
        params={"email": email, "password": password, "display_name": "L"},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


async def test_login_wrong_password_returns_401(client: AsyncClient):
    """Contraseña incorrecta retorna 401."""
    email = _email()
    await client.post(
        "/api/v1/auth/register",
        params={"email": email, "password": "Correct1!", "display_name": "L"},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "Wrong999!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 401


async def test_login_nonexistent_user_returns_401(client: AsyncClient):
    """Login con email que no existe retorna 401."""
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "noexiste@scicalc.test", "password": "NoExist1!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 401


# ── /users/me ─────────────────────────────────────────────────────────────────

async def test_get_me_returns_user_data(client: AsyncClient, auth_headers: dict, test_user: dict):
    """GET /users/me con token válido retorna user_id y email."""
    resp = await client.get("/api/v1/users/me", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == test_user["email"]
    assert "user_id" in body


async def test_get_me_without_token_returns_401(client: AsyncClient):
    """GET /users/me sin Authorization retorna 401."""
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 401


async def test_get_me_invalid_token_returns_401(client: AsyncClient):
    """GET /users/me con token basura retorna 401."""
    resp = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer esto.no.es.jwt"},
    )
    assert resp.status_code == 401


# ── DELETE /users/{id} ────────────────────────────────────────────────────────

async def test_delete_user_success(client: AsyncClient):
    """DELETE /users/{id} con token válido retorna 200 y deleted=True."""
    email = _email()
    reg = await client.post(
        "/api/v1/auth/register",
        params={"email": email, "password": "Del1Test!", "display_name": "Del"},
    )
    user_id = reg.json()["id"]
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "Del1Test!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login.json()["access_token"]

    resp = await client.delete(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True


async def test_delete_nonexistent_user_returns_404(client: AsyncClient, auth_headers: dict):
    """DELETE /users/id_fantasma retorna 404."""
    fake_id = str(uuid.uuid4())
    resp = await client.delete(f"/api/v1/users/{fake_id}", headers=auth_headers)
    assert resp.status_code == 404
