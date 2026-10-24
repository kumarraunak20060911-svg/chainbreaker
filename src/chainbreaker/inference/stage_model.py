from chainbreaker.domain.enums import Stage


def stage_for_event(event_type: str, source: str, *, command: str | None = None) -> Stage:
    text = f"{event_type} {source} {command or ''}".lower()
    if "fail" in text or "spray" in text: return Stage.CREDENTIAL_ACCESS
    if "login" in text or "vpn" in text: return Stage.INITIAL_ACCESS
    if "command" in text or "set-phase" in text: return Stage.IMPACT
    if "dns" in text or "beacon" in text: return Stage.COMMAND_AND_CONTROL
    if "pivot" in text or "gateway" in text: return Stage.LATERAL_MOVEMENT
    return Stage.DISCOVERY
