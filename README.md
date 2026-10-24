# ChainBreaker

ChainBreaker is a Python-only, read-only security investigation platform for
universities and small-to-medium organizations. It correlates authentication,
VPN, DNS, web, and IoT activity into a tenant-scoped temporal evidence graph,
then gives analysts an explainable investigation timeline and safety-aware
containment simulation. It does not claim that correlation proves compromise,
and it never executes account, network, or device containment actions.

## What is implemented

* deterministic CSV/JSONL ingestion with schema normalization and HMAC
  pseudonymization;
* explainable authentication, DNS, portal, and IoT detectors;
* rarity/time-weighted evidence links with isotonic calibration;
* stage-aware top-k attack-chain inference and minimal justification rows;
* safety-tiered containment planning with weighted vertex cuts, Pareto ranking,
  counterfactual replay, and human decision receipts;
* Merkle-rooted row verification for exported case reports;
* server-rendered analyst dashboard using FastAPI, Jinja2, SVG, and CSS;
* synthetic benchmark metrics for precision/recall/F1, incident ARI, correct-chain
  rate, time to detect, events per second, Brier score, and ablation metadata.
* PostgreSQL-first persistence with SQLAlchemy 2.x, Alembic migrations, tenant,
  event, finding, case, evidence-graph, job, and audit tables;
* durable asynchronous ingestion jobs with status/progress APIs, idempotent event
  fingerprints, duplicate counts, bounded analysis windows, and retry-safe leases;
* paginated event/finding/case APIs, production authentication boundary, health
  checks, Docker Compose deployment, and scale-benchmark tooling.

No Node.js, JavaScript build step, `.env` file, or `requirements.txt` is required.
Configuration is checked in under `config/default.toml`; production secrets are
provided through the process environment or a secret manager.

## Run the demo

```bash
python -m pip install -e ".[dev]"
CHAINBREAKER_ENVIRONMENT=test python -m pytest -q
CHAINBREAKER_ENVIRONMENT=test PYTHONPATH=src python scripts/seed_demo.py
CHAINBREAKER_ENVIRONMENT=test PYTHONPATH=src python -m uvicorn chainbreaker.api.app:app --reload
```

Open `http://127.0.0.1:8000`. The seeded Central District scenario demonstrates
password spray, a valid operator login, a gateway pivot, an off-window traffic
controller command, and DNS beaconing. The containment view is simulation-only
and will never execute a network or account action.

## Checks

```bash
PYTHONPATH=src pytest -q
PYTHONPATH=src python -m compileall -q src tests evaluation scripts
PYTHONPATH=src python evaluation/run_benchmark.py
PYTHONPATH=src python evaluation/run_ablation.py
PYTHONPATH=src python scripts/scale_benchmark.py --events 10000 100000
```

The dashboard includes `/metrics`, `/runs/<run_id>/evidence`,
`/runs/<run_id>/containment`, `/runs/<run_id>/replay`, and
`/runs/<run_id>/report`. Uploads may include optional asset and device-inventory
files so criticality and IoT baselines come from the authorized site inventory.

## PostgreSQL deployment

```bash
export CHAINBREAKER_ENVIRONMENT=production
export CHAINBREAKER_DATABASE_URL='postgresql+psycopg://chainbreaker:<password>@localhost:5432/chainbreaker'
export CHAINBREAKER_API_TOKEN='<long-random-token>'
python -m alembic upgrade head
python -m uvicorn chainbreaker.api.app:app --host 0.0.0.0 --port 8000
```

Or use Docker Compose without an `.env` file:

```bash
export CHAINBREAKER_POSTGRES_PASSWORD='use-a-secret-manager-value'
export CHAINBREAKER_API_TOKEN='use-a-secret-manager-value'
docker compose up --build
```

PostgreSQL stores organizations, users, data sources, ingestion jobs, events,
findings, cases, graph nodes/edges, reports, and audit events. The worker parses
CSV/JSONL in batches, isolates malformed rows, pseudonymizes before persistence,
counts duplicates with stable fingerprints, and analyzes a bounded window for
large datasets while retaining all ingested events in PostgreSQL.

Production API calls require `Authorization: Bearer $CHAINBREAKER_API_TOKEN`,
`X-Organization-ID`, and `X-User-ID`.

## Current production limitations

The repository now has a real persistence and job foundation, but it is not a
claim of production readiness. Authentication is a bearer-token boundary rather
than a complete OIDC/SAML identity-provider integration; organization provisioning
and role administration remain deployment tasks; the in-process worker is
single-node until queue-depth measurements justify a supervised worker service;
and million-event end-to-end capacity must be measured on target hardware before
capacity claims are made.

## Security posture

ChainBreaker consumes synthetic, public, or explicitly authorized logs. It does
not scan systems, exploit vulnerabilities, disable accounts, or block traffic.
See `SECURITY.md`, `docs/threat-model.md`, and `docs/responsible-use.md`.
