from fastapi import Request
from fastapi.responses import JSONResponse

from chainbreaker.domain.errors import ChainBreakerError


async def chainbreaker_error_handler(request: Request, exc: ChainBreakerError):
    return JSONResponse({"error": str(exc)}, status_code=400)
