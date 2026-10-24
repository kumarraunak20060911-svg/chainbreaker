from .event_graph import graph_edges, graph_nodes
from .stage_model import stage_for_event
from .viterbi import StageAwareViterbi


def infer_chains(events, links, *, top_k=3):
    stages = {event.event_id: stage_for_event(event.event_type, event.source.value, command=event.command).value for event in events}
    nodes = graph_nodes(events, stages)
    edges = graph_edges(links)
    transitions = {"credential-access": {"initial-access": .8}, "initial-access": {"lateral-movement": .7}, "lateral-movement": {"command-and-control": .7, "impact": .6}, "command-and-control": {"impact": .8}}
    return StageAwareViterbi(transitions).infer(nodes, edges, top_k=top_k)
