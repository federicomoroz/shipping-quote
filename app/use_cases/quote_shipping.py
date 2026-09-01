import asyncio
from datetime import datetime, timezone

from app.domain.pricing import apply_service_fee
from app.domain.trace import Tracer
from app.ports.carrier_port import CarrierPort, CarrierUnavailableError
from app.ports.quote_history_port import QuoteHistoryPort, QuoteRecordData
from app.ports.shipping_quote_port import CarrierResult, QuoteRequest, QuoteResponse, ShippingQuotePort
from app.use_cases.pipeline import ClassifyZoneStep, PipelineStep, QuoteContext, ValidateEligibilityStep


class QuoteShippingUseCase(ShippingQuotePort):
    def __init__(self, carriers: list[CarrierPort], history: QuoteHistoryPort) -> None:
        self._carriers = carriers
        self._history = history
        self._steps: list[PipelineStep] = [ValidateEligibilityStep(), ClassifyZoneStep()]

    async def execute(self, request: QuoteRequest, tracer: Tracer) -> QuoteResponse:
        tracer.mark("caso_de_uso", "QuoteShippingUseCase", "inicio")

        ctx = QuoteContext(request=request, tracer=tracer)
        for step in self._steps:
            await step.execute(ctx)
        assert ctx.package is not None and ctx.zone is not None

        results = list(await asyncio.gather(*(self._quote_from(carrier, ctx) for carrier in self._carriers)))

        successful = [r for r in results if r.ok]
        best = min(successful, key=lambda r: r.amount_ars) if successful else None
        await self._history.save(
            QuoteRecordData(
                created_at=datetime.now(timezone.utc),
                postal_code=request.postal_code,
                zone=ctx.zone,
                effective_weight_kg=ctx.package.effective_weight_kg,
                best_carrier=best.carrier if best else None,
                best_amount_ars=best.amount_ars if best else None,
            )
        )

        return QuoteResponse(
            zone=ctx.zone,
            effective_weight_kg=ctx.package.effective_weight_kg,
            results=results,
            trace=list(tracer.entries),
        )

    async def _quote_from(self, carrier: CarrierPort, ctx: QuoteContext) -> CarrierResult:
        assert ctx.package is not None and ctx.zone is not None
        ctx.tracer.mark("puerto_secundario", "CarrierPort", f"-> {carrier.name}")
        try:
            quote = await carrier.get_rate(ctx.package, ctx.zone, ctx.tracer)
        except CarrierUnavailableError as exc:
            return CarrierResult(carrier=carrier.name, ok=False, amount_ars=None, eta_days=None, error=str(exc))

        final_amount = apply_service_fee(quote.amount_ars, ctx.zone, ctx.package.effective_weight_kg)
        ctx.tracer.mark(
            "dominio",
            "FeePolicy",
            f"{carrier.name}: ${quote.amount_ars:.0f} + comision -> ${final_amount:.0f}",
        )
        return CarrierResult(carrier=carrier.name, ok=True, amount_ars=final_amount, eta_days=quote.eta_days, error=None)
