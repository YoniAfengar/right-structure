"""Round 5 — which region is costing us the most storage?"""
from __future__ import annotations

from typing import TypeAlias

from given.catalog import Node
from given.round import check_round

Round5Prepared: TypeAlias = tuple[str, int] 

def _total_size(node: Node) -> int:
    """Return the total size of the subtree rooted at this node."""
    if node.size is not None:
        return node.size
    else:
        return sum(_total_size(child) for child in node.children)
    
def prepare(root: Node) -> Round5Prepared:
    top_region_name = ""
    top_region_size = 0

    for region in root.children:
        region_size = _total_size(region)

        if region_size > top_region_size:
            top_region_size = region_size
            top_region_name = region.name

    return (top_region_name, top_region_size)

def serve(prepared: Round5Prepared, query: None = None) -> tuple[str, int]:
    """The name of the top-level region whose subtree holds the most bytes, and how many."""
    return prepared


check_round(prepare, serve)
