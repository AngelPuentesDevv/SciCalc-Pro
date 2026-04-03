import re
from ...domain.entities.profile import Profile
from ...domain.ports.output.profile_repository_port import ProfileRepositoryPort
from ...domain.exceptions.domain_exceptions import DomainError

_ANGLE_MODES = {"DEG", "RAD"}
_THEMES = {"LIGHT", "DARK"}


class ManageProfileUseCase:
    def __init__(self, repo: ProfileRepositoryPort):
        self._repo = repo

    async def get(self, user_id: str) -> Profile:
        profile = await self._repo.get_by_user(user_id)
        if profile is None:
            profile = Profile(user_id=user_id)
        return profile

    async def update(
        self,
        user_id: str,
        preferred_precision: int | None = None,
        angle_mode: str | None = None,
        theme: str | None = None,
        avatar_url: str | None = None,
    ) -> Profile:
        profile = await self.get(user_id)

        if preferred_precision is not None:
            if not (2 <= preferred_precision <= 50):
                raise DomainError("preferred_precision debe estar entre 2 y 50", "INVALID_PRECISION")
            profile.preferred_precision = preferred_precision

        if angle_mode is not None:
            if angle_mode.upper() not in _ANGLE_MODES:
                raise DomainError("angle_mode debe ser DEG o RAD", "INVALID_ANGLE_MODE")
            profile.angle_mode = angle_mode.upper()

        if theme is not None:
            if theme.upper() not in _THEMES:
                raise DomainError("theme debe ser LIGHT o DARK", "INVALID_THEME")
            profile.theme = theme.upper()

        if avatar_url is not None:
            profile.avatar_url = avatar_url

        return await self._repo.upsert(profile)
