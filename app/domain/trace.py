"""Traza del circuito hexagonal: una entrada por cada hop real que atraviesa un request.

`Tracer` es la abstraccion (nivel dominio, sin dependencias) que ports y adapters
usan para dejar constancia de su propio hop sin acoplarse a como se acumula la
traza. `TraceRecorder` es la unica implementacion: un acumulador mutable con
timestamps relativos al inicio del request.
"""

import time
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class TraceEntry:
    step: str
    label: str
    detail: str
    elapsed_ms: float


class Tracer(Protocol):
    entries: list[TraceEntry]

    def mark(self, step: str, label: str, detail: str) -> None: ...


@dataclass
class TraceRecorder:
    entries: list[TraceEntry] = field(default_factory=list)
    _started_at: float = field(default_factory=time.perf_counter)

    def mark(self, step: str, label: str, detail: str) -> None:
        elapsed_ms = (time.perf_counter() - self._started_at) * 1000
        self.entries.append(TraceEntry(step=step, label=label, detail=detail, elapsed_ms=round(elapsed_ms, 2)))
