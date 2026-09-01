from sqlalchemy import Column, DateTime, Float, Integer, Numeric, String

from app.core.database import Base

# ARS hasta 10 digitos enteros + 2 decimales; de sobra para este dominio.
MONEY_PRECISION = 10
MONEY_SCALE = 2


class QuoteRecord(Base):
    __tablename__ = "quote_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False)
    postal_code = Column(Integer, nullable=False)
    zone = Column(String, nullable=False)
    effective_weight_kg = Column(Float, nullable=False)
    best_carrier = Column(String, nullable=True)
    best_amount_ars = Column(Numeric(MONEY_PRECISION, MONEY_SCALE), nullable=True)
