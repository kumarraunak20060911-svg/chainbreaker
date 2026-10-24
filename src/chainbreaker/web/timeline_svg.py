def timeline_svg(events) -> str:
    width = 860
    stages = ["credential access", "initial access", "lateral movement", "command and control", "impact"]
    points = []
    for index, stage in enumerate(stages):
        x = 80 + index * 175
        points.append(f'<circle cx="{x}" cy="70" r="9"/><text x="{x}" y="48">{stage}</text>')
        if index: points.append(f'<line x1="{x-175}" y1="70" x2="{x}" y2="70"/>')
    return f'<svg viewBox="0 0 {width} 110" class="timeline"><style>.timeline{{width:100%;height:auto}}line{{stroke:#7f8b17;stroke-width:3}}circle{{fill:#a6b23b;stroke:#3d2615;stroke-width:2}}text{{font:11px system-ui;text-anchor:middle;fill:#3d2615}}</style>{"".join(points)}</svg>'
