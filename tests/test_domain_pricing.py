from decimal import Decimal

import pytest

from app.domain.pricing import apply_service_fee, weight_bracket
from app.domain.zones import Zone


@pytest.mark.parametrize(
    "weight,expected_bracket",
    [(3, "liviano"), (5, "liviano"), (10, "medio"), (15, "medio"), (25, "pesado"), (30, "pesado")],
)
def test_weight_bracket(weight, expected_bracket):
    assert weight_bracket(weight) == expected_bracket


def test_apply_service_fee_amba_liviano():
    assert apply_service_fee(Decimal("1000"), Zone.AMBA, 3) == Decimal("1060")


def test_apply_service_fee_patagonia_pesado():
    assert apply_service_fee(Decimal("1000"), Zone.PATAGONIA, 28) == Decimal("1250")


def test_apply_service_fee_rounds_half_up_not_banker():
    # 102.80 * 1.25 = 128.50 exacto. round() nativo de Python redondearia al
    # par mas cercano (128, banker's rounding); ROUND_HALF_UP redondea a 129,
    # que es el comportamiento esperado para un monto de dinero.
    assert apply_service_fee(Decimal("102.80"), Zone.PATAGONIA, 28) == Decimal("129")
