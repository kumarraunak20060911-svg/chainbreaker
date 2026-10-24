def incident_summary(events, findings, chains):
    return {
        "events": len(events),
        "findings": len(findings),
        "chains": len(chains),
        "top_chain_score": round(chains[0].score, 3) if chains else 0.0,
    }
