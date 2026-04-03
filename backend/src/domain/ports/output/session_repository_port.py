from abc import ABC, abstractmethod
from datetime import datetime


class SessionRepositoryPort(ABC):

    @abstractmethod
    async def create(
        self,
        user_id: str,
        browser_agent: str,
        jwt_token_hash: str,
        expires_at: datetime,
    ) -> str:
        """Registra una nueva sesión activa. Retorna el id de sesión."""
        ...

    @abstractmethod
    async def invalidate(self, jwt_token_hash: str) -> bool:
        """Marca la sesión como inactiva (logout). Retorna True si existía."""
        ...

    @abstractmethod
    async def count_active(self, user_id: str) -> int:
        """Retorna el número de sesiones activas del usuario."""
        ...
