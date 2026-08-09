"""The counting domain types and `count_ops()`. Do not edit.

Nothing here inspects your code. Your `serve` is a black box. Instead, Python itself reports what
happened: when a container looks a value up, or when you ask whether one value equals or precedes
another, the work is not done by the operator — the operator *asks the objects*. These types simply
count the asking on the way past.

So a tally is not an estimate and not instrumentation bolted onto your functions. It is the exact
number of questions your algorithm asked the data.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Iterator


@dataclass
class Ops:
    """What your algorithm asked the data, inside one `count_ops()` block."""
    hashes: int = 0          # a value was asked for its hash
    comparisons: int = 0     # two values were checked for equality
    orderings: int = 0       # two values were asked which comes first
    arithmetic: int = 0      # two distances were added or subtracted

    def __str__(self) -> str:
        return (f"hashes={self.hashes} comparisons={self.comparisons} "
                f"orderings={self.orderings} arithmetic={self.arithmetic}")


_active: Ops | None = None


@contextmanager
def count_ops() -> Iterator[Ops]:
    """Tally every question asked of the domain types inside the block.

    Outside a `count_ops()` block the tally is inert, so your own scripts pay nothing for it.
    Blocks nest; the innermost one wins.
    """
    global _active
    ops, previous = Ops(), _active
    _active = ops
    try:
        yield ops
    finally:
        _active = previous


class _Counted:
    """A value object that reports what was asked of it. The base of every type below."""
    __slots__ = ("_value",)

    def __init__(self, value: Any) -> None:
        self._value = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._value!r})"

    def __hash__(self) -> int:
        if _active is not None:
            _active.hashes += 1
        return hash(self._value)

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        if _active is not None:
            _active.comparisons += 1
        return bool(self._value == other._value)

    def __lt__(self, other: Any) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        if _active is not None:
            _active.orderings += 1
        return bool(self._value < other._value)

    def __le__(self, other: Any) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        if _active is not None:
            _active.orderings += 1
        return bool(self._value <= other._value)


# `__eq__`, `__lt__` and `__le__` are the whole comparison surface on purpose. `a > b` with no
# `__gt__` falls back to `b.__lt__(a)`; `a >= b` falls back to `b.__le__(a)`; `a != b` falls back to
# `__eq__`. Every container in the standard library, and every comparison you can write, is built out
# of those three questions — so all of them route through the counters above, whichever you reach for.
# There is nowhere to slip past.

class Station(_Counted):
    """Where a trip started. Hashable, orderable."""
    __slots__ = ()


class TripId(_Counted):
    """The id printed on a customer's receipt."""
    __slots__ = ()


class Timestamp(_Counted):
    """When a trip started, as whole seconds since an arbitrary epoch."""
    __slots__ = ()


class Distance(_Counted):
    """Metres ridden. Adds and subtracts — and says so."""
    __slots__ = ()

    def __add__(self, other: Any) -> "Distance":
        if isinstance(other, Distance):
            addend = other._value
        elif isinstance(other, int):        # so `sum()` can start from 0
            addend = other
        else:
            return NotImplemented
        if _active is not None:
            _active.arithmetic += 1
        return Distance(self._value + addend)

    __radd__ = __add__

    def __sub__(self, other: "Distance") -> "Distance":
        if type(other) is not Distance:
            return NotImplemented
        if _active is not None:
            _active.arithmetic += 1
        return Distance(self._value - other._value)


class Trip:
    """One ride. Plain data — the counting lives in its fields."""
    __slots__ = ("trip_id", "station", "started_at", "distance_m")

    def __init__(self, trip_id: TripId, station: Station,
                 started_at: Timestamp, distance_m: Distance) -> None:
        self.trip_id = trip_id
        self.station = station
        self.started_at = started_at
        self.distance_m = distance_m

    def __repr__(self) -> str:
        return f"Trip({self.trip_id!r}, {self.station!r}, {self.started_at!r}, {self.distance_m!r})"
