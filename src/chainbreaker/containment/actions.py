from chainbreaker.domain.enums import ActionType


DEFAULT_ACTIONS = (
    ActionType.REVOKE_SESSION,
    ActionType.BLOCK_COMMAND,
    ActionType.BLOCK_TOPIC,
    ActionType.BLOCK_DOMAIN,
    ActionType.ISOLATE_HOST,
)
