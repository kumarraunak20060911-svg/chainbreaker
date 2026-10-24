# ChainBreaker Data Model

ChainBreaker models smart-city incident reconstruction using four core data layers:

```
Telemetry Events  ──>  Detection Findings  ──>  Evidence Links  ──>  Inferred Chains & Containment
 (Normalised CSV)       (Rule-ID tagged)        (Fellegi-Sunter)        (Viterbi DAG / Pareto Cut)
```

## 1. Event (`chainbreaker.domain.models.Event`)
The atomic normalized unit of telemetry ingested from IT and OT sources:
- `event_id`: Unique deterministic hash ID.
- `timestamp`: UTC timestamp with applied clock skew compensation.
- `source`: Log source origin (e.g. `zeek-dns`, `syslog-auth`, `mqtt-traffic`).
- `account`, `ip`, `host`, `device_id`, `session_id`: Entity identifiers (HMAC-pseudonymized for PII).
- `command`, `stage`: Associated activity and MITRE ATT&CK stage hint.
- `network_zone`: Segment identifier (e.g. `public-wifi`, `ot-supervisory`, `traffic-control`).

## 2. Detection Finding (`chainbreaker.detection.finding.DetectionFinding`)
Explainable detector alerts tagged with mathematical evidence:
- `finding_id`: Unique identifier.
- `event_id`: Triggering event.
- `rule_id`: Identifier (e.g. `IOT-MAINTENANCE-WINDOW-BREACH`, `DNS-DGA-ENTROPY`, `AUTH-SPRAY-BETA-BINOMIAL`).
- `severity`: Severity level (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
- `features`: Feature dict containing triggering values (e.g. calculated entropy, command name).

## 3. Evidence Link (`chainbreaker.domain.models.EvidenceLink`)
Probabilistic connection between two events sharing entities across time:
- `left_event_id`, `right_event_id`: Linked events.
- `entity_type`, `entity_value`: Shared pivot.
- `weight`: Fellegi-Sunter rarity/time weight: $w(e, dt) = -\log p(e) \cdot \exp(-dt/T)$.
- `probability`: Calibrated linkage probability (isotonic regression).

## 4. Candidate Action (`chainbreaker.domain.models.CandidateAction`)
Pareto containment options evaluated over the evidence graph min-cut:
- `action_id`, `action_type`: Remediation type (`REVOKE_SESSION`, `BLOCK_COMMAND`, `ISOLATE_HOST`).
- `target_id`: Affected asset or identity.
- `evidence_severed`: Fraction of malicious flow disrupted.
- `criticality`: Asset criticality tier (`LIFE_SAFETY`, `ESSENTIAL`, `STANDARD`).
- `auto_recommendable`: Strictly `False` for `LIFE_SAFETY` assets to protect physical operations.
