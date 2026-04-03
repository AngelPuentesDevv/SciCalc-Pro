import uuid
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class FavoriteConversionModel(Base):
    __tablename__ = "favorite_conversions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    from_unit: Mapped[str] = mapped_column(String(30), nullable=False)
    to_unit: Mapped[str] = mapped_column(String(30), nullable=False)
    category: Mapped[str] = mapped_column(String(10), nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
