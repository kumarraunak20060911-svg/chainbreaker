# ChainBreaker

ChainBreaker is a Python-only, read-only security workbench for reconstructing
multi-stage incidents across staff authentication, DNS, web, and connected
device telemetry. It is designed for municipal, campus, and industrial-park
teams that need an explainable answer before they touch a safety-critical
asset.

## What is implemented

* deterministic CSV/JSONL ingestion with schema normalization and HMAC
  pseudonymization;
* explainable authentication, DNS, portal, and IoT detectors;
* rarity/time-weighted evidence links with isotonic calibration;
* stage-aware top-k attack-chain inference and minimal justification rows;
* safety-tiered containment planning with weighted vertex cuts, Pareto ranking,
  and counterfactual replay;
* Merkle-rooted row verification for exported case reports;
* server-rendered analyst dashboard using FastAPI, Jinja2, SVG, and CSS.

No Node.js, JavaScript build step, or `.env` file is required. Configuration is
checked in under `config/default.toml`; secrets are supplied as command-line
arguments or generated locally for a demo run.

## Run the demo

```bash
python -m pip install -r requirements.txt
PYTHONPATH=src python scripts/seed_demo.py
PYTHONPATH=src uvicorn chainbreaker.api.app:app --reload
```

Open `http://127.0.0.1:8000`. The seeded Central District scenario demonstrates
password spray, a valid operator login, a gateway pivot, an off-window traffic
controller command, and DNS beaconing. The containment view is simulation-only
and will never execute a network or account action.

## Checks

```bash
PYTHONPATH=src pytest -q
PYTHONPATH=src python -m compileall -q src tests evaluation scripts
```

## Security posture

ChainBreaker consumes synthetic, public, or explicitly authorized logs. It does
not scan systems, exploit vulnerabilities, disable accounts, or block traffic.
See `SECURITY.md`, `docs/threat-model.md`, and `docs/responsible-use.md`.
