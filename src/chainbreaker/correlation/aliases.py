from collections import defaultdict
from typing import Iterable

from chainbreaker.domain.models import Event


def infer_aliases(events: Iterable[Event]) -> dict[str, set[str]]:
    aliases: defaultdict[str, set[str]] = defaultdict(set)
    for event in events:
        if event.account and event.host:
            aliases[event.account].add(event.host)
    return dict(aliases)
