# Proposal coverage audit

Audited against `vr.pdf` (ChronoForge Cybersecurity Proposal, pages 1–3).

| Proposal idea | Repository implementation | Status |
| --- | --- | --- |
| CSV/JSONL event intake | `ingest/service.py`, upload UI and `/api/ingest` | Complete |
| Schema normalization and bad-row handling | `ingest/schemas.py`, `ingest/diagnostics.py` | Complete |
| HMAC pseudonymization | `ingest/pseudonymize.py` | Complete |
| Merkle-verifiable evidence | `ingest/merkle.py`, report verification route | Complete |
| Clock-skew correction | Explicit per-source `clock_offset_seconds`, correction receipt | Complete, conservative |
| Reversible alias correction | `correlation/aliases.py`, report corrections | Complete |
| Rarity/time-weighted Fellegi–Sunter-style links | `correlation/link_weights.py` | Complete |
| Public-Wi-Fi NAT suppression | Explicit NAT metadata, link penalty and UI fields | Complete |
| Rare external-IP strengthening | IP classification and link scoring | Complete |
| Isotonic calibration and Brier score | `EvidenceLinkEngine` and calibration report | Complete |
| IoT behavioral fingerprints | `detection/iot.py`, inventory profiles | Complete |
| MITRE Enterprise/ICS stage tagging | `inference/stage_model.py` | Complete |
| Stage-aware top-k Viterbi inference | `inference/viterbi.py` | Complete |
| Greedy minimal justification | `minimal_justification` set-cover step | Complete |
| Incident clustering | `correlation/clustering.py` connected components | Complete |
| Weighted vertex-cut planner | `containment/min_cut.py` | Complete |
| Revoke/block/isolate candidate actions | `containment/service.py` | Complete |
| Pareto frontier | `containment/pareto.py` | Complete |
| Life-safety protection | domain policy, planner, tests, UI | Complete |
| Counterfactual replay | `containment/replay.py`, replay UI/report | Complete |
| Human approval and decision receipt | containment decision API and SQLite table | Complete |
| DNS n-gram/entropy/rate/beacon/rarity | `detection/dns.py`, `detection/statistics.py` | Complete |
| Portal look-alike, URL indicators, host bursts | `detection/portal.py` | Complete |
| Authentication spray/Beta-binomial/CUSUM | `detection/auth.py` | Complete |
| Synthetic attack scenarios | `scenarios/generator.py` | Complete |
| Benign near-miss catalog | `scenarios/benign_cases.py` | Complete |
| Evasion knobs and hill climbing | `scenarios/evasion.py` | Complete |
| Precision/recall/F1, ARI, chain rate, TTD, throughput, Brier | `chainbreaker/evaluation/metrics.py` and evaluation scripts | Complete |
| Naive vs weighted and ablation metadata | `evaluation/run_ablation.py` | Complete |
| Server-rendered graph/timeline/link inspector | `web/templates`, SVG helpers | Complete |
| Audit-ready report and local summary | `reporting/`, report route | Complete |
| Optional LLM summary with citations | provider-neutral prompt plus deterministic local summary | Complete, opt-in |
| React/Vite/Cytoscape wireframe | intentionally not used | Replaced by Python/SVG because Node is prohibited |
| Post-hackathon STIX/Sigma/Wazuh adapters | documented as future integration direction | Deferred by proposal scope |

The only intentionally conservative choice is clock correction: timestamps are
shifted only when a source explicitly supplies `clock_offset_seconds`, avoiding
unsafe inference that mistakes real cross-source event order for clock drift.
