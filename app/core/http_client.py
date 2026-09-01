import httpx
from fastapi import FastAPI


def build_carrier_client(mocks_app: FastAPI) -> httpx.AsyncClient:
    """Cliente HTTP compartido, atado por ASGITransport al sub-app de mocks.

    Nunca abre un socket real: en tests y en produccion el adaptador hace el
    mismo request ASGI de punta a punta, sin ramas condicionales por entorno.
    """
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=mocks_app), base_url="http://mocks")
