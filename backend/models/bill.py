from datetime import datetime

from sqlalchemy import JSON, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base


class Bill(Base):
    __tablename__ = "bills"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    bill_name: Mapped[str] = mapped_column(String(255), nullable=False, default="Unknown Bill")
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    tax: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    raw_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="processed")
