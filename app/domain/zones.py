"""Clasificacion de codigo postal a zona logistica.

Tabla simplificada con fines de demo (no es la zonificacion real y completa de
Correo Argentino), pero es data-driven: agregar o ajustar una zona es una fila
nueva, no una rama de if/elif.
"""

ZONE_TABLE: tuple[tuple[int, int, str], ...] = (
    (1000, 1499, "AMBA"),       # CABA
    (1500, 1599, "Interior"),
    (1600, 1899, "AMBA"),       # GBA
    (1900, 8299, "Interior"),
    (8300, 9420, "Patagonia"),
    (9421, 9999, "Interior"),
)


class InvalidPostalCodeError(Exception):
    pass


def classify_zone(postal_code: int) -> str:
    for start, end, zone in ZONE_TABLE:
        if start <= postal_code <= end:
            return zone
    raise InvalidPostalCodeError(
        f"codigo postal {postal_code} fuera de rango (1000-9999)"
    )
