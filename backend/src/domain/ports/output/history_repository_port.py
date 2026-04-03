from abc import ABC, abstractmethod
from ...entities.calculation import Calculation


class HistoryRepositoryPort(ABC):
    @abstractmethod
    async def save(self, calc: Calculation) -> Calculation: ...

    @abstractmethod
    async def get_by_user(self, user_id: str, limit: int = 50) -> list[Calculation]: ...

    @abstractmethod
    async def delete_logical(self, calc_id: str) -> bool: ...

    @abstractmethod
    async def count_active(self, user_id: str) -> int: ...

    @abstractmethod
    async def get_oldest_active(self, user_id: str) -> Calculation | None: ...
