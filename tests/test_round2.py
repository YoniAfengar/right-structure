"""Round 2 — one prepared structure, two questions, both O(1)."""
from given.fixtures import round2
from given.probe import Trip, count_ops
from src.round2 import prepare, serve


def test_receipt_lookup_and_dashboard_together():
    trips, queries, expected = round2()

    prepared = prepare(trips)
    with count_ops() as ops:
        answers = [serve(prepared, q) for q in queries]

    for got, want in zip(answers, expected, strict=True):
        if isinstance(want, Trip):
            assert got is want, "the support desk got the wrong trip"
        else:
            assert got == want, "the dashboard's counts changed"

    assert ops.comparisons <= 2 * len(queries), (
        f"one of the two questions is being answered by searching ({ops}). Both must cost the "
        f"same as they would if the other did not exist.")
