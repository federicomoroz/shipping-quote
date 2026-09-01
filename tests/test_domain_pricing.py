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
    assert apply_service_fee(1000, Zone.AMBA, 3) == 1060


def test_apply_service_fee_patagonia_pesado():
    assert apply_service_fee(1000, Zone.PATAGONIA, 28) == 1250
