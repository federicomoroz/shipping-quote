import httpx

from app.domain.package import Package
from app.domain.trace import Tracer
from app.ports.carrier_port import CarrierPort, CarrierQuote, CarrierUnavailableError


class AndreaniAdapter(CarrierPort):
    name = "Andreani"

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def get_rate(self, package: Package, zone: str, tracer: Tracer) -> CarrierQuote:
        tracer.mark("adaptador_secundario", self.name, "traduciendo Package -> {kg, zona_andreani}")
        try:
            response = await self._client.post(
                "/andreani/tarifar",
                json={"kg": package.effective_weight_kg, "zona_andreani": zone},
                timeout=2.0,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            tracer.mark("salida", self.name, "sin respuesta")
            raise CarrierUnavailableError("Andreani no disponible") from exc

        data = response.json()
        tracer.mark("salida", self.name, f"tarifa_pesos={data['tarifa_pesos']} eta_dias={data['eta_dias']}")
        return CarrierQuote(amount_ars=data["tarifa_pesos"], eta_days=data["eta_dias"])
