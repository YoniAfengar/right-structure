"""Round 3 — the k busiest stations, live on the wall display."""
from __future__ import annotations

from typing import Any, Sequence, TypeAlias

from given.probe import Station, Trip
from given.round import check_round

Round3Prepared: TypeAlias = Any      # <- YOUR structural decision, in one line. Replace `Any`.


def prepare(trips: Sequence[Trip]) -> Round3Prepared:
    raise NotImplementedError


def serve(prepared: Round3Prepared, k: int) -> list[Station]:
    """The `k` stations with the most metres ridden from them, most-first."""
    raise NotImplementedError


check_round(prepare, serve)
