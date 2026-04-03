from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....domain.entities.profile import Profile
from ....domain.ports.output.profile_repository_port import ProfileRepositoryPort
from ...persistence.models.profile import ProfileModel


class PostgresProfileRepo(ProfileRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_user(self, user_id: str) -> Profile | None:
        result = await self._session.execute(
            select(ProfileModel).where(
                ProfileModel.user_id == user_id,
                ProfileModel.is_deleted.is_(False),
            )
        )
        row = result.scalars().first()
        if row is None:
            return None
        return Profile(
            id=row.id,
            user_id=row.user_id,
            avatar_url=row.avatar_url,
            preferred_precision=row.preferred_precision,
            angle_mode=row.angle_mode,
            theme=row.theme,
            updated_at=row.updated_at.isoformat() if row.updated_at else None,
        )

    async def upsert(self, profile: Profile) -> Profile:
        result = await self._session.execute(
            select(ProfileModel).where(ProfileModel.user_id == profile.user_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            row = ProfileModel(
                id=profile.id,
                user_id=profile.user_id,
            )
            self._session.add(row)

        row.avatar_url = profile.avatar_url
        row.preferred_precision = profile.preferred_precision
        row.angle_mode = profile.angle_mode
        row.theme = profile.theme
        row.is_deleted = False
        await self._session.flush()
        await self._session.refresh(row)

        profile.id = row.id
        profile.updated_at = row.updated_at.isoformat() if row.updated_at else None
        return profile
