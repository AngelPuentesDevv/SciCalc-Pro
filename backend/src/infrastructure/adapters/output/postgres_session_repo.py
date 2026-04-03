from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ....domain.ports.output.session_repository_port import SessionRepositoryPort
from ...persistence.models.session import SessionModel


class PostgresSessionRepo(SessionRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(
        self,
        user_id: str,
        browser_agent: str,
        jwt_token_hash: str,
        expires_at: datetime,
    ) -> str:
        row = SessionModel(
            user_id=user_id,
            browser_agent=browser_agent,
            jwt_token_hash=jwt_token_hash,
            expires_at=expires_at,
        )
        self._session.add(row)
        await self._session.flush()
        return row.id

    async def invalidate(self, jwt_token_hash: str) -> bool:
        result = await self._session.execute(
            select(SessionModel).where(
                SessionModel.jwt_token_hash == jwt_token_hash,
                SessionModel.is_active.is_(True),
            )
        )
        row = result.scalars().first()
        if row is None:
            return False
        row.is_active = False
        row.is_deleted = True
        await self._session.flush()
        return True

    async def count_active(self, user_id: str) -> int:
        result = await self._session.execute(
            select(func.count()).where(
                SessionModel.user_id == user_id,
                SessionModel.is_active.is_(True),
                SessionModel.is_deleted.is_(False),
            )
        )
        return result.scalar_one()
