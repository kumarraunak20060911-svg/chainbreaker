from chainbreaker.reporting.stix_sigma import export_stix_bundle, export_sigma_rules


def test_stix_bundle_generation():
    findings = [
        {"finding_id": "f-1", "title": "Password Spray", "rule_id": "AUTH-BETA-BINOMIAL", "severity": "medium", "stage": "credential-access", "explanation": "Spray detected", "features": {"source_ip": "10.20.0.8"}},
        {"finding_id": "f-2", "title": "Off Window Command", "rule_id": "IOT-OFF-WINDOW", "severity": "high", "stage": "impact", "explanation": "OT override", "features": {}},
    ]
    report = {"summary": "Test incident", "findings": findings}
    bundle = export_stix_bundle("run-123", report)

    assert bundle["type"] == "bundle"
    assert "objects" in bundle
    obj_types = {obj["type"] for obj in bundle["objects"]}
    assert "identity" in obj_types
    assert "threat-actor" in obj_types
    assert "indicator" in obj_types
    assert "relationship" in obj_types


def test_sigma_rules_generation():
    findings = [
        {"finding_id": "f-1", "title": "DNS Beaconing", "rule_id": "DNS-BEACON-PERIODICITY", "severity": "high", "stage": "command-and-control", "explanation": "Low CV interval", "events": ["e1"]},
    ]
    yaml_text = export_sigma_rules("run-123", findings)
    assert "title: ChainBreaker DNS-BEACON-PERIODICITY" in yaml_text
    assert "level: high" in yaml_text
    assert "DNS-BEACON-PERIODICITY" in yaml_text
