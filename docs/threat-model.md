# ChainBreaker Threat Model

ChainBreaker models attacks targeting connected-city cyber-physical infrastructure (smart traffic controllers, EV charging stations, surveillance cameras, municipal water pumps, and operator portals).

## Target Systems & Criticality Tiers

1. **Life-Safety (`LIFE_SAFETY`):**
   - *Assets:* Traffic Signal Controllers (e.g. `TC-14`), Emergency Preemption Systems, Water Treatment RTUs.
   - *Physical Consequence:* Vehicle crashes, traffic gridlock, water pressure failures.
   - *Containment Policy:* **Hard-locked against automated isolation.** Remediation must target upstream VPN sessions or supervisory credentials rather than taking physical hardware offline.

2. **Essential Infrastructure (`ESSENTIAL`):**
   - *Assets:* EV Fast-Charger Grid Managers (e.g. `EV-08`), Power Substation Gateways.
   - *Physical Consequence:* 350kW continuous load surges, transformer tripping, transit fleet depowering.
   - *Containment Policy:* Surgical command filtering (e.g., blocking `max-draw-override`) without disconnecting chargers.

3. **Standard IT & Civic Infrastructure (`STANDARD` / `CIVIC`):**
   - *Assets:* Public Park Wi-Fi, University Portals, Municipal CCTV.
   - *Threat:* Shared NAT correlation collapse (RFC 1918 false merges), unauthorized video streaming.
   - *Defense:* Fellegi-Sunter RFC 1918 NAT penalties ($w=0.08$) and HMAC-SHA256 privacy preservation.

## Adversary Attack Progression (MITRE ATT&CK for Enterprise & ICS)

```
Credential Access  ──>  Initial Access  ──>  Lateral Movement  ──>  Command & Control  ──>  Physical Impact
 (Password Spray)       (Compromised VPN)    (Supervisory Gateway)   (DGA DNS Beaconing)      (OT set-phase Override)
```
