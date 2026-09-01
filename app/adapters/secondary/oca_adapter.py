import httpx

from app.domain.package import Package
from app.domain.trace import Tracer
from app.ports.carrier_port import CarrierPort, CarrierQuote, CarrierUnavailableError


class OCAAdapter(CarrierPort):
    name = "OCA"

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def get_rate(self, package: Package, zone: str, tracer: Tracer) -> CarrierQuote:
        tracer.mark("adaptador_secundario", self.name, "traduciendo Package -> {weight, region}")
        try:
            response = await self._client.post(
                "/oca/quote",
                json={"weight": package.effective_weight_kg, "region": zone},
                timeout=2.0,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            tracer.mark("salida", self.name, "sin respuesta")
            raise CarrierUnavailableError("OCA no disponible") from exc

        data = response.json()
        tracer.mark("salida", self.name, f"price={data['price']} estimated_delivery={data['estimated_delivery']}")
        return CarrierQuote(amount_ars=data["price"], eta_days=data["estimated_delivery"])
