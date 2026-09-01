from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class QuoteRecordData:
    created_at: datetime
    postal_code: int
    zone: str
    effective_weight_kg: float
    best_carrier: str | None
    best_amount_ars: float | None
    id: int | None = None


class QuoteHistoryPort(ABC):
    """Puerto secundario #2: persistencia de cotizaciones, intercambiable como cualquier otro adaptador."""

    @abstractmethod
    async def save(self, record: QuoteRecordData) -> None: ...

    @abstractmethod
    async def list_recent(self, limit: int = 20) -> list[QuoteRecordData]: ...
