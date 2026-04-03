from ...domain.ports.output.history_repository_port import HistoryRepositoryPort
from ...domain.entities.calculation import Calculation

MAX_HISTORY = 50


class ManageHistoryUseCase:
    def __init__(self, repo: HistoryRepositoryPort):
        self._repo = repo

    async def save(self, calc: Calculation) -> Calculation:
        """Guarda y aplica FIFO: si hay 50 activos, borra el más antiguo primero."""
        count = await self._repo.count_active(calc.user_id)
        if count >= MAX_HISTORY:
            oldest = await self._repo.get_oldest_active(calc.user_id)
            if oldest:
                await self._repo.delete_logical(oldest.id)
        return await self._repo.save(calc)

    async def get_by_user(self, user_id: str, limit: int = MAX_HISTORY) -> list[Calculation]:
        return await self._repo.get_by_user(user_id, limit)

    async def delete(self, calc_id: str) -> bool:
        return await self._repo.delete_logical(calc_id)
