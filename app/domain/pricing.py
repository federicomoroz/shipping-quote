"""Politica de comision propia sobre la tarifa que devuelve cada transportista.

La tarifa del carrier es un precio ajeno (viene de una API externa simulada);
esta es la unica parte del precio final que decide nuestro dominio.
"""

from enum import Enum

from app.domain.zones import Zone


class WeightBracket(str, Enum):
    LIVIANO = "liviano"
    MEDIO = "medio"
    PESADO = "pesado"


WEIGHT_BRACKETS: tuple[tuple[float, WeightBracket], ...] = (
    (5.0, WeightBracket.LIVIANO),
    (15.0, WeightBracket.MEDIO),
    (30.0, WeightBracket.PESADO),
)

FEE_TABLE: dict[tuple[Zone, WeightBracket], float] = {
    (Zone.AMBA, WeightBracket.LIVIANO): 0.06,
    (Zone.AMBA, WeightBracket.MEDIO): 0.08,
    (Zone.AMBA, WeightBracket.PESADO): 0.10,
    (Zone.INTERIOR, WeightBracket.LIVIANO): 0.10,
    (Zone.INTERIOR, WeightBracket.MEDIO): 0.13,
    (Zone.INTERIOR, WeightBracket.PESADO): 0.16,
    (Zone.PATAGONIA, WeightBracket.LIVIANO): 0.15,
    (Zone.PATAGONIA, WeightBracket.MEDIO): 0.20,
    (Zone.PATAGONIA, WeightBracket.PESADO): 0.25,
}


def weight_bracket(effective_weight_kg: float) -> WeightBracket:
    for limit, bracket in WEIGHT_BRACKETS:
        if effective_weight_kg <= limit:
            return bracket
    # Inalcanzable mientras `build_package` siga rechazando > 30kg: si esto
    # dispara, la invariante de dominio se rompio en otro lado.
    raise ValueError(f"peso efectivo {effective_weight_kg}kg no entra en ningun bracket definido")


def apply_service_fee(carrier_amount_ars: float, zone: Zone, effective_weight_kg: float) -> float:
    bracket = weight_bracket(effective_weight_kg)
    markup = FEE_TABLE[(zone, bracket)]
    return round(carrier_amount_ars * (1 + markup))
