from decimal import Decimal

from app.domain.trace import TraceRecorder
from app.domain.zones import Zone
from app.ports.carrier_port import CarrierPort, CarrierQuote, CarrierUnavailableError
from app.ports.quote_history_port import DEFAULT_HISTORY_LIMIT, QuoteHistoryPort, QuoteRecordData
from app.ports.shipping_quote_port import QuoteRequest
from app.use_cases.quote_shipping import QuoteShippingUseCase


class _FakeCarrier(CarrierPort):
    def __init__(self, name, amount_ars=None, eta_days=None, fails=False):
        self.name = name
        self._amount_ars = amount_ars
        self._eta_days = eta_days
        self._fails = fails

    async def get_rate(self, package, zone, tracer):
        tracer.mark("adaptador_secundario", self.name, "fake")
        if self._fails:
            raise CarrierUnavailableError(f"{self.name} no disponible")
        return CarrierQuote(amount_ars=self._amount_ars, eta_days=self._eta_days)


class _FakeHistory(QuoteHistoryPort):
    def __init__(self):
        self.saved: list[QuoteRecordData] = []

    async def save(self, record: QuoteRecordData) -> None:
        self.saved.append(record)

    async def list_recent(self, limit: int = DEFAULT_HISTORY_LIMIT):
        return list(reversed(self.saved))[:limit]


def _request(**overrides):
    defaults = dict(weight_kg=4, length_cm=30, width_cm=20, height_cm=15, postal_code=1425)
    defaults.update(overrides)
    return QuoteRequest(**defaults)


async def test_use_case_returns_all_carrier_results():
    carriers = [
        _FakeCarrier("A", amount_ars=Decimal("1000"), eta_days=3),
        _FakeCarrier("B", amount_ars=Decimal("1200"), eta_days=2),
    ]
    history = _FakeHistory()
    use_case = QuoteShippingUseCase(carriers=carriers, history=history)

    response = await use_case.execute(_request(), TraceRecorder())

    assert response.zone == Zone.AMBA
    assert len(response.results) == 2
    assert all(r.ok for r in response.results)
    assert history.saved


async def test_use_case_tolerates_one_failing_carrier():
    carriers = [
        _FakeCarrier("Confiable", amount_ars=Decimal("1000"), eta_days=3),
        _FakeCarrier("Caido", fails=True),
    ]
    use_case = QuoteShippingUseCase(carriers=carriers, history=_FakeHistory())

    response = await use_case.execute(_request(), TraceRecorder())

    ok_results = [r for r in response.results if r.ok]
    failed_results = [r for r in response.results if not r.ok]
    assert len(ok_results) == 1
    assert len(failed_results) == 1
    assert failed_results[0].error == "Caido no disponible"


async def test_use_case_trace_covers_full_circuit():
    carriers = [_FakeCarrier("A", amount_ars=Decimal("1000"), eta_days=3)]
    use_case = QuoteShippingUseCase(carriers=carriers, history=_FakeHistory())

    response = await use_case.execute(_request(), TraceRecorder())

    steps = {entry.step for entry in response.trace}
    assert {"caso_de_uso", "dominio", "puerto_secundario", "adaptador_secundario"} <= steps
