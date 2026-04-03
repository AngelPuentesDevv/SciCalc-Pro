"""Prueba 5: CRUD de historial con borrado lógico y FIFO — RF-003."""
import pytest
from src.application.use_cases.manage_history import ManageHistoryUseCase
from src.domain.entities.calculation import Calculation


@pytest.mark.asyncio
async def test_save_stores_record(history_repo):
    uc = ManageHistoryUseCase(history_repo)
    calc = Calculation(expression="5+3", result="8", user_id="user-1")
    saved = await uc.save(calc)
    assert saved.id == calc.id
    assert saved.is_deleted is False


@pytest.mark.asyncio
async def test_get_by_user_returns_active_only(history_repo):
    uc = ManageHistoryUseCase(history_repo)
    c1 = Calculation(expression="1+1", result="2", user_id="user-1")
    c2 = Calculation(expression="2+2", result="4", user_id="user-1")
    await uc.save(c1)
    await uc.save(c2)
    await uc.delete(c1.id)  # borrado lógico

    items = await uc.get_by_user("user-1")
    assert len(items) == 1
    assert items[0].id == c2.id


@pytest.mark.asyncio
async def test_delete_is_logical_not_physical(history_repo):
    uc = ManageHistoryUseCase(history_repo)
    calc = Calculation(expression="3*3", result="9", user_id="user-1")
    await uc.save(calc)
    deleted = await uc.delete(calc.id)

    assert deleted is True
    # El registro sigue en el store pero con is_deleted=True
    assert history_repo._store[calc.id].is_deleted is True


@pytest.mark.asyncio
async def test_fifo_limit_50(history_repo):
    """Al llegar a 50 registros activos, el 51° borra el más antiguo."""
    uc = ManageHistoryUseCase(history_repo)
    first_id = None
    for i in range(50):
        calc = Calculation(
            expression=f"{i}+1",
            result=str(i + 1),
            user_id="user-fifo",
            created_at=f"2026-01-01T00:00:{i:02d}+00:00",
        )
        if i == 0:
            first_id = calc.id
        await uc.save(calc)

    # Agregar el 51°
    c51 = Calculation(expression="51+1", result="52", user_id="user-fifo",
                      created_at="2026-01-01T00:01:00+00:00")
    await uc.save(c51)

    active = await uc.get_by_user("user-fifo", limit=100)
    assert len(active) == 50
    # El primero (más antiguo) debe estar borrado
    assert history_repo._store[first_id].is_deleted is True


@pytest.mark.asyncio
async def test_different_users_isolated(history_repo):
    uc = ManageHistoryUseCase(history_repo)
    await uc.save(Calculation(expression="1+1", result="2", user_id="user-A"))
    await uc.save(Calculation(expression="2+2", result="4", user_id="user-B"))

    items_a = await uc.get_by_user("user-A")
    items_b = await uc.get_by_user("user-B")
    assert len(items_a) == 1
    assert len(items_b) == 1
    assert items_a[0].expression == "1+1"
    assert items_b[0].expression == "2+2"
