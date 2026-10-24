from __future__ import annotations

from html import escape


def evidence_graph_svg(events, links) -> str:
    if not events:
        return (
            '<svg viewBox="0 0 800 200" width="100%" height="200" role="img" aria-label="Empty Graph">'
            '<rect width="100%" height="100%" fill="#090d16" rx="8"/>'
            '<text x="50%" y="50%" fill="#64748b" text-anchor="middle" font-family="system-ui" font-size="14">'
            'No correlated events in evidence graph</text></svg>'
        )

    # Display up to 10 prominent events cleanly across the canvas
    display_events = list(events)[:10]
    count = len(display_events)
    spacing = max(95, min(140, 860 // max(count, 1)))
    width = max(900, count * spacing + 120)
    height = 290

    # Categorize nodes and assign tiered vertical positions
    # Group by source/stage for an intuitive topology flow
    positions: dict[str, tuple[int, int]] = {}
    for index, event in enumerate(display_events):
        source = getattr(event, "source", None)
        src_val = source.value if hasattr(source, "value") else str(source or "").lower()
        if "auth" in src_val:
            y = 120
        elif "vpn" in src_val:
            y = 175
        elif "iot" in src_val:
            # Stagger IoT devices
            y = 115 if (index % 2 == 0) else 190
        elif "dns" in src_val:
            y = 155
        else:
            y = 130 + (index % 2) * 55
        x = 75 + index * spacing
        positions[event.event_id] = (x, y)

    # Color palettes per telemetry source
    color_map = {
        "auth": {"fill": "#f59e0b", "glow": "rgba(245, 158, 11, 0.25)", "label": "AUTH"},
        "vpn": {"fill": "#6366f1", "glow": "rgba(99, 102, 241, 0.28)", "label": "VPN"},
        "iot": {"fill": "#f43f5e", "glow": "rgba(244, 63, 94, 0.28)", "label": "IOT"},
        "dns": {"fill": "#06b6d4", "glow": "rgba(6, 182, 212, 0.28)", "label": "DNS"},
        "portal": {"fill": "#3b82f6", "glow": "rgba(59, 130, 246, 0.25)", "label": "PORTAL"},
    }

    edges_svg = []
    for link in links:
        if link.left_event_id in positions and link.right_event_id in positions:
            x1, y1 = positions[link.left_event_id]
            x2, y2 = positions[link.right_event_id]
            prob = getattr(link, "probability", 0.5)
            weight = getattr(link, "weight", 0.5)
            
            # Line stroke style by probability
            if prob >= 0.7:
                stroke_color = "#22d3ee"
                stroke_width = 2.5
                glow_opacity = "0.7"
                dash = ""
            elif prob >= 0.4:
                stroke_color = "#818cf8"
                stroke_width = 2.0
                glow_opacity = "0.4"
                dash = ""
            else:
                stroke_color = "#64748b"
                stroke_width = 1.5
                glow_opacity = "0.2"
                dash = 'stroke-dasharray="4,4"'

            # Smooth cubic Bezier curve
            dx = x2 - x1
            mid_x = (x1 + x2) / 2
            ctrl_y = min(y1, y2) - max(25, int(abs(dx) * 0.18)) if dx > 0 else max(y1, y2) + 30
            path_d = f"M {x1} {y1} Q {mid_x} {ctrl_y} {x2} {y2}"

            # Prob badge midpoint along curve
            pill_x = mid_x
            pill_y = (y1 + y2) / 2 + (ctrl_y - (y1 + y2) / 2) * 0.5

            tooltip = escape(
                f"Link: {link.left_event_id} → {link.right_event_id}\n"
                f"Entity: {getattr(link, 'entity_type', '')} ({getattr(link, 'entity_value', '')})\n"
                f"Calibrated Prob: {prob:.3f}\n"
                f"Evidence Weight: {weight:.2f}\n"
                f"Time Gap: {getattr(link, 'delta_seconds', 0)}s"
            )

            edge_elem = (
                f'<g class="edge-group">'
                f'<title>{tooltip}</title>'
                f'<path d="{path_d}" fill="none" stroke="{stroke_color}" stroke-opacity="{glow_opacity}" stroke-width="{stroke_width + 3}"/>'
                f'<path d="{path_d}" fill="none" stroke="{stroke_color}" stroke-width="{stroke_width}" {dash} marker-end="url(#arrow)"/>'
                f'<g transform="translate({pill_x - 22}, {pill_y - 9})">'
                f'<rect width="44" height="18" rx="4" fill="#0f172a" stroke="{stroke_color}" stroke-width="1" fill-opacity="0.95"/>'
                f'<text x="22" y="13" class="prob-text" fill="{stroke_color}">{prob:.2f}</text>'
                f'</g>'
                f'</g>'
            )
            edges_svg.append(edge_elem)

    nodes_svg = []
    for event in display_events:
        x, y = positions[event.event_id]
        source = getattr(event, "source", None)
        src_val = source.value if hasattr(source, "value") else str(source or "iot").lower()
        cfg = color_map.get(src_val, {"fill": "#10b981", "glow": "rgba(16, 185, 129, 0.25)", "label": "EVT"})
        fill_color = cfg["fill"]
        src_tag = cfg["label"]

        # Primary label
        primary = getattr(event, "device_id", None) or getattr(event, "account", None) or getattr(event, "domain", None) or getattr(event, "event_type", "event")
        primary_clean = escape(str(primary)[:16])
        event_id_clean = escape(event.event_id)
        
        # Tooltip content
        tt_items = [
            f"Event ID: {event.event_id}",
            f"Source: {src_val.upper()}",
            f"Type: {getattr(event, 'event_type', '')}",
        ]
        if getattr(event, "account", None):
            tt_items.append(f"Account: {event.account}")
        if getattr(event, "ip", None):
            tt_items.append(f"IP: {event.ip}")
        if getattr(event, "host", None):
            tt_items.append(f"Host: {event.host}")
        if getattr(event, "device_id", None):
            tt_items.append(f"Device: {event.device_id} ({getattr(event, 'device_class', '')})")
        if getattr(event, "command", None):
            tt_items.append(f"Command: {event.command}")
        tooltip = escape("\n".join(tt_items))

        node_elem = (
            f'<g class="node-group" transform="translate({x}, {y})">'
            f'<title>{tooltip}</title>'
            f'<circle cx="0" cy="0" r="28" fill="{fill_color}" fill-opacity="0.15" stroke="{fill_color}" stroke-opacity="0.3" stroke-width="1.5" class="halo"/>'
            f'<circle cx="0" cy="0" r="20" fill="#0f172a" stroke="{fill_color}" stroke-width="2.5" class="node-circle"/>'
            f'<text x="0" y="4" class="node-icon" fill="{fill_color}">{src_tag}</text>'
            f'<text x="0" y="36" class="node-label" fill="#f8fafc">{primary_clean}</text>'
            f'<text x="0" y="49" class="node-id" fill="#64748b">{event_id_clean}</text>'
            f'</g>'
        )
        nodes_svg.append(node_elem)

    return (
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" class="evidence-graph" role="img" aria-label="Evidence Correlation Graph">'
        f'<defs>'
        f'<pattern id="cyber-grid" width="20" height="20" patternUnits="userSpaceOnUse">'
        f'<circle cx="2" cy="2" r="1" fill="#334155" fill-opacity="0.35"/>'
        f'</pattern>'
        f'<marker id="arrow" viewBox="0 0 10 10" refX="24" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        f'<path d="M 0 1 L 10 5 L 0 9 z" fill="#38bdf8"/>'
        f'</marker>'
        f'</defs>'
        f'<style>'
        f'.evidence-graph {{ font-family: "JetBrains Mono", Consolas, system-ui, sans-serif; background: #080c14; border-radius: 8px; }}'
        f'.node-group {{ cursor: pointer; transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1); }}'
        f'.node-group:hover {{ transform: scale(1.08); }}'
        f'.node-group:hover .halo {{ fill-opacity: 0.35; stroke-opacity: 0.8; r: 32; }}'
        f'.node-icon {{ font-size: 9px; font-weight: 800; text-anchor: middle; letter-spacing: 0.05em; }}'
        f'.node-label {{ font-size: 11px; font-weight: 700; text-anchor: middle; }}'
        f'.node-id {{ font-size: 9px; text-anchor: middle; }}'
        f'.prob-text {{ font-size: 9.5px; font-weight: 800; text-anchor: middle; }}'
        f'.edge-group:hover path {{ stroke-width: 3.5; stroke-opacity: 1; }}'
        f'</style>'
        f'<rect width="100%" height="100%" fill="#080c14" rx="8"/>'
        f'<rect width="100%" height="100%" fill="url(#cyber-grid)" rx="8"/>'
        f'{"".join(edges_svg)}'
        f'{"".join(nodes_svg)}'
        f'<g transform="translate(18, {height - 18})">'
        f'<circle cx="0" cy="0" r="4" fill="#f59e0b"/><text x="10" y="3" fill="#94a3b8" font-size="10">Auth</text>'
        f'<circle cx="60" cy="0" r="4" fill="#6366f1"/><text x="70" y="3" fill="#94a3b8" font-size="10">VPN</text>'
        f'<circle cx="115" cy="0" r="4" fill="#f43f5e"/><text x="125" y="3" fill="#94a3b8" font-size="10">IoT / Controller</text>'
        f'<circle cx="230" cy="0" r="4" fill="#06b6d4"/><text x="240" y="3" fill="#94a3b8" font-size="10">DNS Beacon</text>'
        f'<text x="{width - 240}" y="3" fill="#64748b" font-size="10">Hover elements for evidence telemetry</text>'
        f'</g>'
        f'</svg>'
    )
