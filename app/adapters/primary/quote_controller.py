from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.domain.package import PackageTooHeavyError
from app.domain.trace import TraceRecorder
from app.domain.zones import MAX_POSTAL_CODE, MIN_POSTAL_CODE, InvalidPostalCodeError
from app.ports.quote_history_port import QuoteHistoryPort
from app.ports.shipping_quote_port import QuoteRequest, ShippingQuotePort

router = APIRouter(prefix="/api")

# Techos de sanidad del input HTTP: mas permisivos que las reglas de negocio
# del dominio (ver PackageTooHeavyError) a proposito, para que sea el dominio
# -no un 422 generico de Pydantic- el que explique por que se rechazo.
MAX_INPUT_WEIGHT_KG = 100.0
MAX_INPUT_DIMENSION_CM = 200.0


class QuotePayload(BaseModel):
    weight_kg: float = Field(gt=0, le=MAX_INPUT_WEIGHT_KG)
    length_cm: float = Field(gt=0, le=MAX_INPUT_DIMENSION_CM)
    width_cm: float = Field(gt=0, le=MAX_INPUT_DIMENSION_CM)
    height_cm: float = Field(gt=0, le=MAX_INPUT_DIMENSION_CM)
    declared_value_ars: float = Field(ge=0)
    postal_code: int = Field(ge=MIN_POSTAL_CODE, le=MAX_POSTAL_CODE)


def get_use_case(request: Request) -> ShippingQuotePort:
    return request.app.state.quote_use_case


def get_history(request: Request) -> QuoteHistoryPort:
    return request.app.state.history


@router.post("/quote")
async def post_quote(payload: QuotePayload, use_case: ShippingQuotePort = Depends(get_use_case)):
    tracer = TraceRecorder()
    tracer.mark("entrada", "HTTP", f"POST /api/quote peso={payload.weight_kg}kg CP={payload.postal_code}")
    tracer.mark("adaptador_primario", "quote_controller", "traduciendo JSON -> QuoteRequest")

    quote_request = QuoteRequest(
        weight_kg=payload.weight_kg,
        length_cm=payload.length_cm,
        width_cm=payload.width_cm,
        height_cm=payload.height_cm,
        declared_value_ars=payload.declared_value_ars,
        postal_code=payload.postal_code,
    )

    tracer.mark("puerto_primario", "ShippingQuotePort", "invocando caso de uso")
    try:
        return await use_case.execute(quote_request, tracer)
    except PackageTooHeavyError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except InvalidPostalCodeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/history")
async def get_history_route(history: QuoteHistoryPort = Depends(get_history)):
    records = await history.list_recent()
    return [
        {
            "id": r.id,
            "created_at": r.created_at.isoformat(),
            "postal_code": r.postal_code,
            "zone": r.zone,
            "effective_weight_kg": r.effective_weight_kg,
            "best_carrier": r.best_carrier,
            "best_amount_ars": r.best_amount_ars,
        }
        for r in records
    ]
