from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Date, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class Liability(Base):
    __tablename__ = "liabilities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    type: Mapped[str] = mapped_column(String(64), default="loan")
    lender: Mapped[str | None] = mapped_column(String(255), nullable=True)
    initial_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    remaining_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    interest_rate: Mapped[Decimal | None] = mapped_column(Numeric(6, 3), nullable=True)
    monthly_payment: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
