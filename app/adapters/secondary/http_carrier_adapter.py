import logging
from typing import Callable

import httpx

from app.domain.package import Package
from app.domain.trace import Tracer
from app.domain.zones import Zone
from app.ports.carrier_port import CARRIER_REQUEST_TIMEOUT_S, CarrierPort, CarrierQuote, CarrierUnavailableError

logger = logging.getLogger(__name__)

BuildRequest = Callable[[Package, Zone], dict]
ParseResponse = Callable[[dict], CarrierQuote]


class HttpCarrierAdapter(CarrierPort):
    """CarrierPort generico para cualquier transportista que hable HTTP+JSON.

    Cada transportista real solo aporta *datos*: su endpoint y como traducir
    Package/Zone a su request, y su response a un CarrierQuote. El timeout, el
    manejo de errores y la traza son identicos para cualquiera de ellos y
    viven una sola vez aca (composicion), en vez de repetirse por herencia
    en tres clases casi identicas.
    """

    def __init__(
        self,
        name: str,
        client: httpx.AsyncClient,
        endpoint_path: str,
        build_request: BuildRequest,
        parse_response: ParseResponse,
    ) -> None:
        self.name = name
        self._client = client
        self._endpoint_path = endpoint_path
        self._build_request = build_request
        self._parse_response = parse_response

    async def get_rate(self, package: Package, zone: Zone, tracer: Tracer) -> CarrierQuote:
        tracer.mark("adaptador_secundario", self.name, f"traduciendo Package -> POST {self._endpoint_path}")
        try:
            response = await self._client.post(
                self._endpoint_path,
                json=self._build_request(package, zone),
                timeout=CARRIER_REQUEST_TIMEOUT_S,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            tracer.mark("salida", self.name, f"la API devolvio {exc.response.status_code}")
            logger.warning("%s no disponible: HTTP %s", self.name, exc.response.status_code)
            raise CarrierUnavailableError(f"{self.name} no disponible ({exc.response.status_code})") from exc
        except httpx.TimeoutException as exc:
            tracer.mark("salida", self.name, "timeout")
            logger.warning("%s no respondio a tiempo", self.name)
            raise CarrierUnavailableError(f"{self.name} no respondio a tiempo") from exc

        data = response.json()
        quote = self._parse_response(data)
        tracer.mark("salida", self.name, f"respuesta: {data}")
        return quote
