"""Politica de comision propia sobre la tarifa que devuelve cada transportista.

La tarifa del carrier es un precio ajeno (viene de una API externa simulada);
esta es la unica parte del precio final que decide nuestro dominio.
"""

WEIGHT_BRACKETS: tuple[tuple[float, str], ...] = (
    (5.0, "liviano"),
    (15.0, "medio"),
    (30.0, "pesado"),
)

FEE_TABLE: dict[tuple[str, str], float] = {
    ("AMBA", "liviano"): 0.06,
    ("AMBA", "medio"): 0.08,
    ("AMBA", "pesado"): 0.10,
    ("Interior", "liviano"): 0.10,
    ("Interior", "medio"): 0.13,
    ("Interior", "pesado"): 0.16,
    ("Patagonia", "liviano"): 0.15,
    ("Patagonia", "medio"): 0.20,
    ("Patagonia", "pesado"): 0.25,
}


def weight_bracket(effective_weight_kg: float) -> str:
    for limit, bracket in WEIGHT_BRACKETS:
        if effective_weight_kg <= limit:
            return bracket
    return WEIGHT_BRACKETS[-1][1]


def apply_service_fee(carrier_amount_ars: float, zone: str, effective_weight_kg: float) -> float:
    bracket = weight_bracket(effective_weight_kg)
    markup = FEE_TABLE[(zone, bracket)]
    return round(carrier_amount_ars * (1 + markup))
