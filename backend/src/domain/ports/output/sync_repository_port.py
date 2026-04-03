from abc import ABC, abstractmethod
from typing import Any


class AuditRepositoryPort(ABC):
    """Puerto de auditoría — registra acciones sobre entidades del sistema."""

    @abstractmethod
    async def log_action(
        self,
        user_id: str,
        entity_type: str,
        entity_id: str,
        action: str,
        status: str = "success",
        payload: Any = None,
    ) -> None: ...
