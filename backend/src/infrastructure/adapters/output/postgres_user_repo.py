from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ....domain.ports.output.user_repository_port import UserRepositoryPort
from ....domain.entities.user import User
from ...persistence.models.user import UserModel


class PostgresUserRepo(UserRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, user: User) -> User:
        model = UserModel(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            display_name=user.display_name,
        )
        self._session.add(model)
        await self._session.flush()
        return user

    async def get_by_id(self, user_id: str) -> User | None:
        stmt = select(UserModel).where(
            UserModel.id == user_id,
            UserModel.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(
            UserModel.email == email,
            UserModel.is_deleted.is_(False)
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def update(self, user: User) -> User:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user.id)
            .values(email=user.email, display_name=user.display_name)
        )
        await self._session.execute(stmt)
        return user

    async def delete_logical(self, user_id: str) -> bool:
        stmt = update(UserModel).where(UserModel.id == user_id).values(is_deleted=True)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    @staticmethod
    def _to_entity(m: UserModel) -> User:
        return User(
            id=m.id,
            email=m.email,
            password_hash=m.password_hash,
            display_name=m.display_name,
            created_at=m.created_at.isoformat(),
            is_deleted=m.is_deleted,
        )
