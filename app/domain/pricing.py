"""Politica de comision propia sobre la tarifa que devuelve cada transportista.

La tarifa del carrier es un precio ajeno (viene de una API externa simulada);
esta es la unica parte del precio final que decide nuestro dominio. Se opera
en `Decimal` -no `float`- porque es dinero: evita tanto el error de
representacion binaria como el redondeo "banker's rounding" sorpresivo de
`round()`, y se redondea de forma explicita con `ROUND_HALF_UP`.
"""

from decimal import ROUND_HALF_UP, Decimal
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

FEE_TABLE: dict[tuple[Zone, WeightBracket], Decimal] = {
    (Zone.AMBA, WeightBracket.LIVIANO): Decimal("0.06"),
    (Zone.AMBA, WeightBracket.MEDIO): Decimal("0.08"),
    (Zone.AMBA, WeightBracket.PESADO): Decimal("0.10"),
    (Zone.INTERIOR, WeightBracket.LIVIANO): Decimal("0.10"),
    (Zone.INTERIOR, WeightBracket.MEDIO): Decimal("0.13"),
    (Zone.INTERIOR, WeightBracket.PESADO): Decimal("0.16"),
    (Zone.PATAGONIA, WeightBracket.LIVIANO): Decimal("0.15"),
    (Zone.PATAGONIA, WeightBracket.MEDIO): Decimal("0.20"),
    (Zone.PATAGONIA, WeightBracket.PESADO): Decimal("0.25"),
}

# Los montos finales se cotizan en pesos enteros, sin centavos.
PESO_QUANTUM = Decimal("1")


def weight_bracket(effective_weight_kg: float) -> WeightBracket:
    for limit, bracket in WEIGHT_BRACKETS:
        if effective_weight_kg <= limit:
            return bracket
    # Inalcanzable mientras `build_package` siga rechazando > 30kg: si esto
    # dispara, la invariante de dominio se rompio en otro lado.
    raise ValueError(f"peso efectivo {effective_weight_kg}kg no entra en ningun bracket definido")


def apply_service_fee(carrier_amount_ars: Decimal, zone: Zone, effective_weight_kg: float) -> Decimal:
    bracket = weight_bracket(effective_weight_kg)
    markup = FEE_TABLE[(zone, bracket)]
    final_amount = carrier_amount_ars * (Decimal("1") + markup)
    return final_amount.quantize(PESO_QUANTUM, rounding=ROUND_HALF_UP)
