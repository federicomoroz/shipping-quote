from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.adapters.primary.quote_controller import router as quote_router
from app.adapters.secondary.andreani_adapter import AndreaniAdapter
from app.adapters.secondary.correo_argentino_adapter import CorreoArgentinoAdapter
from app.adapters.secondary.oca_adapter import OCAAdapter
from app.adapters.secondary.sqlite_quote_history import SQLiteQuoteHistory
import app.core.database as database
from app.core.http_client import build_carrier_client
from app.external_mocks.carrier_mocks import mocks_app
from app.use_cases.quote_shipping import QuoteShippingUseCase
from app.views.templates.spa import render_spa


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Se resuelve `database.engine` en el modulo (no por nombre importado) porque
    # los tests lo parchean antes de que arranque el lifespan.
    database.Base.metadata.create_all(bind=database.engine)

    http_client = build_carrier_client(mocks_app)
    carriers = [
        CorreoArgentinoAdapter(http_client),
        OCAAdapter(http_client),
        AndreaniAdapter(http_client),
    ]
    history = SQLiteQuoteHistory()

    app.state.history = history
    app.state.quote_use_case = QuoteShippingUseCase(carriers=carriers, history=history)

    yield

    await http_client.aclose()


app = FastAPI(title="shipping-gondola", lifespan=lifespan)
app.include_router(quote_router)


@app.get("/")
async def root() -> HTMLResponse:
    return HTMLResponse(render_spa())
