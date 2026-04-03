from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ....domain.ports.output.sync_repository_port import AuditRepositoryPort
from ...persistence.models.sync_log import AuditLogModel


class PostgresAuditRepo(AuditRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def log_action(
        self,
        user_id: str,
        entity_type: str,
        entity_id: str,
        action: str,
        status: str = "success",
        payload: Any = None,
    ) -> None:
        model = AuditLogModel(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            status=status,
            payload=payload,
        )
        self._session.add(model)
        await self._session.flush()
