from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from app.domain.zones import Zone


DEFAULT_HISTORY_LIMIT = 20


@dataclass(frozen=True)
class QuoteRecordData:
    created_at: datetime
    postal_code: int
    zone: Zone
    effective_weight_kg: float
    best_carrier: str | None
    best_amount_ars: float | None
    id: int | None = None


class QuoteHistoryPort(ABC):
    """Puerto secundario #2: persistencia, intercambiable como cualquier otro adaptador."""

    @abstractmethod
    async def save(self, record: QuoteRecordData) -> None: ...

    @abstractmethod
    async def list_recent(self, limit: int = DEFAULT_HISTORY_LIMIT) -> list[QuoteRecordData]: ...
