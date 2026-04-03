import hashlib
from datetime import datetime, timedelta, timezone

from ...domain.ports.output.session_repository_port import SessionRepositoryPort

MAX_ACTIVE_SESSIONS = 5


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class ManageSessionUseCase:
    def __init__(self, repo: SessionRepositoryPort):
        self._repo = repo

    async def register(
        self,
        user_id: str,
        token: str,
        browser_agent: str,
        expire_minutes: int = 15,
    ) -> None:
        """Registra la sesión activa tras un login exitoso."""
        token_hash = _hash_token(token)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
        await self._repo.create(
            user_id=user_id,
            browser_agent=browser_agent,
            jwt_token_hash=token_hash,
            expires_at=expires_at,
        )

    async def logout(self, token: str) -> bool:
        """Invalida la sesión asociada al token. Retorna True si existía."""
        return await self._repo.invalidate(_hash_token(token))

    async def count_active(self, user_id: str) -> int:
        return await self._repo.count_active(user_id)
