"""
TC-INT-008: Pruebas de integración — CRUD de conversiones favoritas (B3).

Cubre GET/POST/DELETE /api/v1/conversions/favorites con PostgreSQL real.
ISO 29119 — Test Integration 008
"""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_favorites_list_empty(client: AsyncClient, test_user, auth_headers):
    """TC-INT-008a: Lista de favoritos vacía por defecto."""
    resp = await client.get("/api/v1/conversions/favorites", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_favorites_create(client: AsyncClient, test_user, auth_headers):
    """TC-INT-008b: POST crea un favorito y retorna sus campos."""
    resp = await client.post(
        "/api/v1/conversions/favorites",
        json={"from_unit": "km", "to_unit": "m", "category": "LENGTH"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["from_unit"] == "km"
    assert body["to_unit"] == "m"
    assert body["category"] == "LENGTH"
    assert "id" in body


async def test_favorites_list_after_create(client: AsyncClient, test_user, auth_headers):
    """TC-INT-008c: Tras crear un favorito, aparece en la lista."""
    await client.post(
        "/api/v1/conversions/favorites",
        json={"from_unit": "kg", "to_unit": "g", "category": "MASS"},
        headers=auth_headers,
    )
    resp = await client.get("/api/v1/conversions/favorites", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


async def test_favorites_delete(client: AsyncClient, test_user, auth_headers):
    """TC-INT-008d: DELETE elimina el favorito por id (borrado lógico)."""
    create = await client.post(
        "/api/v1/conversions/favorites",
        json={"from_unit": "L", "to_unit": "mL", "category": "VOLUME"},
        headers=auth_headers,
    )
    fav_id = create.json()["id"]

    del_resp = await client.delete(f"/api/v1/conversions/favorites/{fav_id}", headers=auth_headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["deleted"] is True


async def test_favorites_delete_not_found(client: AsyncClient, test_user, auth_headers):
    """TC-INT-008e: DELETE con id inexistente retorna 404."""
    resp = await client.delete(
        "/api/v1/conversions/favorites/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert resp.status_code == 404


async def test_favorites_invalid_category(client: AsyncClient, test_user, auth_headers):
    """TC-INT-008f: category inválida retorna 400."""
    resp = await client.post(
        "/api/v1/conversions/favorites",
        json={"from_unit": "x", "to_unit": "y", "category": "INVALID"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


async def test_favorites_requires_auth(client: AsyncClient):
    """TC-INT-008g: Sin token retorna 401/403."""
    resp = await client.get("/api/v1/conversions/favorites")
    assert resp.status_code in (401, 403)
