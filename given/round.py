"""The shape of every round. Do not edit.

`prepare` runs once, at boot, while nobody is waiting. `serve` runs in the request path, millions of
times. Between them sits the structure `prepare` builds and `serve` reads — and choosing it is the
exercise.

We cannot name that structure's type here, because it changes every round. But `prepare` returns it and
`serve` takes it, and it has to be *the same one* on both sides. A type variable says exactly that, and
`check_round` is the one place the two ends are made to line up.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TypeVar

from .probe import Station, TripId

Source = TypeVar("Source")
PreparedDataStructure = TypeVar("PreparedDataStructure")
Query = TypeVar("Query")
Answer = TypeVar("Answer")


def check_round(
    prepare: Callable[[Source], PreparedDataStructure],
    serve: Callable[[PreparedDataStructure, Query], Answer],
) -> None:
    """Line the two functions up at type-check time. It does nothing at runtime.

    `prepare` turns the source into *some* structure; `serve` reads *that same* structure.
    `PreparedDataStructure` is the single type variable that stands in for both `prepare`'s return and
    `serve`'s first argument, so if your two annotations disagree there is no consistent type to give
    it and mypy says so. Nothing here knows or cares what you chose — only that both ends chose the
    same thing.
    """


# Round 2 asks two different questions of one prepared structure. A query is one of these.
@dataclass(frozen=True)
class ByStation:
    """The dashboard: how many trips started here?"""
    station: Station


@dataclass(frozen=True)
class ByReceipt:
    """The support desk, reading a customer's receipt aloud: which trip is this?"""
    station: Station
    trip_id: TripId


Query2 = ByStation | ByReceipt
