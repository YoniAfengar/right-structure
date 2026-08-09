"""The drop catalog (Round 5). Do not edit.

A node has a name, a size if it is a file, and children if it is not. It has no other methods — no
traversal, no search, no iteration. Those are yours.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Node:
    name: str
    size: int | None = None                    # bytes, iff this node is a file
    children: tuple["Node", ...] = field(default_factory=tuple)

    @property
    def is_file(self) -> bool:
        return self.size is not None


def region(name: str, *children: Node) -> Node:
    """A region: no size of its own, holds other regions and files. May hold nothing."""
    return Node(name=name, children=children)


def file(name: str, size: int) -> Node:
    """A file: a size, no children."""
    return Node(name=name, size=size)
