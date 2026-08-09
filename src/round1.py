"""Round 1 — how many trips started at each station?"""
from __future__ import annotations

from typing import Any, Sequence, TypeAlias

from given.probe import Station, Trip
from given.round import check_round

Round1Prepared: TypeAlias = Any      # <- YOUR structural decision, in one line. Replace `Any`.


def prepare(trips: Sequence[Trip]) -> Round1Prepared:
    raise NotImplementedError


def serve(prepared: Round1Prepared, station: Station) -> int:
    raise NotImplementedError


check_round(prepare, serve)   # keep this line; mypy fails here if the two ends disagree
