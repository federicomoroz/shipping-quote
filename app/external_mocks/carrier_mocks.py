"""Simulacion de 3 APIs externas reales, cada una con su propio contrato.

Esta es la "salida" del circuito: un sistema ajeno, con su propio vocabulario
de campos (espaniol/ingles mezclado, distintas unidades de nombre). El trabajo
del adaptador (en `app/adapters/secondary/`) es traducir esto al puerto comun.

Este modulo no importa nada del dominio: un sistema externo real no conoce
nuestros tipos, asi que las zonas viajan como el `str` crudo que llega por HTTP.
La formula de precio esta parametrizada en `CarrierSimulationProfile` para que
sea *dato*, no codigo repetido tres veces: agregar un cuarto transportista es
un perfil nuevo, no un endpoint copy-pasteado.

Se monta via ASGITransport (nunca abre un socket real), asi el mismo codigo
corre igual en produccion y en tests.
"""

import asyncio
import random
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

mocks_app = FastAPI(title="Carrier Mocks (simulacion de APIs externas)")


@dataclass(frozen=True)
class CarrierSimulationProfile:
    base_price_ars: float
    price_per_kg_ars: float
    zone_extra_ars: dict[str, float]
    eta_days_by_zone: dict[str, int]
    latency_range_s: tuple[float, float]
    price_jitter_range: tuple[float, float]
    failure_probability: float = 0.0


CORREO_ARGENTINO_PROFILE = CarrierSimulationProfile(
    base_price_ars=1400,
    price_per_kg_ars=165,
    zone_extra_ars={"AMBA": 0, "Interior": 600, "Patagonia": 1800},
    eta_days_by_zone={"AMBA": 5, "Interior": 8, "Patagonia": 12},
    latency_range_s=(0.4, 0.9),
    price_jitter_range=(0.92, 1.08),
    failure_probability=0.15,
)

OCA_PROFILE = CarrierSimulationProfile(
    base_price_ars=1700,
    price_per_kg_ars=190,
    zone_extra_ars={"AMBA": 0, "Interior": 600, "Patagonia": 1800},
    eta_days_by_zone={"AMBA": 3, "Interior": 6, "Patagonia": 9},
    latency_range_s=(0.12, 0.28),
    price_jitter_range=(0.92, 1.08),
)

ANDREANI_PROFILE = CarrierSimulationProfile(
    base_price_ars=1900,
    price_per_kg_ars=175,
    zone_extra_ars={"AMBA": 0, "Interior": 600, "Patagonia": 1800},
    eta_days_by_zone={"AMBA": 2, "Interior": 5, "Patagonia": 8},
    latency_range_s=(0.08, 0.18),
    price_jitter_range=(0.92, 1.08),
)


async def _simulate_quote(profile: CarrierSimulationProfile, weight_kg: float, zone: str) -> tuple[float, int]:
    await asyncio.sleep(random.uniform(*profile.latency_range_s))
    if profile.failure_probability and random.random() < profile.failure_probability:
        raise HTTPException(status_code=503, detail="servicio no disponible")

    jitter = random.uniform(*profile.price_jitter_range)
    price = (profile.base_price_ars + profile.price_per_kg_ars * weight_kg + profile.zone_extra_ars[zone]) * jitter
    return round(price, 2), profile.eta_days_by_zone[zone]


class CorreoArgentinoRequest(BaseModel):
    peso_kg: float
    zona: str


@mocks_app.post("/correo-argentino/cotizar")
async def correo_argentino_cotizar(payload: CorreoArgentinoRequest):
    monto, dias_habiles = await _simulate_quote(CORREO_ARGENTINO_PROFILE, payload.peso_kg, payload.zona)
    return {"monto": monto, "dias_habiles": dias_habiles}


class OcaRequest(BaseModel):
    weight: float
    region: str


@mocks_app.post("/oca/quote")
async def oca_quote(payload: OcaRequest):
    price, estimated_delivery = await _simulate_quote(OCA_PROFILE, payload.weight, payload.region)
    return {"price": price, "estimated_delivery": estimated_delivery}


class AndreaniRequest(BaseModel):
    kg: float
    zona_andreani: str


@mocks_app.post("/andreani/tarifar")
async def andreani_tarifar(payload: AndreaniRequest):
    tarifa_pesos, eta_dias = await _simulate_quote(ANDREANI_PROFILE, payload.kg, payload.zona_andreani)
    return {"tarifa_pesos": tarifa_pesos, "eta_dias": eta_dias}
