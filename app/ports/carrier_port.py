from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.package import Package
from app.domain.trace import Tracer
from app.domain.zones import Zone


class CarrierUnavailableError(Exception):
    pass


# Cuanto espera un adaptador la respuesta de su transportista antes de darlo
# por caido. Vive en el puerto (no en cada adaptador) porque es parte del
# contrato: cualquier CarrierPort debe responder o fallar dentro de este plazo.
CARRIER_REQUEST_TIMEOUT_S = 2.0


@dataclass(frozen=True)
class CarrierQuote:
    amount_ars: float
    eta_days: int


class CarrierPort(ABC):
    """Puerto secundario: cada transportista real es un adaptador distinto de este contrato."""

    name: str

    @abstractmethod
    async def get_rate(self, package: Package, zone: Zone, tracer: Tracer) -> CarrierQuote: ...
