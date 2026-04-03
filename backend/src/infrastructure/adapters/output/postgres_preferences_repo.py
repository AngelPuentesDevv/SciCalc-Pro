from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ...persistence.models.user_preference import UserPreferenceModel


class PostgresPreferencesRepo:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, user_id: str, key: str) -> str | None:
        stmt = select(UserPreferenceModel).where(
            UserPreferenceModel.user_id == user_id,
            UserPreferenceModel.key == key,
            UserPreferenceModel.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return row.value if row else None

    async def set(self, user_id: str, key: str, value: str) -> None:
        stmt = (
            insert(UserPreferenceModel)
            .values(
                user_id=user_id,
                key=key,
                value=value,
                is_deleted=False,
                updated_at=datetime.now(timezone.utc),
            )
            .on_conflict_do_update(
                constraint="uq_user_pref_key",
                set_={"value": value, "is_deleted": False, "updated_at": datetime.now(timezone.utc)},
            )
        )
        await self._session.execute(stmt)

    async def delete(self, user_id: str, key: str) -> None:
        stmt = (
            update(UserPreferenceModel)
            .where(
                UserPreferenceModel.user_id == user_id,
                UserPreferenceModel.key == key,
            )
            .values(is_deleted=True)
        )
        await self._session.execute(stmt)
