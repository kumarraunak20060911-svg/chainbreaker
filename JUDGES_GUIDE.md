# 🏆 ChainBreaker — Judges Evaluation Guide

**Hackathon ChronoForge · Track: Cybersecurity · Theme: Cities of the Future**  
**Team: PVR** · *Members: Kumar Raunak, Vishesh Sharma*  
**Repository:** [github.com/kumarraunak20060911-svg/chainbreaker](https://github.com/kumarraunak20060911-svg/chainbreaker)  
**📹 Project Running Video:** [Watch Video Demonstration (Google Drive)](https://drive.google.com/file/d/1TIwZt9zTsLzR9PjJZ_ZIAURQcekt0Dkt/view?usp=sharing)  

---

## 🎯 Executive Summary (30-Second Brief)
Cities of the future run on interconnected IT and OT infrastructure: smart traffic signal controllers, EV charging stations, municipal CCTV, public Wi-Fi, and operator portals. 

Two critical flaws plague modern smart-city security:
1. **Correlation collapses in cities:** Shared IP pools (e.g. public Wi-Fi NAT) falsely merge innocent citizen traffic with attacker activity into massive alert fatigue.
2. **Automated containment causes real-world catastrophe:** Isolating a traffic signal controller or shutting down an emergency gateway can cause physical vehicle collisions or municipal blackout.

**ChainBreaker** solves both:
* It uses **calibrated Fellegi-Sunter probabilistic linking** ($w(e, dt) = -\log p(e) \cdot \exp(-dt/T)$) with RFC 1918 NAT penalties to isolate the adversary from benign surges.
* It computes a **safety-tiered Pareto containment frontier** that strictly **locks Life-Safety infrastructure from automated network isolation**, recommending surgical session revocations while cryptographically logging human analyst approval receipts.

---

## ⚡ 1-Minute Launch Instructions

```bash
# Clone and enter directory
git clone https://github.com/kumarraunak20060911-svg/chainbreaker.git
cd chainbreaker

# Quick Launch (Linux / macOS / WSL)
chmod +x start.sh && ./start.sh

# Quick Launch (Windows PowerShell)
.\start.ps1

# Or with Docker Compose (PostgreSQL 16 Multi-Tenant Cloud Stack)
docker compose up -d
```
Open **`http://127.0.0.1:8000`** in your browser.

---

## 🧭 The 5-Minute Evaluation Walkthrough

Follow this 5-step walkthrough specifically designed to showcase every pillar of the ChronoForge proposal:

```
[1. Recreate Attack] ──> [2. Kill Chain] ──> [3. Toggle Naive Mode] ──> [4. Pareto Containment] ──> [5. Merkle Dossier] ──> [6. Societal Resilience]
    /recreate               /incidents/{id}       /toggle-linking         /containment                 /report                   /resilience
```

### Step 1: Recreate the Attack Live (`http://localhost:8000/recreate`)
* Click **Recreate Attack** in the top navigation.
* Select **Central District Traffic (TC-14)**.
* Click `[▶ Auto Play]` or press `Space` to step through the intrusion packet-by-packet:
  1. *02:10 UTC (Credential Access):* Password spray against municipal SSO from `10.20.0.8`.
  2. *02:14 UTC (Initial Access):* Compromised operator `ops_k` valid IPsec VPN session `sess-ops-k`.
  3. *02:16 UTC (Lateral Movement):* Subnet bridge to field gateway `GW-3` managing traffic controllers.
  4. *02:19 UTC (Command & Control):* DGA-like DNS beaconing to `q7k2m9x4v8z1-control.example`.
  5. *02:21 UTC (Impact Attempt):* Off-window MQTT control override `set-phase: FLASHING_YELLOW_ALL` sent to Traffic Controller `TC-14` (Life-Safety Asset)!
* Watch the live Zeek/OT syslog packet stream and the target asset status alert light up in real time.

### Step 2: Inferred Kill Chain & Minimal Justification (`http://localhost:8000/incidents/INC-001`)
* Click **Launch in Full Workbench**.
* **Stage-Aware Viterbi Chain:** View the dynamically rendered SVG graph and kill-chain pipeline maximizing $\sum w(\text{link}) + \sum \log P(\text{stage}_{k+1} \mid \text{stage}_k)$.
* **Minimal Justification Chips:** Inspect the highlighted row chips at the top showing the greedy minimal set of 5 logs that mathematically support the incident.

### Step 3: Judges Demo #3 — Toggle Naive SIEM Mode (`/runs/{id}/toggle-linking`)
* Click the amber banner **"JUDGES DEMO: TOGGLE NAIVE SIEM CORRELATION"**.
* **Naive Mode Active:** Observe how a standard SIEM links events by raw IP matching, incorrectly pulling in 8 innocent citizens on public Wi-Fi NAT `10.0.0.40`.
* **Calibrated Mode Active:** Fellegi-Sunter weight with RFC 1918 NAT penalty ($w=0.08$) mathematically eliminates the benign surge and cleanly isolates the adversary path.

### Step 4: Safety-Tiered Pareto Containment (`/incidents/{id}/containment`)
* Click the **Pareto Containment** tab.
* Look at **Cut C (Isolate Traffic Controller TC-14):**
  * **Status:** `LOCKED — LIFE-SAFETY ASSET`.
  * The system strictly blocks isolating the signal controller to avoid street traffic gridlock or accidents.
* Look at **Cut A (Revoke `ops_k` Session):**
  * **Recommendation:** `RECOMMENDED ACTION`.
  * Severs 82% of evidence links with minimal collateral impact.
* Click **Approve Containment Cut A**: Type an analyst justification (e.g. *"Approved: Revoke operator session pending password reset"*) and click **Submit Decision Receipt**. The decision is cryptographically written to the database audit log.

### Step 5: Cryptographic Audit Dossier & Standards Export (`/incidents/{id}/report`)
* Click the **Merkle Case Report** tab.
* **Merkle Root:** View the SHA-256 tree root computed over all ingested telemetry.
* **Leaf Proof Verification:** Select any evidence row in the verifier dropdown and click **Verify Proof Against Root**. The mathematical verification passes instantaneously.
* **Standards-Compliant Export:** Click **Export STIX 2.1 Bundle** to download structured JSON threat intelligence, or **Export Sigma Rules** for instant ingestion into Wazuh, Splunk, or Elastic.

### Step 6: Societal Impact & Production Dispatcher (`http://localhost:8000/resilience`)
* Click **Societal Impact** in the top navigation bar.
* **Quantified Avoided Economic Loss:** View avoided transit gridlock and energy disruption calculated from US DOT / FHWA benchmarks (**$480,000+ USD saved per incident**).
* **Public Safety & Privacy Index:** Real-time verification that Life-Safety physical services maintained **100% uptime** and citizen privacy remained **100% protected** via HMAC-SHA256 pseudonymization.
* **Production SOAR & Firewall Dispatcher:** Inspect auto-generated, copy-paste ready Linux `iptables`, OpenVPN, and MQTT broker remediation commands, along with standardized JSON webhook payloads for **Cortex XSOAR** and **Wazuh Active Response**.
* **Autonomous OT/IoT Discovery:** See how ChainBreaker automatically detects untagged municipal controllers from raw network streams and elevates them to Life-Safety protection without requiring manual inventory configuration.

---

## 📊 Scientific Metrics & Ablation Suite (Section 8)

| Metric | Score | Benchmark Target | Meaning |
|---|:---:|:---:|---|
| **Incident Clustering ARI** | **1.000** | $> 0.85$ | Perfect clustering separation vs Ground Truth |
| **Correct Chain Rate (CCR)** | **100.0%** | $> 90\%$ | Accurate chronological MITRE stage progression |
| **Time to Detect (TTD)** | **120.0s** | $< 300\text{s}$ | Rapid detection from first attack packet |
| **Brier Score Calibration** | **0.172** | $< 0.25$ | Low probabilistic calibration error (Isotonic) |
| **Ingestion Throughput** | **12,400+ EPS** | $> 1,000\text{ EPS}$ | High performance in-memory stream processing |

To verify offline from the command line:
```bash
python -m pytest tests/ -v
PYTHONPATH=src python evaluation/run_benchmark.py
PYTHONPATH=src python evaluation/run_ablation.py
```

---

## ⚖️ ChronoForge Rubric Alignment

| Judging Criteria | Weight | How ChainBreaker Excels |
|---|:---:|---|
| **Originality & Innovation** | 25% | First platform to combine Fellegi-Sunter entity-rarity linking (fixing the NAT false merge problem) with weighted vertex-cut Pareto containment that protects life-safety infrastructure. |
| **Track Relevance** | 25% | Direct fit for Cybersecurity Track: Multi-source IT/OT correlation, IoT device-class fingerprints, DNS entropy/beaconing detectors, URL indicator analysis, keyed HMAC pseudonymization. |
| **Technical Depth** | 25% | Fully implemented mathematical layers: Viterbi dynamic programming over ATT&CK transition matrices, SHA-256 Merkle proofs, isotonic regression, and hill-climbing adversarial evasion simulation. |
| **Feasibility & Execution** | 15% | Clean, modular Python 3.12 architecture. Zero `.env` files, zero Node.js dependencies. 29/29 unit and integration tests passing in 1.6s. Dual-engine persistence (SQLite / PostgreSQL). |
| **Real-World Impact** | 10% | Directly protects critical urban infrastructure: traffic signals, EV grids, water pumps, power substations, and citizen privacy. Built-in SOAR dispatcher and universal log ingestion. |

---

*ChainBreaker Team PVR · ChronoForge Hackathon 2026*
