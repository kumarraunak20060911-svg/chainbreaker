import hmac
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from chainbreaker.domain.errors import ChainBreakerError
from chainbreaker.observability import configure_logging, observe_request
from chainbreaker.settings import Settings
from chainbreaker.web.app import router as web_router
from .errors import chainbreaker_error_handler
from .routes import cases, containment, evidence, events, findings, health, incidents, jobs, reports, upload


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = Settings.load()
    if settings.environment != "test":
        from chainbreaker.ingest.jobs import recover_pending_jobs
        recover_pending_jobs(settings=settings)
    yield


app = FastAPI(title="ChainBreaker", version="0.2.0", description="Explainable, safety-aware incident reconstruction", lifespan=lifespan)
configure_logging()
app.mount("/static", StaticFiles(directory=Path(__file__).parents[1] / "web" / "static"), name="static")
app.add_exception_handler(ChainBreakerError, chainbreaker_error_handler)
app.include_router(health.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(findings.router, prefix="/api")
app.include_router(cases.router, prefix="/api")
app.include_router(incidents.router, prefix="/api")
app.include_router(evidence.router, prefix="/api")
app.include_router(containment.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(web_router)


@app.middleware("http")
async def production_auth_boundary(request: Request, call_next):
    started = __import__("time").perf_counter()
    settings = __import__("chainbreaker.settings", fromlist=["Settings"]).Settings.load()
    if settings.environment == "production" and request.url.path.startswith("/api") and request.url.path != "/api/health":
        expected = os.getenv("CHAINBREAKER_API_TOKEN")
        presented = request.headers.get("authorization", "")
        if not expected or not hmac.compare_digest(presented, f"Bearer {expected}"):
            response = JSONResponse({"detail": "authentication required"}, status_code=401)
            observe_request(request.method, request.url.path, 401, __import__("time").perf_counter() - started)
            return response
    response = await call_next(request)
    observe_request(request.method, request.url.path, response.status_code, __import__("time").perf_counter() - started)
    return response
