from html import escape


def evidence_graph_svg(events, links) -> str:
    width, height = 860, 280
    positions = {event.event_id: (80 + index * 120, 130 + (index % 2) * 40) for index, event in enumerate(events[:7])}
    nodes = []
    for event in events[:7]:
        x, y = positions[event.event_id]
        label = escape(event.device_id or event.account or event.domain or event.event_type)
        nodes.append(f'<circle cx="{x}" cy="{y}" r="26" class="node"/><text x="{x}" y="{y + 45}" class="label">{label}</text>')
    edges = []
    for link in links:
        if link.left_event_id in positions and link.right_event_id in positions:
            x1, y1 = positions[link.left_event_id]; x2, y2 = positions[link.right_event_id]
            edges.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="edge"/><text x="{(x1+x2)//2}" y="{(y1+y2)//2 - 8}" class="weight">p={link.probability:.2f}</text>')
    return f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Evidence graph"><style>.node{{fill:#a6b23b;stroke:#3d2615;stroke-width:3}}.edge{{stroke:#987e66;stroke-width:3}}.label,.weight{{font:12px system-ui;fill:#3d2615;text-anchor:middle}}.weight{{font-weight:700}}</style>{"".join(edges)}{"".join(nodes)}</svg>'
