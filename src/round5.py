"""Round 5 — which region is costing us the most storage?"""
from __future__ import annotations

from typing import Any, TypeAlias

from given.catalog import Node
from given.round import check_round

Round5Prepared: TypeAlias = Any      # <- YOUR structural decision, in one line. Replace `Any`.


def prepare(root: Node) -> Round5Prepared:
    raise NotImplementedError


def serve(prepared: Round5Prepared, query: None = None) -> tuple[str, int]:
    """The name of the top-level region whose subtree holds the most bytes, and how many."""
    raise NotImplementedError


check_round(prepare, serve)
