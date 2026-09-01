import pytest

from app.domain.package import MAX_EFFECTIVE_WEIGHT_KG, PackageTooHeavyError, build_package


def test_effective_weight_uses_real_weight_when_higher():
    package = build_package(weight_kg=10, length_cm=10, width_cm=10, height_cm=10, declared_value_ars=1000)
    assert package.volumetric_weight_kg == pytest.approx(0.2)
    assert package.effective_weight_kg == 10


def test_effective_weight_uses_volumetric_when_higher():
    package = build_package(weight_kg=1, length_cm=50, width_cm=50, height_cm=50, declared_value_ars=1000)
    assert package.volumetric_weight_kg == pytest.approx(25.0)
    assert package.effective_weight_kg == pytest.approx(25.0)


def test_rejects_package_over_max_effective_weight():
    with pytest.raises(PackageTooHeavyError):
        build_package(
            weight_kg=MAX_EFFECTIVE_WEIGHT_KG + 1,
            length_cm=10,
            width_cm=10,
            height_cm=10,
            declared_value_ars=1000,
        )


def test_accepts_package_at_max_effective_weight():
    package = build_package(
        weight_kg=MAX_EFFECTIVE_WEIGHT_KG, length_cm=1, width_cm=1, height_cm=1, declared_value_ars=1000
    )
    assert package.effective_weight_kg == MAX_EFFECTIVE_WEIGHT_KG
