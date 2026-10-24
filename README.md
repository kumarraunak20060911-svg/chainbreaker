# ChainBreaker
**Safety-Aware Incident Reconstruction & Containment Planning for Connected-City Infrastructure**

*Hackathon ChronoForge · Track: Cybersecurity · Team: PVR (Kumar Raunak, Vishesh Sharma) · Theme: Cities of the Future*

ChainBreaker is an explainable, read-only security investigation platform built for connected-city infrastructure (traffic signal controllers, EV chargers, CCTV networks, smart campus grids, and municipal operator portals). It correlates multi-source IT and OT activity into a temporal evidence graph, infers the most plausible attack chain, and simulates Pareto-ranked containment options that strictly respect life-safety service limits.

---

## ⚡ Quick Start (Zero Config, No `.env` or Node.js Required)

ChainBreaker runs out of the box with zero external dependencies. The persistence engine automatically provisions a local SQLite database at `runtime/databases/chainbreaker.sqlite3` or connects to PostgreSQL if configured.

### Linux / macOS / WSL:
```bash
chmod +x start.sh && ./start.sh
```

### Windows PowerShell:
```powershell
.\start.ps1
```

### Manual Python Command:
```bash
python -m uvicorn chainbreaker.api.app:app --host 127.0.0.1 --port 8000 --reload
```

Open `http://127.0.0.1:8000` in your browser.

---

## 🎯 5-Step Judges Demonstration Flow (Proposal Page 3)

The UI has been specifically engineered to fulfill the 5-step evaluation protocol defined in the hackathon proposal:

1. **Step 1: Recreate or Ingest Connected-City Attack**
   - Navigate to `/recreate` or `/scenarios` and select **Central District Traffic Signal Intrusion**.
   - Watch the attack unfold step-by-step: password spray (02:10 UTC) $\rightarrow$ operator VPN access (02:14 UTC) $\rightarrow$ OT gateway pivot $\rightarrow$ DGA DNS beaconing $\rightarrow$ unauthorized physical `set-phase` command to Traffic Controller TC-14 outside maintenance windows.

2. **Step 2: Inspect Ordered Chain & Minimal Justification**
   - Click **Launch in Full Workbench** (`/incidents/{id}`).
   - View the Viterbi dynamic program attack path maximizing $\sum w(\text{link}) + \sum \log P(\text{stage}_{k+1} \mid \text{stage}_k)$.
   - Inspect the **Minimal Justification** chip row identifying the minimum subset of 5 log rows that mathematically support the incident.

3. **Step 3: Toggle Naive Linking vs Calibrated Fellegi-Sunter Model**
   - In the banner or at `/runs/{id}/toggle-linking`, click **Toggle Naive SIEM Mode**.
   - **Naive Field Matching:** Falsely merges 8 benign citizens on public Wi-Fi NAT (`10.0.0.40`), bloating the graph into alert fatigue.
   - **ChainBreaker Calibrated Linking:** Fellegi-Sunter weight $w(e, dt) = -\log p(e) \cdot \exp(-dt/T)$ applies RFC 1918 NAT penalties ($w=0.08$), cleanly isolating the true adversary chain.

4. **Step 4: Safety-Aware What-If Containment & Replay**
   - Open **Pareto Containment** (`/incidents/{id}/containment`).
   - Observe that **Cut C (Isolate Traffic Controller TC-14)** is flagged **LOCKED (LIFE-SAFETY)** to prevent street traffic gridlock or accidents.
   - **Cut A (Revoke `ops_k` session)** is recommended with 82% evidence severed and low collateral cost.
   - Submit an analyst approval receipt with justification to log the human decision cryptographically in the database.

5. **Step 5: Cryptographic Audit Dossier & Export**
   - Open **Merkle Case Report** (`/incidents/{id}/report`).
   - Verify any raw event row against the SHA-256 Merkle root with an interactive leaf inclusion proof.
   - Export machine-readable artifacts: **STIX 2.1 Bundle (JSON)** and **Sigma Detection Rule (YAML)**.

---

## 🏙️ Connected-City Threat Scenarios

ChainBreaker includes 4 fully modeled smart-city incident scenarios (`src/chainbreaker/scenarios/`):

* **Central District Traffic Signal Intrusion (TC-14):** External password spray $\rightarrow$ operator VPN $\rightarrow$ supervisory gateway GW-3 $\rightarrow$ off-window `set-phase: FLASHING_YELLOW_ALL` override on life-safety traffic controller TC-14.
* **Perimeter CCTV Pivot to EV Fast Charger Grid (EV-08):** Compromised RTSP camera CAM-22 $\rightarrow$ first-seen C2 domain `trusted-update.example` $\rightarrow$ Modbus pivot $\rightarrow$ unauthorized `max-draw-override` current surge risking grid transformer trips.
* **Public Wi-Fi NAT Surge vs Intrusion (Judges Demo #3):** Interleaves the Central District attack with 8 benign park visitors and transit commuters on NAT `10.0.0.40`. Demonstrates how naive SIEM correlation collapses while ChainBreaker remains mathematically precise.
* **University Campus Identity & Facility Intrusion (LAB-CAM-7):** Compromised student credentials over campus-NAT $\rightarrow$ VPN session $\rightarrow$ web portal path traversal on `/grades` $\rightarrow$ unauthorized recording export command on cleanroom camera LAB-CAM-7.

---

## 🔬 Scientific Evaluation & Architectural Ablations (Section 8)

| Pipeline Variant | Incident ARI | Correct Chain Rate (CCR) | Brier Calibration | Operational Consequence |
|---|:---:|:---:|:---:|---|
| **ChainBreaker Full Pipeline** | **1.000** | **100.0%** | **0.172** | **Optimal Baseline:** Zero false merges on public Wi-Fi NAT |
| **Ablation 1: Naive Field Linking** | 0.385 | 66.7% | 0.589 | **Critical Degradation:** Falsely bundles 8 benign citizens into attack cluster |
| **Ablation 2: Uniform Stage Prior** | 0.840 | 71.4% | 0.290 | **Causality Loss:** Inferrer misorders lateral movement before authentication |
| **Ablation 3: No Clock Skew Correction**| 0.720 | 50.0% | 0.340 | **OT Drift:** Off-window OT commands falsely appear inside maintenance windows |
| **Ablation 4: 20% Dropped Syslog Fields**| 0.912 | 88.5% | 0.215 | **Resilient:** Fellegi-Sunter priors maintain attack path even with packet loss |

Run evaluation sweeps from the terminal:
```bash
PYTHONPATH=src python evaluation/run_benchmark.py
PYTHONPATH=src python evaluation/run_ablation.py
```

---

## 🛡️ Architecture & Technology Stack

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CHAINBREAKER SOC ARCHITECTURE                   │
├────────────────────────────────────────────────────────────────────────┤
│ 1. INGESTION & NORMALIZATION (Python, Pydantic, HMAC-SHA256)           │
│    CSV/JSONL parse · RFC 3339 timestamps · Keyed pseudonymization     │
├────────────────────────────────────────────────────────────────────────┤
│ 2. DETECTOR SUITE (Explainable, Rule-ID tagged)                        │
│    Auth Beta-binomial · DNS Count-Min / Entropy · IoT Fingerprints     │
├────────────────────────────────────────────────────────────────────────┤
│ 3. CORRELATION & INFERENCE (NetworkX, Scipy, Fellegi-Sunter)           │
│    w(e,dt) = -log p(e) * exp(-dt/T) · Viterbi DAG · Min-Cut Pareto     │
├────────────────────────────────────────────────────────────────────────┤
│ 4. PERSISTENCE & AUDIT (SQLAlchemy 2.x, SQLite / PostgreSQL 16)        │
│    Runs · Events · Findings · Decisions · Merkle Tree SHA-256          │
├────────────────────────────────────────────────────────────────────────┤
│ 5. OPERATOR CONSOLE (FastAPI, Jinja2, SVG, Pure Vanilla CSS/JS)        │
│    Zero Node.js · Dark SOC design · STIX 2.1 & Sigma rule export      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Docker Deployment

### Standalone (Zero Configuration):
```bash
docker build -t chainbreaker .
docker run -p 8000:8000 chainbreaker
```

### Full Multi-Tenant Cloud Stack (PostgreSQL 16 + Web):
```bash
docker compose up -d
```

---

## 📋 Security & Responsible Use

ChainBreaker is strictly read-only and defensive. It processes synthetic, public, or explicitly authorized logs. It will never scan external networks, exploit vulnerabilities, or automatically terminate physical infrastructure. All containment options require human analyst authorization.
