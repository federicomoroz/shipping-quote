# shipping-quote

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/federicomoroz/shipping-quote)

Cotizador de envíos que existe para mostrar un circuito de arquitectura hexagonal
funcionando de verdad, no como diagrama: cada request real que procesa queda
trazado hop por hop, desde que entra por HTTP hasta que tres transportistas
distintos devuelven su propia cotización.

**Demo en vivo:** [shipping-quote.onrender.com](https://shipping-quote.onrender.com/) _(free tier: se duerme tras 15 min sin tráfico, el primer request tarda ~30-50s)_

```
entrada -> adaptador -> puerto -> caso de uso -> dominio -> puerto -> adaptador -> salida
 (POST)   quote_       Shipping   QuoteShipping  pipeline   Carrier   *Adapter   API del
          controller   QuotePort  UseCase        steps      Port                carrier
```

## Por qué existe

Es un caso de uso — cotizar un paquete — corriendo contra 3 adaptadores de
transportista (Correo Argentino, OCA, Andreani) en el mismo request. El mismo
dominio produce tres resultados reales distintos según qué adaptador atiende
la llamada, sin que el caso de uso sepa que existen tres transportistas.

## Correr localmente

```bash
python -m venv .venv
.venv/Scripts/activate           # o source .venv/bin/activate en Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --port 8005 --reload
```

Abrir `http://localhost:8005`. Un solo comando, sin Docker ni servicios
externos: SQLite es el único estado (por default `sqlite:///shipping_quote.db`,
sobreescribible con la env var `DATABASE_URL`), y los "transportistas externos"
son un sub-app de FastAPI aparte, conectado únicamente por `ASGITransport`
(nunca abre un socket real), así el mismo código de los adaptadores corre
igual en tests y en producción.

El servidor crea la tabla con `create_all()` si no existe, para que correr
`uvicorn` alcance sin pasos manuales. Para evolucionar el schema de verdad
existen migraciones aparte (ver abajo).

## Tests

```bash
pytest -q
```

[![tests](https://github.com/federicomoroz/shipping-quote/actions/workflows/tests.yml/badge.svg)](https://github.com/federicomoroz/shipping-quote/actions/workflows/tests.yml)

31 tests: reglas de dominio puras, pasos del pipeline, el caso de uso con
adaptadores falsos (incluyendo uno que falla a propósito), cada adaptador
real contra su mock, y la integración completa `POST /api/quote`. Corren en
CI (GitHub Actions) en cada push.

## Migraciones

```bash
alembic upgrade head        # aplicar
alembic revision --autogenerate -m "descripcion"   # generar una nueva
```

`migrations/env.py` toma la URL de `app.core.database.DATABASE_URL` (no está
duplicada en `alembic.ini`), así que respeta la misma env var que usa la app.
Es una herramienta aparte del `create_all()` del arranque a propósito: los
tests parchean el engine, no la URL, y engancharlo al lifespan hubiera hecho
que los tests migraran la base real en vez de la de memoria.

## Arquitectura

```
app/
├── domain/            # Package, zonas, FeePolicy, Tracer — sin dependencias externas
├── ports/              # ShippingQuotePort (primario), CarrierPort y QuoteHistoryPort (secundarios)
├── use_cases/          # QuoteShippingUseCase + el pipeline de pasos de dominio
├── adapters/
│   ├── primary/         # quote_controller.py (HTTP -> QuoteRequest) + spa.py (la UI)
│   └── secondary/       # 3 adaptadores de carrier + sqlite/ (QuoteHistoryPort + su modelo ORM)
├── external_mocks/     # simulación de las 3 APIs reales, cada una con su propio JSON
└── main.py             # composition root: arma todo en el lifespan
```

### Decisiones puntuales

- **`ShippingQuotePort` explícito para una sola implementación.** Normalmente
  sería over-engineering (YAGNI); acá el propósito del proyecto es mostrar el
  circuito completo, así que se deja a propósito — ver el docstring del ABC.
- **Traza por request vía `Tracer`/`TraceRecorder`** (`app/domain/trace.py`),
  no un `EventManager` compartido: una traza es de un solo consumidor y
  estrictamente ordenada, así que se pasa por referencia a través de las capas
  en vez de forzar un bus pub/sub donde no hace falta.
- **Dos puertos secundarios** (`CarrierPort` y `QuoteHistoryPort`) para
  reforzar la lección con un segundo ejemplo y darle al proyecto persistencia
  real (historial de cotizaciones).
- **Correo Argentino falla ~15% de las veces** (simulado). El caso de uso
  corre los 3 adaptadores con `asyncio.gather` y devuelve 2 de 3 cotizaciones
  sin explotar cuando uno falla — la prueba de manejo de errores real, no solo
  "llamo a 3 y listo".
- **Peso volumétrico.** El peso efectivo es `max(peso real, largo×ancho×alto / 5000)`,
  la fórmula estándar de la industria — el dominio no es un `if` aislado.
- **`HttpCarrierAdapter` genérico** (`adapters/secondary/http_carrier_adapter.py`).
  Los 3 transportistas no son 3 clases con el mismo try/except/timeout
  repetido: son la misma clase configurada por composición (endpoint +
  2 funciones de mapeo). Agregar un cuarto transportista es un archivo de
  ~15 líneas, no una clase entera.
- **`Decimal`, no `float`, para plata.** `apply_service_fee()` opera en
  `Decimal` y redondea con `ROUND_HALF_UP` explícito — el `round()` nativo de
  Python usa banker's rounding, que para dinero da resultados que sorprenden
  (ver `test_apply_service_fee_rounds_half_up_not_banker`).

### Fuera de alcance (a propósito)

Sin autenticación, sin rate limiting, sin selección manual de transportista
(siempre se cotizan los 3): el objetivo es la arquitectura, no un producto
completo.

## API

| Método | Ruta          | Descripción                                    |
|--------|---------------|-------------------------------------------------|
| POST   | `/api/quote`  | Cotiza un paquete contra los 3 transportistas   |
| GET    | `/api/history`| Últimas 20 cotizaciones guardadas                |

## Stack

FastAPI · SQLAlchemy (SQLite) · Alembic · httpx · Pydantic · pytest + pytest-asyncio
