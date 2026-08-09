"""Round 2 — the support desk has a receipt, and the dashboard has not gone away."""
from __future__ import annotations

from typing import Any, Sequence, TypeAlias

from given.probe import Trip
from given.round import Query2, check_round

Round2Prepared: TypeAlias = Any      # <- YOUR structural decision, in one line. Replace `Any`.


def prepare(trips: Sequence[Trip]) -> Round2Prepared:
    raise NotImplementedError


def serve(prepared: Round2Prepared, query: Query2) -> int | Trip:
    """`ByStation` -> the trip count. `ByReceipt` -> the trip itself."""
    raise NotImplementedError


check_round(prepare, serve)
