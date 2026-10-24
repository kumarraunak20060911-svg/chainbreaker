from __future__ import annotations

from chainbreaker.domain.models import Event, EvidenceLink
from .viterbi import StageEdge, StageNode


def graph_nodes(events: list[Event], stage_by_event: dict[str, str]) -> list[StageNode]:
    return [StageNode(event.event_id, event.timestamp, stage_by_event.get(event.event_id, "discovery"), (event.row_id or event.event_id,)) for event in events]


def graph_edges(links: list[EvidenceLink]) -> list[StageEdge]:
    return [StageEdge(link.link_id, link.left_event_id, link.right_event_id, link.weight, link.row_ids) for link in links]
