from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from chainbreaker.containment.service import plan_actions
from chainbreaker.correlation.service import build_links
from chainbreaker.detection.iot import build_profile
from chainbreaker.detection.service import detect_all
from chainbreaker.domain.enums import Criticality
from chainbreaker.domain.models import Asset
from chainbreaker.ingest.merkle import MerkleTree
from chainbreaker.ingest.service import ingest_file, ingest_rows
from chainbreaker.inference.service import infer_chains
from chainbreaker.reporting.summary import incident_summary
from chainbreaker.scenarios.generator import central_district_rows
from .graph_svg import evidence_graph_svg
from .timeline_svg import timeline_svg


router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
RUNS: dict[str, dict] = {}


def _asset() -> Asset:
    return Asset("TC-14", "Traffic controller TC-14", "signal-controller", Criticality.LIFE_SAFETY, ("signal-phase", "emergency-preemption"), "Central District")


def process_rows(rows) -> dict:
    events = ingest_rows(rows)
    profiles = {}
    device_events = [event for event in events if event.device_class]
    for device_class in {event.device_class for event in device_events}:
        baseline = [event for event in device_events if event.device_class == device_class and event.command != "set-phase"]
        if baseline:
            profiles[device_class] = build_profile(device_class or "unknown", baseline)
    findings = detect_all(events, profiles)
    links = build_links(events)
    chains = infer_chains(events, links)
    tree = MerkleTree([asdict(event) for event in events])
    run_id = f"run-{uuid4().hex[:10]}"
    summary = incident_summary(events, findings, chains)
    record = {"run_id": run_id, "events": events, "findings": findings, "links": links, "chains": chains, "tree": tree, "summary": summary}
    RUNS[run_id] = record
    return record


def demo_run() -> dict:
    return process_rows(central_district_rows())


def latest() -> dict:
    if RUNS:
        return next(reversed(RUNS.values()))
    return demo_run()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    run = latest()
    return templates.TemplateResponse(request=request, name="home.html", context={"run": run, "graph": evidence_graph_svg(run["events"], run["links"])})


@router.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse(request=request, name="upload.html", context={})


@router.post("/upload")
async def upload_dataset(request: Request, file: UploadFile = File(...)):
    content = await file.read()
    temp = Path("runtime/uploads") / (file.filename or "upload.csv")
    temp.parent.mkdir(parents=True, exist_ok=True)
    temp.write_bytes(content)
    run = process_rows(__import__("chainbreaker.ingest.service", fromlist=["read_rows"]).read_rows(temp))
    return RedirectResponse(f"/runs/{run['run_id']}", status_code=303)


@router.get("/runs/{run_id}", response_class=HTMLResponse)
async def run_page(request: Request, run_id: str):
    run = RUNS.get(run_id) or latest()
    return templates.TemplateResponse(request=request, name="incident.html", context={"run": run, "graph": evidence_graph_svg(run["events"], run["links"]), "timeline": timeline_svg(run["events"])})


@router.get("/runs/{run_id}/containment", response_class=HTMLResponse)
async def containment_page(request: Request, run_id: str):
    run = RUNS.get(run_id) or latest()
    plan = plan_actions(_asset())
    return templates.TemplateResponse(request=request, name="containment.html", context={"run": run, "plan": plan})


@router.get("/runs/{run_id}/report", response_class=HTMLResponse)
async def report_page(request: Request, run_id: str):
    run = RUNS.get(run_id) or latest()
    return templates.TemplateResponse(request=request, name="report.html", context={"run": run, "root": run["tree"].root})
