"""Clasificacion de codigo postal a zona logistica.

Tabla simplificada con fines de demo (no es la zonificacion real y completa de
Correo Argentino), pero es data-driven: agregar o ajustar una zona es una fila
nueva, no una rama de if/elif. `Zone` es la unica fuente de verdad de los
nombres de zona validos: todo el resto del codigo (fee table, adaptadores)
importa este enum en vez de repetir los strings.
"""

from enum import Enum


class Zone(str, Enum):
    AMBA = "AMBA"
    INTERIOR = "Interior"
    PATAGONIA = "Patagonia"


ZONE_TABLE: tuple[tuple[int, int, Zone], ...] = (
    (1000, 1499, Zone.AMBA),       # CABA
    (1500, 1599, Zone.INTERIOR),
    (1600, 1899, Zone.AMBA),       # GBA
    (1900, 8299, Zone.INTERIOR),
    (8300, 9420, Zone.PATAGONIA),
    (9421, 9999, Zone.INTERIOR),
)

MIN_POSTAL_CODE = ZONE_TABLE[0][0]
MAX_POSTAL_CODE = ZONE_TABLE[-1][1]


class InvalidPostalCodeError(Exception):
    pass


def classify_zone(postal_code: int) -> Zone:
    for start, end, zone in ZONE_TABLE:
        if start <= postal_code <= end:
            return zone
    raise InvalidPostalCodeError(
        f"codigo postal {postal_code} fuera de rango ({MIN_POSTAL_CODE}-{MAX_POSTAL_CODE})"
    )
