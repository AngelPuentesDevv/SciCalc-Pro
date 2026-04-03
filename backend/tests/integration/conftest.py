"""
Fixtures compartidos para pruebas de integración.

Usa httpx.AsyncClient con ASGITransport — no requiere servidor live.
Requiere PostgreSQL corriendo (DATABASE_URL en el entorno).
Ejecutar con:
    pytest tests/integration/ -v
"""
import sys
import uuid

# Windows: asyncpg requiere SelectorEventLoop
if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import pytest
from httpx import AsyncClient, ASGITransport

from src.main import app


def _unique_email() -> str:
    """Genera un email único para evitar colisiones entre tests."""
    return f"inttest_{uuid.uuid4().hex[:8]}@scicalc.test"


@pytest.fixture(scope="session")
async def client():
    """
    Cliente HTTP que habla directamente con la app ASGI (sin servidor real).
    scope="module" → el lifespan (create_all / engine.dispose) corre UNA sola vez
    por archivo de tests, evitando el bug de asyncpg en Windows donde
    Connection._cancel deja coroutines pendientes al cerrar el loop entre tests.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user(client: AsyncClient):
    """
    Crea un usuario de prueba único, devuelve sus credenciales y token,
    y lo elimina al finalizar el test.
    """
    email = _unique_email()
    password = "IntTest1!"
    display_name = "Integration Tester"

    # Registro
    reg = await client.post(
        "/api/v1/auth/register",
        params={"email": email, "password": password, "display_name": display_name},
    )
    assert reg.status_code == 201, f"Registro falló: {reg.text}"
    user_id = reg.json()["id"]

    # Login para obtener token
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    yield {
        "id": user_id,
        "email": email,
        "password": password,
        "display_name": display_name,
        "token": token,
    }

    # Teardown — borrado lógico del usuario
    await client.delete(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )


@pytest.fixture
def auth_headers(test_user: dict) -> dict:
    """Cabecera Authorization lista para usar en peticiones protegidas."""
    return {"Authorization": f"Bearer {test_user['token']}"}
