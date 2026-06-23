import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker


BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is required. Add it to backend/.env or deployment environment variables.")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from models.bill import Bill  # noqa: F401

    Base.metadata.create_all(bind=engine)
    ensure_bill_schema()


def ensure_bill_schema() -> None:
    statements = [
        "ALTER TABLE bills ADD COLUMN IF NOT EXISTS filename VARCHAR(255) NOT NULL DEFAULT ''",
        "ALTER TABLE bills ADD COLUMN IF NOT EXISTS file_type VARCHAR(50) NOT NULL DEFAULT ''",
        "ALTER TABLE bills ADD COLUMN IF NOT EXISTS detected_type VARCHAR(80) NOT NULL DEFAULT ''",
        "ALTER TABLE bills ADD COLUMN IF NOT EXISTS confidence NUMERIC(5, 2) NOT NULL DEFAULT 0",
        "ALTER TABLE bills ADD COLUMN IF NOT EXISTS vendor VARCHAR(255) NOT NULL DEFAULT ''",
        "ALTER TABLE bills ADD COLUMN IF NOT EXISTS invoice_number VARCHAR(120) NOT NULL DEFAULT ''",
        "ALTER TABLE bills ADD COLUMN IF NOT EXISTS bill_date VARCHAR(80) NOT NULL DEFAULT ''",
        "ALTER TABLE bills ADD COLUMN IF NOT EXISTS customer VARCHAR(255) NOT NULL DEFAULT ''",
        "ALTER TABLE bills ADD COLUMN IF NOT EXISTS buyer VARCHAR(255) NOT NULL DEFAULT ''",
        "ALTER TABLE bills ADD COLUMN IF NOT EXISTS phone VARCHAR(80) NOT NULL DEFAULT ''",
        "ALTER TABLE bills ADD COLUMN IF NOT EXISTS gst_number VARCHAR(120) NOT NULL DEFAULT ''",
        "ALTER TABLE bills ADD COLUMN IF NOT EXISTS gst_amount NUMERIC(12, 2) NOT NULL DEFAULT 0",
        "ALTER TABLE bills ADD COLUMN IF NOT EXISTS discount NUMERIC(12, 2) NOT NULL DEFAULT 0",
        "ALTER TABLE bills ADD COLUMN IF NOT EXISTS payment_method VARCHAR(120) NOT NULL DEFAULT ''",
        "ALTER TABLE bills ADD COLUMN IF NOT EXISTS rows_count INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE bills ADD COLUMN IF NOT EXISTS columns_json JSONB NOT NULL DEFAULT '[]'::jsonb",
        "ALTER TABLE bills ADD COLUMN IF NOT EXISTS rows_json JSONB NOT NULL DEFAULT '[]'::jsonb",
        "ALTER TABLE bills ADD COLUMN IF NOT EXISTS fields_json JSONB NOT NULL DEFAULT '{}'::jsonb",
        "ALTER TABLE bills ADD COLUMN IF NOT EXISTS extracted_text TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE bills ADD COLUMN IF NOT EXISTS preview_url VARCHAR(500) NOT NULL DEFAULT ''",
        "ALTER TABLE bills ADD COLUMN IF NOT EXISTS file_path VARCHAR(500) NOT NULL DEFAULT ''",
    ]
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
