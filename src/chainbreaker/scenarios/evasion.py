def evasion_knobs() -> dict[str, tuple[float, ...]]:
    return {"rate": (0.5, 1.0, 2.0), "jitter_seconds": (0.0, 5.0, 30.0), "trusted_domain_c2": (0.0, 1.0)}


def hill_climb_evasion(score_fn, *, start: dict[str, float] | None = None, steps: int = 25) -> dict[str, float]:
    """Find a low-detection synthetic configuration without generating attack tooling."""
    current = dict(start or {"rate": 1.0, "jitter_seconds": 0.0, "trusted_domain_c2": 0.0})
    best_score = float(score_fn(current))
    candidates = ("rate", "jitter_seconds", "trusted_domain_c2")
    for _ in range(steps):
        improved = False
        for key in candidates:
            for delta in (-0.25, 0.25):
                proposal = dict(current)
                proposal[key] = max(0.0, proposal[key] + delta)
                score = float(score_fn(proposal))
                if score < best_score:
                    current, best_score, improved = proposal, score, True
        if not improved:
            break
    return current
