"""Round 4 — total distance of trips that started between 09:00 and 11:00."""
from __future__ import annotations

from sys import prefix
from typing import Sequence, TypeAlias

from given.probe import Distance, Timestamp, Trip
from given.round import check_round

Round4Prepared: TypeAlias = tuple[
    list[Timestamp],
    list[Distance],
]


def _started_at(trip: Trip) -> Timestamp:
    return trip.started_at


def _find_lo_index(timestamps: list[Timestamp], lo: Timestamp) -> int:
    left = 0
    right = len(timestamps)

    while left < right:
        middle = (left + right) // 2
        if timestamps[middle] < lo:
            left = middle + 1
        else:
            right = middle

    return left

def _find_hi_index(timestamps: list[Timestamp], hi: Timestamp) -> int:
    left = 0
    right = len(timestamps)

    while left < right:
        middle = (left + right) // 2

        if timestamps[middle] < hi:
            left = middle + 1
        else:
            right = middle

    return left

def prepare(trips: Sequence[Trip]) -> Round4Prepared:
    ordered = sorted(trips, key=_started_at)
    timestamps: list[Timestamp] = []
    prefix: list[Distance] = [Distance(0)]

    for trip in ordered:
        timestamps.append(trip.started_at)
        prefix.append(prefix[-1] + trip.distance_m)

    return (timestamps, prefix)

def serve(prepared: Round4Prepared, span: tuple[Timestamp, Timestamp]) -> Distance:
    """Total metres ridden on trips that started in the half-open range [lo, hi)."""

    (lo, hi) = span
    (timestamps, prefix) = prepared

    lo_index = _find_lo_index(timestamps, lo)
    hi_index = _find_hi_index(timestamps, hi)

    return prefix[hi_index] - prefix[lo_index]


check_round(prepare, serve)
