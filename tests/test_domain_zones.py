import pytest

from app.domain.zones import InvalidPostalCodeError, classify_zone


@pytest.mark.parametrize(
    "postal_code,expected_zone",
    [
        (1425, "AMBA"),
        (1900, "Interior"),
        (8400, "Patagonia"),
        (9500, "Interior"),
    ],
)
def test_classify_zone(postal_code, expected_zone):
    assert classify_zone(postal_code) == expected_zone


def test_rejects_out_of_range_postal_code():
    with pytest.raises(InvalidPostalCodeError):
        classify_zone(500)
