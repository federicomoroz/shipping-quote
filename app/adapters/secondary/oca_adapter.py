from decimal import Decimal

import httpx

from app.adapters.secondary.http_carrier_adapter import HttpCarrierAdapter
from app.ports.carrier_port import CarrierPort, CarrierQuote

CARRIER_NAME = "OCA"
ENDPOINT_PATH = "/oca/quote"


def build_oca_adapter(client: httpx.AsyncClient) -> CarrierPort:
    return HttpCarrierAdapter(
        name=CARRIER_NAME,
        client=client,
        endpoint_path=ENDPOINT_PATH,
        build_request=lambda package, zone: {"weight": package.effective_weight_kg, "region": zone.value},
        parse_response=lambda data: CarrierQuote(
            amount_ars=Decimal(str(data["price"])), eta_days=data["estimated_delivery"]
        ),
    )
