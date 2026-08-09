"""Round 1 — how many trips started at each station?"""
from __future__ import annotations

from typing import Sequence, TypeAlias

from given.probe import Station, Trip
from given.round import check_round

Round1Prepared: TypeAlias = dict[Station, int]


def prepare(trips: Sequence[Trip]) -> Round1Prepared:
    counts: Round1Prepared = {}
    for trip in trips:
        counts[trip.station] = counts.get(trip.station, 0) + 1
    return counts


def serve(prepared: Round1Prepared, station: Station) -> int:
    return prepared.get(station, 0)


check_round(prepare, serve)   # keep this line; mypy fails here if the two ends disagree
