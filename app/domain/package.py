from dataclasses import dataclass

MAX_EFFECTIVE_WEIGHT_KG = 30.0
VOLUMETRIC_DIVISOR = 5000.0  # cm3 por kg, divisor estandar de la industria


class PackageTooHeavyError(Exception):
    pass


@dataclass(frozen=True)
class Package:
    weight_kg: float
    length_cm: float
    width_cm: float
    height_cm: float

    @property
    def volumetric_weight_kg(self) -> float:
        return (self.length_cm * self.width_cm * self.height_cm) / VOLUMETRIC_DIVISOR

    @property
    def effective_weight_kg(self) -> float:
        return max(self.weight_kg, self.volumetric_weight_kg)


def build_package(weight_kg: float, length_cm: float, width_cm: float, height_cm: float) -> Package:
    package = Package(weight_kg, length_cm, width_cm, height_cm)
    if package.effective_weight_kg > MAX_EFFECTIVE_WEIGHT_KG:
        raise PackageTooHeavyError(
            f"peso efectivo {package.effective_weight_kg:.1f}kg supera el maximo "
            f"de {MAX_EFFECTIVE_WEIGHT_KG:.0f}kg (real {weight_kg:.1f}kg, "
            f"volumetrico {package.volumetric_weight_kg:.1f}kg)"
        )
    return package
