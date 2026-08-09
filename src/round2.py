"""Round 2 — the support desk has a receipt, and the dashboard has not gone away."""
from __future__ import annotations

from typing import Sequence, TypeAlias

from given.probe import Station, Trip, TripId
from given.round import ByStation, Query2, check_round

Round2Prepared: TypeAlias = tuple[
    dict[Station, int],
    dict[tuple[Station, TripId], Trip],
]

def prepare(trips: Sequence[Trip]) -> Round2Prepared:
    counts: dict[Station, int] = {}
    trips_by_receipt: dict[tuple[Station, TripId], Trip] = {}

    for trip in trips:
        counts[trip.station] = counts.get(trip.station, 0) + 1
        trips_by_receipt[(trip.station, trip.trip_id)] = trip

    return counts, trips_by_receipt

def serve(prepared: Round2Prepared, query: Query2) -> int | Trip:
    if isinstance(query, ByStation):
        return prepared[0].get(query.station, 0)
    else:
        return prepared[1][(query.station, query.trip_id)]


check_round(prepare, serve)
