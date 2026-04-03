import pytest
from unittest.mock import AsyncMock
from src.infrastructure.adapters.input.math_engine_adapter import MpMathCalculationEngine
from src.domain.entities.calculation import Calculation
from src.domain.ports.output.history_repository_port import HistoryRepositoryPort
from src.domain.ports.output.user_repository_port import UserRepositoryPort


@pytest.fixture
def engine_dep():
    return MpMathCalculationEngine()


class InMemoryHistoryRepo(HistoryRepositoryPort):
    def __init__(self):
        self._store: dict[str, Calculation] = {}

    async def save(self, calc: Calculation) -> Calculation:
        self._store[calc.id] = calc
        return calc

    async def get_by_user(self, user_id: str, limit: int = 50) -> list[Calculation]:
        items = [c for c in self._store.values() if c.user_id == user_id and not c.is_deleted]
        items.sort(key=lambda c: c.created_at, reverse=True)
        return items[:limit]

    async def delete_logical(self, calc_id: str) -> bool:
        if calc_id in self._store:
            self._store[calc_id].is_deleted = True
            return True
        return False

    async def count_active(self, user_id: str) -> int:
        return sum(1 for c in self._store.values() if c.user_id == user_id and not c.is_deleted)

    async def get_oldest_active(self, user_id: str) -> Calculation | None:
        items = [c for c in self._store.values() if c.user_id == user_id and not c.is_deleted]
        if not items:
            return None
        return min(items, key=lambda c: c.created_at)


@pytest.fixture
def history_repo():
    return InMemoryHistoryRepo()


class InMemoryUserRepo(UserRepositoryPort):
    def __init__(self):
        self._store: dict[str, object] = {}

    async def create(self, user):
        self._store[user.id] = user
        return user

    async def get_by_id(self, user_id: str):
        return self._store.get(user_id)

    async def get_by_email(self, email: str):
        return next((u for u in self._store.values() if u.email == email and not u.is_deleted), None)

    async def update(self, user):
        self._store[user.id] = user
        return user

    async def delete_logical(self, user_id: str) -> bool:
        if user_id in self._store:
            self._store[user_id].is_deleted = True
            return True
        return False


@pytest.fixture
def user_repo():
    return InMemoryUserRepo()
