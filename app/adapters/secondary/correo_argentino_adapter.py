from decimal import Decimal

import httpx

from app.adapters.secondary.http_carrier_adapter import HttpCarrierAdapter
from app.ports.carrier_port import CarrierPort, CarrierQuote

CARRIER_NAME = "Correo Argentino"
ENDPOINT_PATH = "/correo-argentino/cotizar"


def build_correo_argentino_adapter(client: httpx.AsyncClient) -> CarrierPort:
    return HttpCarrierAdapter(
        name=CARRIER_NAME,
        client=client,
        endpoint_path=ENDPOINT_PATH,
        build_request=lambda package, zone: {"peso_kg": package.effective_weight_kg, "zona": zone.value},
        parse_response=lambda data: CarrierQuote(
            amount_ars=Decimal(str(data["monto"])), eta_days=data["dias_habiles"]
        ),
    )
