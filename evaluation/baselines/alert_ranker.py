def rank_findings(findings):
    severity = {"critical": 3, "high": 2, "medium": 1, "low": 0}
    return sorted(findings, key=lambda finding: severity.get(finding.severity, 0), reverse=True)
