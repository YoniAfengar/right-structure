"""Round 3 — the k busiest stations, live on the wall display."""
from __future__ import annotations

from typing import Any, Sequence, TypeAlias

from given.probe import Distance, Station, Trip
from given.round import check_round

Round3Prepared: TypeAlias = dict[Station, Distance]

def _sift_up(heap: list[tuple[Distance, Station]], i: int) -> None:
    while i > 0 and heap[i][0] < heap[(i - 1) // 2][0]:
        parent = (i - 1) // 2
        heap[i], heap[parent] = heap[parent], heap[i]
        i = parent


def _sift_down(heap: list[tuple[Distance, Station]], i: int) -> None:
    while True:
        smallest = i
        left = 2 * i + 1
        right = 2 * i + 2

        if left < len(heap) and heap[left][0] < heap[smallest][0]:
            smallest = left

        if right < len(heap) and heap[right][0] < heap[smallest][0]:
            smallest = right

        if smallest == i:
            return

        heap[i], heap[smallest] = heap[smallest], heap[i]
        i = smallest


def _pop_weakest(heap: list[tuple[Distance, Station]]) -> tuple[Distance, Station]:
    heap[0], heap[-1] = heap[-1], heap[0]
    weakest = heap.pop()

    if heap:
        _sift_down(heap, 0)

    return weakest


def prepare(trips: Sequence[Trip]) -> Round3Prepared:
    totals: Round3Prepared = {}
    for trip in trips:
        totals[trip.station] = totals.get(trip.station, 0) + trip.distance_m
    return totals  

def serve(prepared: Round3Prepared, k: int) -> list[Station]:
    heap: list[tuple[Distance, Station]] = []

    for station, total in prepared.items():
        if len(heap) < k:
            heap.append((total, station))
            _sift_up(heap, len(heap) - 1)

        elif heap[0][0] < total:
            heap[0] = (total, station)
            _sift_down(heap, 0)

    weakest_first = [_pop_weakest(heap)[1] for _ in range(len(heap))]

    return weakest_first[::-1]


check_round(prepare, serve)





