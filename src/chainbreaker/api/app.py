from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from chainbreaker.domain.errors import ChainBreakerError
from chainbreaker.web.app import router as web_router
from .errors import chainbreaker_error_handler
from .routes import containment, evidence, health, incidents, reports, upload


app = FastAPI(title="ChainBreaker", version="0.1.0", description="Explainable, safety-aware incident reconstruction")
app.mount("/static", StaticFiles(directory=Path(__file__).parents[1] / "web" / "static"), name="static")
app.add_exception_handler(ChainBreakerError, chainbreaker_error_handler)
app.include_router(health.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(incidents.router, prefix="/api")
app.include_router(evidence.router, prefix="/api")
app.include_router(containment.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(web_router)
