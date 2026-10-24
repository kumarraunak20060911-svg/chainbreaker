from __future__ import annotations

from datetime import datetime
from html import escape


def _parse_time(val) -> datetime:
    if isinstance(val, datetime):
        return val
    try:
        return datetime.fromisoformat(str(val))
    except Exception:
        return datetime.min


def timeline_svg(events) -> str:
    if not events:
        return (
            '<svg viewBox="0 0 800 120" width="100%" height="120" role="img" aria-label="Empty Timeline">'
            '<rect width="100%" height="100%" fill="#080c14" rx="8"/>'
            '<text x="50%" y="50%" fill="#64748b" text-anchor="middle" font-family="system-ui" font-size="13">'
            'No event timeline available</text></svg>'
        )

    # Sort events by timestamp
    sorted_events = sorted(events, key=lambda e: _parse_time(getattr(e, "timestamp", datetime.min)))
    display_events = sorted_events[:9]
    t0 = _parse_time(getattr(display_events[0], "timestamp", datetime.min))
    
    count = len(display_events)
    spacing = max(90, min(120, 840 // max(count, 1)))
    width = max(900, count * spacing + 100)
    height = 150

    # Draw Stage Corridor Brackets
    stages = [
        {"name": "01 · Recon / Auth", "x1": 40, "x2": 260, "color": "#f59e0b"},
        {"name": "02 · Initial Access", "x1": 275, "x2": 375, "color": "#6366f1"},
        {"name": "03 · Lateral Pivot", "x1": 390, "x2": 490, "color": "#a855f7"},
        {"name": "04 · Critical Impact", "x1": 505, "x2": 720, "color": "#f43f5e"},
        {"name": "05 · C2 Beaconing", "x1": 735, "x2": width - 30, "color": "#06b6d4"},
    ]

    stage_brackets = []
    for st in stages:
        if st["x1"] < width:
            bx2 = min(st["x2"], width - 15)
            mid = (st["x1"] + bx2) / 2
            bracket = (
                f'<path d="M {st["x1"]} 26 L {st["x1"]} 18 L {bx2} 18 L {bx2} 26" fill="none" stroke="{st["color"]}" stroke-opacity="0.35" stroke-width="1.5"/>'
                f'<text x="{mid}" y="14" fill="{st["color"]}" font-size="9.5" font-weight="700" text-anchor="middle" letter-spacing="0.04em">{st["name"]}</text>'
            )
            stage_brackets.append(bracket)

    # Spine line
    y_axis = 78
    spine_x1 = 50
    spine_x2 = 50 + (count - 1) * spacing
    spine = (
        f'<line x1="{spine_x1}" y1="{y_axis}" x2="{spine_x2}" y2="{y_axis}" stroke="#334155" stroke-width="2.5" stroke-linecap="round"/>'
        f'<line x1="{spine_x1}" y1="{y_axis}" x2="{spine_x2}" y2="{y_axis}" stroke="#38bdf8" stroke-opacity="0.25" stroke-width="6" stroke-linecap="round"/>'
    )

    markers_svg = []
    for idx, event in enumerate(display_events):
        x = 50 + idx * spacing
        t_curr = _parse_time(getattr(event, "timestamp", datetime.min))
        delta_sec = int((t_curr - t0).total_seconds()) if t_curr >= t0 else 0
        minutes, seconds = divmod(delta_sec, 60)
        time_tag = f"+{minutes:02d}:{seconds:02d}"

        etype = getattr(event, "event_type", "event")
        source = getattr(event, "source", None)
        src_val = source.value if hasattr(source, "value") else str(source or "iot").lower()

        # Is attack event or life safety
        is_critical = etype in {"gateway_pivot", "control_command", "set-phase"} or getattr(event, "device_id", "") == "TC-14"
        is_attack = is_critical or event.event_id in {"evt-004", "evt-005", "evt-006", "evt-007"}

        if is_critical:
            dot_color = "#f43f5e"
            dot_glow = "rgba(244, 63, 94, 0.4)"
        elif is_attack:
            dot_color = "#38bdf8"
            dot_glow = "rgba(56, 189, 248, 0.35)"
        elif "login_failure" in etype:
            dot_color = "#f59e0b"
            dot_glow = "rgba(245, 158, 11, 0.3)"
        else:
            dot_color = "#10b981"
            dot_glow = "rgba(16, 185, 129, 0.25)"

        label_primary = escape(getattr(event, "command", None) or getattr(event, "device_id", None) or getattr(event, "account", None) or etype)
        if len(label_primary) > 13:
            label_primary = label_primary[:11] + "…"

        tooltip = escape(
            f"Event: {event.event_id}\n"
            f"Time: {time_tag} ({getattr(event, 'timestamp', '')})\n"
            f"Source: {src_val.upper()}\n"
            f"Action: {etype}\n"
            f"Entity: {getattr(event, 'device_id', None) or getattr(event, 'account', None) or getattr(event, 'domain', '')}"
        )

        marker = (
            f'<g class="time-node" transform="translate({x}, {y_axis})">'
            f'<title>{tooltip}</title>'
            f'<text x="0" y="-18" class="time-label" fill="#94a3b8">{time_tag}</text>'
            f'<circle cx="0" cy="0" r="14" fill="{dot_color}" fill-opacity="0.18" stroke="{dot_color}" stroke-opacity="0.4" stroke-width="1.5" class="time-halo"/>'
            f'<circle cx="0" cy="0" r="7" fill="#0f172a" stroke="{dot_color}" stroke-width="2.5"/>'
            f'<text x="0" y="24" class="event-id" fill="#f8fafc">{escape(event.event_id)}</text>'
            f'<text x="0" y="38" class="event-desc" fill="#64748b">{label_primary}</text>'
            f'</g>'
        )
        markers_svg.append(marker)

    return (
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" class="timeline-svg" role="img" aria-label="Incident Attack Timeline">'
        f'<style>'
        f'.timeline-svg {{ font-family: "JetBrains Mono", Consolas, system-ui, sans-serif; background: #080c14; border-radius: 8px; }}'
        f'.time-node {{ cursor: pointer; }}'
        f'.time-node .time-halo {{ transition: fill-opacity 0.2s ease, stroke-opacity 0.2s ease; }}'
        f'.time-node:hover .time-halo {{ fill-opacity: 0.5; stroke-opacity: 0.9; stroke-width: 2.5; }}'
        f'.time-label, .event-id, .event-desc {{ pointer-events: none; }}'
        f'.time-label {{ font-size: 10px; font-weight: 700; text-anchor: middle; }}'
        f'.event-id {{ font-size: 10px; font-weight: 800; text-anchor: middle; }}'
        f'.event-desc {{ font-size: 9px; text-anchor: middle; }}'
        f'</style>'
        f'<rect width="100%" height="100%" fill="#080c14" rx="8"/>'
        f'{"".join(stage_brackets)}'
        f'{spine}'
        f'{"".join(markers_svg)}'
        f'</svg>'
    )
