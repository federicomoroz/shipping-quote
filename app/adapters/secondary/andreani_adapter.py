from decimal import Decimal

import httpx

from app.adapters.secondary.http_carrier_adapter import HttpCarrierAdapter
from app.ports.carrier_port import CarrierPort, CarrierQuote

CARRIER_NAME = "Andreani"
ENDPOINT_PATH = "/andreani/tarifar"


def build_andreani_adapter(client: httpx.AsyncClient) -> CarrierPort:
    return HttpCarrierAdapter(
        name=CARRIER_NAME,
        client=client,
        endpoint_path=ENDPOINT_PATH,
        build_request=lambda package, zone: {"kg": package.effective_weight_kg, "zona_andreani": zone.value},
        parse_response=lambda data: CarrierQuote(
            amount_ars=Decimal(str(data["tarifa_pesos"])), eta_days=data["eta_dias"]
        ),
    )
