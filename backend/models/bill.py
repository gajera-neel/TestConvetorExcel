from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base


class Bill(Base):
    __tablename__ = "bills"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    bill_name: Mapped[str] = mapped_column(String(255), nullable=False, default="Unknown Bill")
    filename: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    file_type: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    detected_type: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    confidence: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    vendor: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    invoice_number: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    bill_date: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    customer: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    buyer: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    phone: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    gst_number: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    tax: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    gst_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    discount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    payment_method: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    rows_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    columns_json: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    rows_json: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    fields_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    extracted_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    preview_url: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    raw_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="processed")
