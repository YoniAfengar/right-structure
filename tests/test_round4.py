"""Round 4 — two gates: finding the range, and totalling it."""
from math import log2

from given.fixtures import round4
from given.probe import count_ops
from src.round4 import prepare, serve


def test_total_distance_in_a_time_range():
    trips, queries, expected = round4()

    prepared = prepare(trips)
    with count_ops() as ops:
        answers = [serve(prepared, span) for span in queries]

    assert answers == list(expected), "wrong total — mind the half-open boundary: lo is in, hi is out"
    assert ops.orderings <= 4 * log2(len(trips)) * len(queries), (
        f"finding the range costs more than O(log n) per query ({ops})")
    assert ops.arithmetic <= 2 * len(queries), (
        f"the total is being added up one trip at a time ({ops}). A query matching 40,000 trips "
        f"must cost what a query matching 200 costs.")
