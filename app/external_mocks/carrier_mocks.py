"""Simulacion de 3 APIs externas reales, cada una con su propio contrato.

Esta es la "salida" del circuito: un sistema ajeno, con su propio vocabulario
de campos (espaniol/ingles mezclado, distintas unidades de nombre) y su propia
formula de precio. El trabajo del adaptador es traducir esto al puerto comun.

Se monta via ASGITransport (nunca abre un socket real), asi el mismo codigo
corre igual en produccion y en tests.
"""

import asyncio
import random

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

mocks_app = FastAPI(title="Carrier Mocks (simulacion de APIs externas)")

ZONE_EXTRA = {"AMBA": 0, "Interior": 600, "Patagonia": 1800}


class CorreoArgentinoRequest(BaseModel):
    peso_kg: float
    zona: str


@mocks_app.post("/correo-argentino/cotizar")
async def correo_argentino_cotizar(payload: CorreoArgentinoRequest):
    await asyncio.sleep(random.uniform(0.4, 0.9))
    if random.random() < 0.15:
        raise HTTPException(status_code=503, detail="servicio no disponible")
    extra = ZONE_EXTRA.get(payload.zona, 600)
    monto = (1400 + 165 * payload.peso_kg + extra) * random.uniform(0.92, 1.08)
    dias_habiles = {"AMBA": 5, "Interior": 8, "Patagonia": 12}.get(payload.zona, 8)
    return {"monto": round(monto, 2), "dias_habiles": dias_habiles}


class OcaRequest(BaseModel):
    weight: float
    region: str


@mocks_app.post("/oca/quote")
async def oca_quote(payload: OcaRequest):
    await asyncio.sleep(random.uniform(0.12, 0.28))
    extra = ZONE_EXTRA.get(payload.region, 600)
    price = (1700 + 190 * payload.weight + extra) * random.uniform(0.92, 1.08)
    estimated_delivery = {"AMBA": 3, "Interior": 6, "Patagonia": 9}.get(payload.region, 6)
    return {"price": round(price, 2), "estimated_delivery": estimated_delivery}


class AndreaniRequest(BaseModel):
    kg: float
    zona_andreani: str


@mocks_app.post("/andreani/tarifar")
async def andreani_tarifar(payload: AndreaniRequest):
    await asyncio.sleep(random.uniform(0.08, 0.18))
    extra = ZONE_EXTRA.get(payload.zona_andreani, 600)
    tarifa_pesos = (1900 + 175 * payload.kg + extra) * random.uniform(0.92, 1.08)
    eta_dias = {"AMBA": 2, "Interior": 5, "Patagonia": 8}.get(payload.zona_andreani, 5)
    return {"tarifa_pesos": round(tarifa_pesos, 2), "eta_dias": eta_dias}
