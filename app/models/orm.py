from sqlalchemy import Column, DateTime, Float, Integer, String

from app.core.database import Base


class QuoteRecord(Base):
    __tablename__ = "quote_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False)
    postal_code = Column(Integer, nullable=False)
    zone = Column(String, nullable=False)
    effective_weight_kg = Column(Float, nullable=False)
    best_carrier = Column(String, nullable=True)
    best_amount_ars = Column(Float, nullable=True)
