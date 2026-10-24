class ChainBreakerError(Exception):
    """Base error surfaced as a safe application response."""


class InputValidationError(ChainBreakerError):
    pass


class UnsafeActionError(ChainBreakerError):
    pass
