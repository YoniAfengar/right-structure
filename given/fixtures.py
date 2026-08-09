"""Seeded generators for trips, query workloads, and the catalog. Do not edit.

Everything is deterministic: the same seed gives the same trips on your laptop and in CI, so a cost
gate means the same thing everywhere. Expected answers are computed here from plain integers, by the
same loop that generates the data — a slow, obviously-correct baseline.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from functools import lru_cache

from .catalog import Node, file, region
from .probe import Distance, Station, Timestamp, Trip, TripId
from .round import ByReceipt, ByStation, Query2

SEED = 20260714
BASE_EPOCH = 1_741_000_000       # some Friday morning
DAY = 86_400


@dataclass(frozen=True)
class Fixture:
    trips: tuple[Trip, ...]
    names: tuple[str, ...]             # every station name, in name order
    ids: tuple[str, ...]               # trip id strings, aligned with `trips`
    at: tuple[int, ...]                # index into `names` of each trip's station
    counts: tuple[int, ...]            # trips per station, indexed like `names`
    metres: tuple[int, ...]            # metres ridden per station, indexed like `names`
    starts: tuple[int, ...]            # raw start seconds, aligned with `trips`
    distances: tuple[int, ...]         # raw metres, aligned with `trips`


@lru_cache(maxsize=None)
def make_trips(n_trips: int, n_stations: int) -> Fixture:
    """Station popularity is skewed — a few stations see most of the traffic, as in any real city —
    and the popularity order is shuffled away from the name order, so nothing gets to be accidentally
    right because the input happened to arrive sorted."""
    rng = random.Random(SEED + n_trips + n_stations)
    names = tuple(f"ST-{i:04d}" for i in range(n_stations))
    popularity = list(range(n_stations))
    rng.shuffle(popularity)

    counts, metres, rows = [0] * n_stations, [0] * n_stations, []
    for i in range(n_trips):
        idx = popularity[int(n_stations * rng.random() ** 2)]
        start, dist = BASE_EPOCH + rng.randrange(DAY), rng.randrange(200, 12_000)
        counts[idx] += 1
        metres[idx] += dist
        rows.append((f"T-{i:07d}", idx, start, dist))
    rng.shuffle(rows)

    return Fixture(
        trips=tuple(Trip(TripId(tid), Station(names[idx]), Timestamp(s), Distance(d))
                    for tid, idx, s, d in rows),
        names=names, ids=tuple(r[0] for r in rows), at=tuple(r[1] for r in rows),
        counts=tuple(counts), metres=tuple(metres),
        starts=tuple(r[2] for r in rows), distances=tuple(r[3] for r in rows))


# ── Round 1 — trips per station ──────────────────────────────────────────────────
@lru_cache(maxsize=None)
def round1() -> tuple[tuple[Trip, ...], tuple[Station, ...], tuple[int, ...]]:
    """(trips, queries, expected) — 200,000 trips over 200 stations, one query per page load."""
    f = make_trips(200_000, 200)
    rng = random.Random(SEED)
    picks = [rng.randrange(200) for _ in range(100)]
    # Fresh Station objects, equal to but not identical with the ones inside the trips. A lookup
    # then really has to ask `__eq__`, and no identity shortcut can hide the cost.
    return f.trips, tuple(Station(f.names[i]) for i in picks), tuple(f.counts[i] for i in picks)


# ── Round 2 — a trip by its id, and the dashboard, together ──────────────────────
@lru_cache(maxsize=None)
def round2() -> tuple[tuple[Trip, ...], tuple[Query2, ...], tuple[int | Trip, ...]]:
    """(trips, queries, expected) — 200,000 trips over just 20 stations."""
    f = make_trips(200_000, 20)
    rng = random.Random(SEED + 2)
    queries: list[Query2] = []
    expected: list[int | Trip] = []
    for _ in range(100):
        s = rng.randrange(20)
        queries.append(ByStation(Station(f.names[s])))
        expected.append(f.counts[s])
        t = rng.randrange(len(f.trips))
        queries.append(ByReceipt(Station(f.names[f.at[t]]), TripId(f.ids[t])))
        expected.append(f.trips[t])
    return f.trips, tuple(queries), tuple(expected)


# ── Round 3 — the k busiest stations, by metres ridden ───────────────────────────
MAX_K = 50


@lru_cache(maxsize=None)
def round3() -> tuple[tuple[Trip, ...], int, tuple[Station, ...]]:
    """(trips, n_stations, ranking) — 100,000 trips over 5,000 stations.

    Quiet stations tie on total metres all the time, and it does not matter: nothing asks about them.
    What must hold is that the ranking is unambiguous *where it is read* — down to `MAX_K`, and one
    place past it, so that the station in `k`th place strictly beats the station in `k+1`th.
    """
    n_stations = 5_000
    f = make_trips(100_000, n_stations)
    order = sorted(range(n_stations), key=lambda i: -f.metres[i])
    cut = [f.metres[i] for i in order[:MAX_K + 1]]
    assert len(set(cut)) == len(cut), "fixture broken: a tie inside the top k makes the answer ambiguous"
    return f.trips, n_stations, tuple(Station(f.names[i]) for i in order)


# ── Round 4 — total distance in a half-open time range ───────────────────────────
Span = tuple[Timestamp, Timestamp]


@lru_cache(maxsize=None)
def round4() -> tuple[tuple[Trip, ...], tuple[Span, ...], tuple[Distance, ...]]:
    """(trips, queries, expected) — 200,000 trips; ranges matching a few hundred trips up to tens of
    thousands. Expected totals come from a plain scan over the raw integers."""
    f = make_trips(200_000, 200)
    rng = random.Random(SEED + 4)
    queries: list[Span] = []
    expected: list[Distance] = []
    for i in range(200):
        width = (60, 900, 7_200, 28_800)[i % 4]
        lo = BASE_EPOCH + rng.randrange(DAY - width)
        hi = lo + width
        queries.append((Timestamp(lo), Timestamp(hi)))
        matched = (d for s, d in zip(f.starts, f.distances, strict=True) if lo <= s < hi)
        expected.append(Distance(sum(matched)))
    return f.trips, tuple(queries), tuple(expected)


# ── Round 5 — the drop catalog ───────────────────────────────────────────────────
def catalog() -> Node:
    """Six levels deep and irregular. Contains an empty region, a region holding no file at any
    depth, and a file whose name looks like a region's."""
    return region(
        "drops",
        region("emea",
               region("uk",
                      region("london",
                             region("2026",
                                    region("03", file("d-01.jsonl", 900), file("d-02.jsonl", 1_100)),
                                    region("04", file("d-03.jsonl", 2_000)))),
                      region("scotland")),                            # a region with nothing in it
               region("de", region("berlin", file("apac", 3_000)))),  # a file named like a region
        region("apac",
               region("jp", region("tokyo", region("2026", region("03", file("d-04.jsonl", 4_500))))),
               region("au", region("sydney", region("2026", region("03"))))),  # no file at any depth
        region("amer",
               region("us",
                      region("nyc", region("2026", region("03", file("d-05.jsonl", 2_500)))),
                      region("sfo", region("2026", region("03", file("d-06.jsonl", 1_000)))))),
        region("antarctica"),                                        # empty top-level region
    )
