import pytest

from app.domain.zones import InvalidPostalCodeError, Zone, classify_zone


@pytest.mark.parametrize(
    "postal_code,expected_zone",
    [
        (1425, Zone.AMBA),
        (1900, Zone.INTERIOR),
        (8400, Zone.PATAGONIA),
        (9500, Zone.INTERIOR),
    ],
)
def test_classify_zone(postal_code, expected_zone):
    assert classify_zone(postal_code) == expected_zone


def test_rejects_out_of_range_postal_code():
    with pytest.raises(InvalidPostalCodeError):
        classify_zone(500)
