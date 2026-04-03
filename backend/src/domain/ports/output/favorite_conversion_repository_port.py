from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import uuid

_VALID_CATEGORIES = {"LENGTH", "MASS", "TEMP", "VOLUME", "SPEED"}


@dataclass
class FavoriteConversion:
    user_id: str
    from_unit: str
    to_unit: str
    category: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_deleted: bool = False


class FavoriteConversionRepositoryPort(ABC):

    @abstractmethod
    async def list_by_user(self, user_id: str) -> list[FavoriteConversion]: ...

    @abstractmethod
    async def create(self, fav: FavoriteConversion) -> FavoriteConversion: ...

    @abstractmethod
    async def delete(self, fav_id: str, user_id: str) -> bool: ...
