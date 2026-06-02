from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    type: Mapped[str] = mapped_column(String(64), index=True)
    current_value: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency_code: Mapped[str] = mapped_column(String(8), default="EUR")
    risk_level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    liquidity_level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
