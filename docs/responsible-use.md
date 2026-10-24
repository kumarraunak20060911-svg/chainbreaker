# Responsible Use Guidelines

ChainBreaker is strictly an explainable, defensive incident reconstruction platform.

## Core Operational Constraints

1. **Read-Only Telemetry:** ChainBreaker consumes log events and telemetry. It will never send active network probes, run vulnerability scans, or interact with external target infrastructure without authorization.
2. **Human-in-the-Loop Mandatory:** No containment action is ever automatically executed against production physical equipment. Every recommended cut requires human analyst approval, justified with an immutable audit receipt.
3. **No Life-Safety Isolation:** Under no circumstances will ChainBreaker automatically isolate a life-safety physical device (such as a traffic controller or water pump). The system explicitly requires analysts to choose surgical upstream network cuts (e.g. revoking compromised operator VPN sessions).
4. **Citizen Privacy Preservation:** All citizen identifiers from public networks (public Wi-Fi, transit access points) are pseudonymized via HMAC-SHA256 upon ingestion to protect civil liberties and prevent surveillance misuse.
