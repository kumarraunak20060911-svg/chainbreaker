from collections import Counter


def incident_summary(events, findings, chains, incidents=None):
    return {
        "events": len(events),
        "findings": len(findings),
        "chains": len(chains),
        "incidents": len(incidents or []),
        "top_chain_score": round(chains[0].score, 3) if chains else 0.0,
        "severity_counts": dict(Counter(finding.severity for finding in findings)),
        "stage_counts": dict(Counter(finding.stage.value for finding in findings)),
    }


def build_local_executive_summary(summary, findings, chain=None, citations=()):
    top_rule = findings[0].rule_id if findings else "none"
    stages = " → ".join(getattr(chain, "stage_tags", ())) if chain else "no ordered chain"
    return {
        "mode": "deterministic-local",
        "text": f"Observed {summary['events']} events and {summary['findings']} findings across {summary.get('incidents', 0)} clusters. Top rule: {top_rule}. Ordered path: {stages}.",
        "citations": tuple(citations),
        "disclaimer": "A finding is a reason to investigate, not proof of compromise.",
    }


def build_llm_summary_prompt(summary, findings, chain, citations):
    return {
        "instruction": "Summarize only the supplied incident facts. Cite source row IDs after every claim. Do not recommend or execute containment.",
        "facts": {"summary": summary, "findings": findings, "chain": chain, "citations": citations},
    }
