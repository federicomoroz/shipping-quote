from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

from app.domain.trace import TraceEntry, Tracer
from app.domain.zones import Zone


@dataclass(frozen=True)
class QuoteRequest:
    weight_kg: float
    length_cm: float
    width_cm: float
    height_cm: float
    postal_code: int


@dataclass(frozen=True)
class CarrierResult:
    carrier: str
    ok: bool
    amount_ars: Decimal | None
    eta_days: int | None
    error: str | None


@dataclass(frozen=True)
class QuoteResponse:
    zone: Zone
    effective_weight_kg: float
    results: list[CarrierResult]
    trace: list[TraceEntry]


class ShippingQuotePort(ABC):
    """Puerto primario.

    Se deja explicito, con una unica implementacion, para que el circuito
    hexagonal quede completo y visible de punta a punta: en un caso real con
    un solo caso de uso normalmente se inlinearia esta llamada en el controller.
    """

    @abstractmethod
    async def execute(self, request: QuoteRequest, tracer: Tracer) -> QuoteResponse: ...
