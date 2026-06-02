from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class CachedTransaction(Base):
    __tablename__ = "cached_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    firefly_transaction_id: Mapped[str] = mapped_column(String(128), index=True)
    description: Mapped[str] = mapped_column(Text)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency_code: Mapped[str] = mapped_column(String(8), default="EUR")
    category_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    budget_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    transaction_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    transaction_date: Mapped[datetime] = mapped_column(DateTime, index=True)
    synced_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
