def evasion_knobs() -> dict[str, tuple[float, ...]]:
    return {"rate": (0.5, 1.0, 2.0), "jitter_seconds": (0.0, 5.0, 30.0), "trusted_domain_c2": (0.0, 1.0)}
