from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.package import Package
from app.domain.trace import Tracer


class CarrierUnavailableError(Exception):
    pass


@dataclass(frozen=True)
class CarrierQuote:
    amount_ars: float
    eta_days: int


class CarrierPort(ABC):
    """Puerto secundario: cada transportista real es un adaptador distinto de este contrato."""

    name: str

    @abstractmethod
    async def get_rate(self, package: Package, zone: str, tracer: Tracer) -> CarrierQuote: ...
