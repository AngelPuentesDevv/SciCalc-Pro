from ...domain.ports.output.favorite_conversion_repository_port import (
    FavoriteConversion,
    FavoriteConversionRepositoryPort,
    _VALID_CATEGORIES,
)
from ...domain.exceptions.domain_exceptions import DomainError


class ManageFavoriteConversionsUseCase:
    def __init__(self, repo: FavoriteConversionRepositoryPort):
        self._repo = repo

    async def list(self, user_id: str) -> list[FavoriteConversion]:
        return await self._repo.list_by_user(user_id)

    async def create(
        self,
        user_id: str,
        from_unit: str,
        to_unit: str,
        category: str,
    ) -> FavoriteConversion:
        if category.upper() not in _VALID_CATEGORIES:
            raise DomainError(
                f"category debe ser uno de: {', '.join(_VALID_CATEGORIES)}",
                "INVALID_CATEGORY",
            )
        fav = FavoriteConversion(
            user_id=user_id,
            from_unit=from_unit.strip(),
            to_unit=to_unit.strip(),
            category=category.upper(),
        )
        return await self._repo.create(fav)

    async def delete(self, fav_id: str, user_id: str) -> bool:
        return await self._repo.delete(fav_id, user_id)
