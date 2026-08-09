"""Round 5 — correctness only. The structure arrived with the data."""
from given.fixtures import catalog
from src.round5 import prepare, serve


def test_largest_top_level_region():
    prepared = prepare(catalog())
    assert serve(prepared, None) == ("emea", 7000)
