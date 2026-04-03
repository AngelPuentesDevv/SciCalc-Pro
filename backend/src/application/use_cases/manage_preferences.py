from ...infrastructure.adapters.output.postgres_preferences_repo import PostgresPreferencesRepo

_MEMORY_KEY = "memory"


class ManagePreferencesUseCase:
    def __init__(self, repo: PostgresPreferencesRepo):
        self._repo = repo

    async def get_memory(self, user_id: str) -> float | None:
        raw = await self._repo.get(user_id, _MEMORY_KEY)
        return float(raw) if raw is not None else None

    async def set_memory(self, user_id: str, value: float) -> None:
        await self._repo.set(user_id, _MEMORY_KEY, str(value))

    async def clear_memory(self, user_id: str) -> None:
        await self._repo.delete(user_id, _MEMORY_KEY)
