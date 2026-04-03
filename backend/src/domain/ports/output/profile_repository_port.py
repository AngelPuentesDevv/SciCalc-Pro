from abc import ABC, abstractmethod
from ...entities.profile import Profile


class ProfileRepositoryPort(ABC):

    @abstractmethod
    async def get_by_user(self, user_id: str) -> Profile | None: ...

    @abstractmethod
    async def upsert(self, profile: Profile) -> Profile: ...
