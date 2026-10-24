from enum import StrEnum


class Criticality(StrEnum):
    LIFE_SAFETY = "life-safety"
    ESSENTIAL = "essential"
    CONVENIENCE = "convenience"


class Stage(StrEnum):
    CREDENTIAL_ACCESS = "credential-access"
    INITIAL_ACCESS = "initial-access"
    EXECUTION = "execution"
    PERSISTENCE = "persistence"
    DISCOVERY = "discovery"
    LATERAL_MOVEMENT = "lateral-movement"
    COMMAND_AND_CONTROL = "command-and-control"
    IMPACT = "impact"


class EventSource(StrEnum):
    AUTH = "auth"
    DNS = "dns"
    IOT = "iot"
    PORTAL = "portal"
    VPN = "vpn"


class ActionType(StrEnum):
    REVOKE_SESSION = "revoke_session"
    BLOCK_COMMAND = "block_command"
    BLOCK_TOPIC = "block_topic"
    BLOCK_DOMAIN = "block_domain"
    ISOLATE_HOST = "isolate_host"
