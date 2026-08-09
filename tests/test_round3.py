"""Round 3 — the only round that measures `prepare` as well as `serve`."""
import pytest

from given.fixtures import round3
from given.probe import count_ops
from src.round3 import prepare, serve


@pytest.mark.parametrize("k", [1, 10, 50])
def test_k_busiest_stations(k):
    trips, n_stations, ranking = round3()

    with count_ops() as ops:            # prepare AND serve — the gate is on the sum
        prepared = prepare(trips)
        answer = serve(prepared, k)

    assert answer == list(ranking[:k]), "wrong stations, or the wrong order"
    assert ops.orderings <= 3 * n_stations, (
        f"putting {n_stations} stations in order to look at {k} of them costs O(n log n) "
        f"({ops}). The display asked for {k}.")
