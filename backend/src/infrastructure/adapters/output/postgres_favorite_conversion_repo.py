from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....domain.ports.output.favorite_conversion_repository_port import (
    FavoriteConversion,
    FavoriteConversionRepositoryPort,
)
from ...persistence.models.favorite_conversion import FavoriteConversionModel


class PostgresFavoriteConversionRepo(FavoriteConversionRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_by_user(self, user_id: str) -> list[FavoriteConversion]:
        result = await self._session.execute(
            select(FavoriteConversionModel).where(
                FavoriteConversionModel.user_id == user_id,
                FavoriteConversionModel.is_deleted.is_(False),
            )
        )
        return [
            FavoriteConversion(
                id=row.id,
                user_id=row.user_id,
                from_unit=row.from_unit,
                to_unit=row.to_unit,
                category=row.category,
            )
            for row in result.scalars().all()
        ]

    async def create(self, fav: FavoriteConversion) -> FavoriteConversion:
        row = FavoriteConversionModel(
            id=fav.id,
            user_id=fav.user_id,
            from_unit=fav.from_unit,
            to_unit=fav.to_unit,
            category=fav.category,
        )
        self._session.add(row)
        await self._session.flush()
        return fav

    async def delete(self, fav_id: str, user_id: str) -> bool:
        result = await self._session.execute(
            select(FavoriteConversionModel).where(
                FavoriteConversionModel.id == fav_id,
                FavoriteConversionModel.user_id == user_id,
                FavoriteConversionModel.is_deleted.is_(False),
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            return False
        row.is_deleted = True
        await self._session.flush()
        return True
