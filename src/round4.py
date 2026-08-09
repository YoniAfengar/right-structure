"""Round 4 — total distance of trips that started between 09:00 and 11:00."""
from __future__ import annotations

from typing import Any, Sequence, TypeAlias

from given.probe import Distance, Timestamp, Trip
from given.round import check_round

Round4Prepared: TypeAlias = Any      # <- YOUR structural decision, in one line. Replace `Any`.


def prepare(trips: Sequence[Trip]) -> Round4Prepared:
    raise NotImplementedError


def serve(prepared: Round4Prepared, span: tuple[Timestamp, Timestamp]) -> Distance:
    """Total metres ridden on trips that started in the half-open range [lo, hi)."""
    raise NotImplementedError


check_round(prepare, serve)
