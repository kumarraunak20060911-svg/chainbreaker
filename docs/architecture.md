
# ChainBreaker architecture

ChainBreaker is a Python-only modular monolith. The API and the server-rendered
dashboard call the same analysis pipeline, so a demo action and an API action
produce the same report and Merkle root.

## Flow

1. **Ingest** reads CSV or JSONL, validates each row, keeps rejected-row diagnostics,
   normalizes timestamps, applies explicitly supplied source clock offsets, and
   HMAC-pseudonymizes identity fields.
2. **Resolve** records reversible account/host alias candidates and builds entity
   rarity counts. Public Wi-Fi/NAT flags must be explicit in the source metadata;
   private RFC1918 addresses are not treated as public NAT automatically.
3. **Detect** runs explainable rule-ID detectors for authentication, DNS/network,
   portal/web, and IoT behavior. Findings include the feature values that fired.
4. **Correlate** creates rarity/time-weighted links, down-weights explicit public
   Wi-Fi NAT, strengthens rare external destinations, calibrates synthetic labels
   with isotonic regression, and reports the Brier score.
5. **Infer** builds a forward temporal DAG, applies stage transition priors,
   returns top-k chains, and computes a greedy minimal row justification.
6. **Plan** evaluates revoke-session, block-command, block-topic, block-domain,
   and isolate-host candidates using weighted vertex cuts and collateral costs.
   Life-safety isolation remains visible for comparison but is never an automatic
   recommendation. Every candidate has a counterfactual replay.
7. **Report** stores a deterministic local summary, an optional provider-neutral
   LLM prompt with row citations, calibration details, corrections, decisions,
   and Merkle proofs. No action is executed.

## Persistence and boundaries

SQLite stores run metadata, events, findings, links, reports, and analyst decision
receipts under `runtime/databases`. Runtime data is ignored by Git. The process
keeps the active run in memory for the dashboard, while the database provides a
durable audit record for local runs.

The system accepts synthetic, public, or explicitly authorized logs only. It does
not scan, exploit, block traffic, disable accounts, or send control commands.
