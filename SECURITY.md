# Security Policy

## Responsible Disclosure

ChainBreaker is a defensive, read-only incident reconstruction and containment planning platform for municipal IT and operational technology (OT). If you discover a security vulnerability or potential risk in ChainBreaker, please report it responsibly:

- **Contact:** Open a private security advisory on GitHub or email the development team.
- **Scope:** ChainBreaker processes logs and telemetry in memory and local databases; it does not execute remote exploits, network scans, or arbitrary code execution.
- **Response Target:** We acknowledge reports within 48 hours and coordinate patches prior to public disclosure.

## Threat Model & Boundaries

1. **Read-Only Telemetry:** ChainBreaker consumes event telemetry (CSV, JSONL, Zeek, Syslog). It does not maintain active management credentials or remote control sessions into live SCADA/PLC equipment without human operator confirmation.
2. **Citizen Privacy:** Cleartext personally identifiable information (PII) like external IP addresses, usernames, and domains are pseudonymized using keyed HMAC-SHA256 upon ingestion.
3. **Safety-Locked Containment:** Physical life-safety controllers (traffic signal heads, emergency preemption, water pumps) are hard-locked against automated isolation recommendations to prevent physical injury or traffic accidents.
