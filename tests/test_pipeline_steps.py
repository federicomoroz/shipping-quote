import pytest

from app.domain.package import PackageTooHeavyError
from app.domain.trace import TraceRecorder
from app.ports.shipping_quote_port import QuoteRequest
from app.use_cases.pipeline import ClassifyZoneStep, QuoteContext, ValidateEligibilityStep


def _request(**overrides):
    defaults = dict(
        weight_kg=4, length_cm=30, width_cm=20, height_cm=15, declared_value_ars=25000, postal_code=1425
    )
    defaults.update(overrides)
    return QuoteRequest(**defaults)


async def test_validate_eligibility_step_sets_package_and_traces():
    ctx = QuoteContext(request=_request(), tracer=TraceRecorder())
    await ValidateEligibilityStep().execute(ctx)
    assert ctx.package is not None
    assert ctx.package.effective_weight_kg == 4
    assert ctx.tracer.entries[-1].step == "dominio"
    assert ctx.tracer.entries[-1].label == "ValidateEligibilityStep"


async def test_validate_eligibility_step_raises_for_heavy_package():
    ctx = QuoteContext(request=_request(weight_kg=50), tracer=TraceRecorder())
    with pytest.raises(PackageTooHeavyError):
        await ValidateEligibilityStep().execute(ctx)


async def test_classify_zone_step_sets_zone_and_traces():
    ctx = QuoteContext(request=_request(postal_code=8400), tracer=TraceRecorder())
    await ClassifyZoneStep().execute(ctx)
    assert ctx.zone == "Patagonia"
    assert ctx.tracer.entries[-1].label == "ClassifyZoneStep"
