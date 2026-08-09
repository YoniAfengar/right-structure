"""Round 1 — correctness, then cost. Read this file: it is how every round is checked."""
from given.fixtures import round1
from given.probe import count_ops
from src.round1 import prepare, serve


def test_trips_per_station():
    trips, queries, expected = round1()

    prepared = prepare(trips)                        # runs once, at boot — not measured
    with count_ops() as ops:                         # runs in the request path — measured
        answers = [serve(prepared, station) for station in queries]

    assert answers == list(expected), "wrong answer — fix that before you think about cost"
    assert ops.comparisons <= 2 * len(queries), (
        f"serve's cost grows with the number of trips ({ops}). A dashboard page load cannot "
        f"afford to look at every trip.")
