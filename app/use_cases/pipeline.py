from dataclasses import dataclass
from typing import Protocol

from app.domain.package import Package, build_package
from app.domain.trace import Tracer
from app.domain.zones import Zone, classify_zone
from app.ports.shipping_quote_port import QuoteRequest


@dataclass
class QuoteContext:
    request: QuoteRequest
    tracer: Tracer
    package: Package | None = None
    zone: Zone | None = None


class PipelineStep(Protocol):
    async def execute(self, ctx: QuoteContext) -> None: ...


class ValidateEligibilityStep:
    """Dominio: valida el paquete y calcula el peso efectivo (real vs. volumetrico)."""

    async def execute(self, ctx: QuoteContext) -> None:
        r = ctx.request
        ctx.package = build_package(
            r.weight_kg, r.length_cm, r.width_cm, r.height_cm, r.declared_value_ars
        )
        ctx.tracer.mark(
            "dominio",
            "ValidateEligibilityStep",
            f"peso real {r.weight_kg:.1f}kg / volumetrico {ctx.package.volumetric_weight_kg:.1f}kg "
            f"-> efectivo {ctx.package.effective_weight_kg:.1f}kg",
        )


class ClassifyZoneStep:
    """Dominio: mapea el codigo postal a una zona logistica."""

    async def execute(self, ctx: QuoteContext) -> None:
        ctx.zone = classify_zone(ctx.request.postal_code)
        ctx.tracer.mark(
            "dominio", "ClassifyZoneStep", f"CP {ctx.request.postal_code} -> zona {ctx.zone.value}"
        )
