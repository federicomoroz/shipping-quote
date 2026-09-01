import pytest

from app.adapters.secondary.andreani_adapter import AndreaniAdapter
from app.adapters.secondary.correo_argentino_adapter import CorreoArgentinoAdapter
from app.adapters.secondary.oca_adapter import OCAAdapter
from app.core.http_client import build_carrier_client
from app.domain.package import build_package
from app.domain.trace import TraceRecorder
from app.external_mocks.carrier_mocks import mocks_app
from app.ports.carrier_port import CarrierQuote, CarrierUnavailableError


@pytest.fixture
async def carrier_client():
    client = build_carrier_client(mocks_app)
    yield client
    await client.aclose()


def _package():
    return build_package(weight_kg=4, length_cm=30, width_cm=20, height_cm=15, declared_value_ars=25000)


async def test_correo_argentino_adapter_translates_shape(carrier_client, monkeypatch):
    monkeypatch.setattr("app.external_mocks.carrier_mocks.random.random", lambda: 0.99)
    adapter = CorreoArgentinoAdapter(carrier_client)
    tracer = TraceRecorder()

    quote = await adapter.get_rate(_package(), "AMBA", tracer)

    assert isinstance(quote, CarrierQuote)
    assert quote.amount_ars > 0
    assert quote.eta_days > 0
    assert any(e.step == "adaptador_secundario" for e in tracer.entries)
    assert any(e.step == "salida" for e in tracer.entries)


async def test_correo_argentino_adapter_raises_when_carrier_fails(carrier_client, monkeypatch):
    monkeypatch.setattr("app.external_mocks.carrier_mocks.random.random", lambda: 0.01)
    adapter = CorreoArgentinoAdapter(carrier_client)

    with pytest.raises(CarrierUnavailableError):
        await adapter.get_rate(_package(), "AMBA", TraceRecorder())


async def test_oca_adapter_translates_shape(carrier_client):
    adapter = OCAAdapter(carrier_client)
    quote = await adapter.get_rate(_package(), "Interior", TraceRecorder())
    assert quote.amount_ars > 0
    assert quote.eta_days > 0


async def test_andreani_adapter_translates_shape(carrier_client):
    adapter = AndreaniAdapter(carrier_client)
    quote = await adapter.get_rate(_package(), "Patagonia", TraceRecorder())
    assert quote.amount_ars > 0
    assert quote.eta_days > 0
