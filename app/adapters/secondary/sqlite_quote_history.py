import app.core.database as database
from app.models.orm import QuoteRecord
from app.ports.quote_history_port import QuoteHistoryPort, QuoteRecordData


class SQLiteQuoteHistory(QuoteHistoryPort):
    """Importa el modulo `database`, no `SessionLocal` directo: los tests parchean
    `database.SessionLocal` y necesitan que este adapter lo resuelva en cada
    llamada, no que lo capture una sola vez al importarse."""

    async def save(self, record: QuoteRecordData) -> None:
        db = database.SessionLocal()
        try:
            db.add(
                QuoteRecord(
                    created_at=record.created_at,
                    postal_code=record.postal_code,
                    zone=record.zone,
                    effective_weight_kg=record.effective_weight_kg,
                    best_carrier=record.best_carrier,
                    best_amount_ars=record.best_amount_ars,
                )
            )
            db.commit()
        finally:
            db.close()

    async def list_recent(self, limit: int = 20) -> list[QuoteRecordData]:
        db = database.SessionLocal()
        try:
            rows = db.query(QuoteRecord).order_by(QuoteRecord.id.desc()).limit(limit).all()
            return [
                QuoteRecordData(
                    created_at=row.created_at,
                    postal_code=row.postal_code,
                    zone=row.zone,
                    effective_weight_kg=row.effective_weight_kg,
                    best_carrier=row.best_carrier,
                    best_amount_ars=row.best_amount_ars,
                    id=row.id,
                )
                for row in rows
            ]
        finally:
            db.close()
