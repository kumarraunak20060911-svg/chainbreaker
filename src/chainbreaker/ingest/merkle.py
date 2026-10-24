"""Deterministic row hashing and Merkle proofs for case reports."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence


def canonical_row_bytes(row: Mapping[str, Any]) -> bytes:
    return json.dumps(dict(row), sort_keys=True, separators=(",", ":"), default=str).encode()


def row_hash(row: Mapping[str, Any]) -> str:
    return hashlib.sha256(b"chainbreaker:row:v1:" + canonical_row_bytes(row)).hexdigest()


def _pair(left: str, right: str) -> str:
    return hashlib.sha256(b"chainbreaker:node:v1:" + bytes.fromhex(left) + bytes.fromhex(right)).hexdigest()


@dataclass(frozen=True, slots=True)
class MerkleProof:
    leaf_hash: str
    index: int
    siblings: tuple[tuple[str, str], ...]
    root: str


class MerkleTree:
    def __init__(self, rows: Sequence[Mapping[str, Any]]) -> None:
        self.leaves = tuple(row_hash(row) for row in rows)
        current = list(self.leaves) or [row_hash({})]
        levels = [current]
        while len(current) > 1:
            current = [_pair(current[i], current[i + 1] if i + 1 < len(current) else current[i]) for i in range(0, len(current), 2)]
            levels.append(current)
        self.levels = tuple(tuple(level) for level in levels)

    @property
    def root(self) -> str:
        return self.levels[-1][0]

    def proof(self, index: int) -> MerkleProof:
        if not 0 <= index < len(self.leaves):
            raise IndexError("leaf index out of range")
        position = index
        siblings: list[tuple[str, str]] = []
        for level in self.levels[:-1]:
            sibling = position - 1 if position % 2 else position + 1
            sibling = sibling if sibling < len(level) else position
            siblings.append(("left" if position % 2 else "right", level[sibling]))
            position //= 2
        return MerkleProof(self.leaves[index], index, tuple(siblings), self.root)

    @staticmethod
    def verify(proof: MerkleProof) -> bool:
        current = proof.leaf_hash
        for side, sibling in proof.siblings:
            current = _pair(sibling, current) if side == "left" else _pair(current, sibling)
        return current == proof.root
