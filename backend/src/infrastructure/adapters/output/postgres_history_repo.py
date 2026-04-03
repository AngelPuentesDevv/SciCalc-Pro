from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from ....domain.ports.output.history_repository_port import HistoryRepositoryPort
from ....domain.entities.calculation import Calculation
from ...persistence.models.calculation_history import CalculationHistoryModel


class PostgresHistoryRepo(HistoryRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, calc: Calculation) -> Calculation:
        model = CalculationHistoryModel(
            id=calc.id,
            user_id=calc.user_id,
            expression=calc.expression,
            result=calc.result,
            precision_digits=calc.precision_digits,
            is_deleted=calc.is_deleted,
            sync_version=calc.sync_version,
            device_id=calc.device_id,
        )
        self._session.add(model)
        await self._session.flush()
        return calc

    async def get_by_user(self, user_id: str, limit: int = 50) -> list[Calculation]:
        stmt = (
            select(CalculationHistoryModel)
            .where(
                CalculationHistoryModel.user_id == user_id,
                CalculationHistoryModel.is_deleted.is_(False),
            )
            .order_by(CalculationHistoryModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [self._to_entity(r) for r in rows]

    async def delete_logical(self, calc_id: str) -> bool:
        stmt = (
            update(CalculationHistoryModel)
            .where(CalculationHistoryModel.id == calc_id)
            .values(is_deleted=True)
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def count_active(self, user_id: str) -> int:
        stmt = select(func.count()).where(
            CalculationHistoryModel.user_id == user_id,
            CalculationHistoryModel.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_oldest_active(self, user_id: str) -> Calculation | None:
        stmt = (
            select(CalculationHistoryModel)
            .where(
                CalculationHistoryModel.user_id == user_id,
                CalculationHistoryModel.is_deleted.is_(False),
            )
            .order_by(CalculationHistoryModel.created_at.asc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    @staticmethod
    def _to_entity(m: CalculationHistoryModel) -> Calculation:
        return Calculation(
            id=m.id,
            user_id=m.user_id,
            expression=m.expression,
            result=m.result,
            precision_digits=m.precision_digits,
            created_at=m.created_at.isoformat(),
            is_deleted=m.is_deleted,
            sync_version=m.sync_version,
            device_id=m.device_id,
        )
