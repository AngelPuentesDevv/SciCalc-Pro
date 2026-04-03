"""
Pruebas de integración — Health check y páginas web.

Cubre:
  - src/main.py           → endpoint /health + lifespan
  - src/infrastructure/adapters/input/web_router.py → /web/login, /web/register, /web/calculator
"""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")


# ── Health ────────────────────────────────────────────────────────────────────

async def test_health_returns_ok(client: AsyncClient):
    """GET /health debe retornar 200 y status 'ok'."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "scicalc-pro"


# ── Páginas web ───────────────────────────────────────────────────────────────

async def test_web_login_page(client: AsyncClient):
    """GET /web/login debe retornar HTML 200 con formulario de login."""
    resp = await client.get("/web/login")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert b"login" in resp.content.lower()


async def test_web_register_page(client: AsyncClient):
    """GET /web/register debe retornar HTML 200 con formulario de registro."""
    resp = await client.get("/web/register")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert b"register" in resp.content.lower() or b"registro" in resp.content.lower()


async def test_web_calculator_page(client: AsyncClient):
    """GET /web/calculator debe retornar HTML 200 con la calculadora."""
    resp = await client.get("/web/calculator")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert b"calculator" in resp.content.lower() or b"calculadora" in resp.content.lower()


async def test_unknown_route_returns_404(client: AsyncClient):
    """Rutas inexistentes deben retornar 404."""
    resp = await client.get("/ruta/que/no/existe")
    assert resp.status_code == 404
