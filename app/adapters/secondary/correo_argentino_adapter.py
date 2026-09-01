import httpx

from app.domain.package import Package
from app.domain.trace import Tracer
from app.ports.carrier_port import CarrierPort, CarrierQuote, CarrierUnavailableError


class CorreoArgentinoAdapter(CarrierPort):
    name = "Correo Argentino"

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def get_rate(self, package: Package, zone: str, tracer: Tracer) -> CarrierQuote:
        tracer.mark("adaptador_secundario", self.name, "traduciendo Package -> {peso_kg, zona}")
        try:
            response = await self._client.post(
                "/correo-argentino/cotizar",
                json={"peso_kg": package.effective_weight_kg, "zona": zone},
                timeout=2.0,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            tracer.mark("salida", self.name, f"la API devolvio {exc.response.status_code}")
            raise CarrierUnavailableError(f"Correo Argentino no disponible ({exc.response.status_code})") from exc
        except httpx.TimeoutException as exc:
            tracer.mark("salida", self.name, "timeout")
            raise CarrierUnavailableError("Correo Argentino no respondio a tiempo") from exc

        data = response.json()
        tracer.mark("salida", self.name, f"monto={data['monto']} dias_habiles={data['dias_habiles']}")
        return CarrierQuote(amount_ars=data["monto"], eta_days=data["dias_habiles"])
