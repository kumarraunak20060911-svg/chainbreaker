from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, time, timezone
from pathlib import Path
from time import perf_counter
from uuid import uuid4

import networkx as nx
from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from chainbreaker.containment.service import plan_actions
from chainbreaker.correlation.aliases import alias_correction_rows
from chainbreaker.correlation.clustering import cluster_incidents
from chainbreaker.correlation.service import build_links, calibration_report_for
from chainbreaker.detection.iot import build_profile
from chainbreaker.detection.service import detect_all
from chainbreaker.domain.enums import Criticality
from chainbreaker.domain.models import Asset
from chainbreaker.ingest.merkle import MerkleTree
from chainbreaker.ingest.inventory import assets_from_rows, profiles_from_inventory
from chainbreaker.ingest.service import ingest_rows_diagnostics, read_rows
from chainbreaker.inference.service import infer_chains
from chainbreaker.reporting.summary import build_llm_summary_prompt, build_local_executive_summary, incident_summary
from chainbreaker.reporting.case_report import build_case_report
from chainbreaker.scenarios.generator import central_district_rows
from chainbreaker.storage.database import initialize
from chainbreaker.storage.repositories import save_run
from chainbreaker.settings import Settings
DEFAULT_ORGANIZATION_ID = "dev-organization"
from chainbreaker.evaluation.metrics import adjusted_rand_index, correct_chain_rate, events_per_second, time_to_detect
from .graph_svg import evidence_graph_svg
from .timeline_svg import timeline_svg


router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
RUNS: dict[str, dict] = {}


def _asset() -> Asset:
    return Asset("TC-14", "Traffic controller TC-14", "signal-controller", Criticality.LIFE_SAFETY, ("signal-phase", "emergency-preemption"), "Central District")


def _analysis_graph(events, links, target_asset_id: str) -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.add_node("operator")
    for event in events:
        graph.add_node(event.event_id)
    for link in links:
        graph.add_edge(link.left_event_id, link.right_event_id, capacity=max(link.weight, 0.1))
    ordered = sorted(events, key=lambda item: item.timestamp)
    if ordered:
        graph.add_edge("operator", ordered[0].event_id, capacity=1e12)
    target_events = [event.event_id for event in events if event.device_id == target_asset_id or event.host == target_asset_id]
    if target_events:
        for event_id in target_events:
            graph.add_edge(event_id, target_asset_id, capacity=1e12)
    else:
        graph.add_edge(ordered[-1].event_id if ordered else "operator", target_asset_id, capacity=1e12)
    return graph


def process_rows(rows, *, expected_attack_ids: set[str] | None = None, expected_stages: tuple[str, ...] = (), expected_cluster_labels: dict[str, str] | None = None, asset_rows=None, inventory_rows=None, organization_id: str = DEFAULT_ORGANIZATION_ID, ingestion_job_id: str | None = None, settings: Settings | None = None, persist: bool = True) -> dict:
    started_at = datetime.now(timezone.utc)
    tick = perf_counter()
    events, ingest_diagnostics = ingest_rows_diagnostics(rows)
    settings = settings or Settings.load()
    job_id = ingestion_job_id
    update_job = None
    save_report = None
    try:
        from chainbreaker.storage.persistent import ensure_organization, create_job, persist_events, persist_findings, persist_graph, update_job, save_report
        if persist:
            ensure_organization(organization_id, settings=settings)
            job_id = ingestion_job_id or create_job(organization_id, "inline-analysis", settings=settings)
            if ingestion_job_id is None:
                from chainbreaker.storage.persistent import claim_job
                claim_job(job_id, organization_id, settings=settings)
            accepted, duplicates = persist_events(events, organization_id, job_id, settings=settings)
            update_job(job_id, organization_id, processed=len(events), accepted=accepted, rejected=len(ingest_diagnostics.rejected_rows), duplicates=duplicates, progress=0.2, settings=settings)
    except Exception:
        if settings.environment != "test":
            raise
        job_id = ingestion_job_id
    profiles = profiles_from_inventory(events, inventory_rows or []) if inventory_rows else {}
    device_events = [event for event in events if event.device_class]
    for device_class in {event.device_class for event in device_events}:
        if not device_class:
            continue
        baseline = [event for event in device_events if event.device_class == device_class and event.command != "set-phase"]
        if baseline:
            profiles[device_class] = build_profile(device_class or "unknown", baseline, maintenance_windows=((time(2, 0), time(2, 5)),))
    findings = detect_all(events, profiles)
    links = build_links(events)
    try:
        from chainbreaker.storage.persistent import persist_findings, persist_graph
        if persist:
            persist_findings(findings, organization_id, settings=settings)
            persist_graph(events, links, organization_id, settings=settings)
    except Exception:
        if settings.environment != "test":
            raise
    chains = infer_chains(events, links)
    incidents = cluster_incidents(events, findings, links)
    tree = MerkleTree([asdict(event) for event in events])
    run_id = f"run-{uuid4().hex[:10]}"
    summary = incident_summary(events, findings, chains, incidents)
    calibration = calibration_report_for(events)
    assets = assets_from_rows(asset_rows or []) if asset_rows else {}
    asset = assets.get("TC-14") or next((candidate for candidate in assets.values() if candidate.criticality is Criticality.LIFE_SAFETY), None) or _asset()
    graph = _analysis_graph(events, links, asset.asset_id)
    containment = plan_actions(asset, primary_severance=min(0.95, 0.62 + 0.04 * len(chains)), graph=graph, source_nodes=("operator",), target_nodes=(asset.asset_id,))
    expected_attack_ids = expected_attack_ids or set()
    predicted_by_event = {}
    for index, incident in enumerate(incidents):
        for event_id in incident["event_ids"]:
            predicted_by_event[event_id] = f"incident-{index}"
    expected_labels = [expected_cluster_labels.get(event.event_id, "unknown") for event in events] if expected_cluster_labels else (["attack" if event.event_id in expected_attack_ids else "benign" for event in events] if expected_attack_ids else ["unknown"] * len(events))
    predicted_labels = [predicted_by_event.get(event.event_id, "unlinked") for event in events]
    finished_at = datetime.now(timezone.utc)
    metrics = {
        "incident_ari": round(adjusted_rand_index(expected_labels, predicted_labels), 4) if expected_attack_ids else 0.0,
        "correct_chain_rate": correct_chain_rate(chains, expected_stages),
        "time_to_detect_seconds": time_to_detect(events, findings, expected_attack_ids) if expected_attack_ids else None,
        "events_per_second": round(events_per_second(len(events), started_at, finished_at), 3),
        "processing_seconds": round(perf_counter() - tick, 6),
    }
    row_proofs = [tree.proof(index) for index in range(len(events))]
    corrections = alias_correction_rows(events)
    citations = tuple(chain.justification.row_ids for chain in chains[:1])
    executive_summary = build_local_executive_summary(summary, findings, chains[0] if chains else None, citations[0] if citations else ())
    llm_prompt = build_llm_summary_prompt(summary, findings, chains[0] if chains else None, citations[0] if citations else ())
    report = build_case_report(run_id, summary, chains[0] if chains else None, findings, links, tree.root, calibration=calibration, containment=containment, row_proofs=row_proofs, diagnostics=ingest_diagnostics, incidents=incidents, metrics=metrics, corrections=corrections, executive_summary=executive_summary, llm_prompt=llm_prompt)
    report_path = settings.report_directory / f"{run_id}.json"
    if settings.environment != "production":
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, default=str))
    record = {
        "run_id": run_id,
        "events": events,
        "findings": findings,
        "links": links,
        "chains": chains,
        "tree": tree,
        "summary": summary,
        "calibration": calibration,
        "containment": containment,
        "report": report,
        "report_path": report_path,
        "incidents": incidents,
        "diagnostics": ingest_diagnostics,
        "metrics": metrics,
        "graph": graph,
        "asset": asset,
        "corrections": corrections,
        "decisions": [],
    }
    RUNS[run_id] = record
    try:
        if job_id and update_job and save_report:
            update_job(job_id, organization_id, status="SUCCEEDED", processed=len(events), accepted=len(events) - len(ingest_diagnostics.rejected_rows), rejected=len(ingest_diagnostics.rejected_rows), progress=1.0, settings=settings)
        if save_report:
            save_report(run_id, organization_id, report, settings=settings)
    except Exception:
        if settings.environment != "test":
            raise
    if persist and settings.environment != "production":
        database_path = Path("runtime/databases/chainbreaker.sqlite3")
        initialize(database_path)
        save_run(database_path, run_id, report["generated_at"], events, findings, tree.root, incident_count=len(incidents), links=links, report=report)
    return record


def demo_run() -> dict:
    rows = central_district_rows()
    return process_rows(rows, expected_attack_ids={"evt-004", "evt-005", "evt-006", "evt-007"}, expected_stages=("initial-access", "lateral-movement", "impact"), expected_cluster_labels={str(row["event_id"]): "central-incident" for row in rows})


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
async def upload_dataset(request: Request, file: UploadFile = File(...), assets_file: UploadFile | None = File(None), inventory_file: UploadFile | None = File(None)):
    settings = Settings.load()
    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        return HTMLResponse("Upload exceeds the configured size limit.", status_code=413)
    temp = settings.upload_directory / f"{uuid4().hex}-{Path(file.filename or 'upload.csv').name}"
    temp.parent.mkdir(parents=True, exist_ok=True)
    temp.write_bytes(content)
    asset_path = inventory_path = None
    for uploaded, label in ((assets_file, "assets"), (inventory_file, "inventory")):
        if uploaded and uploaded.filename:
            supplemental = settings.upload_directory / f"{uuid4().hex}-{label}-{Path(uploaded.filename).name}"
            supplemental.write_bytes(await uploaded.read())
            if label == "assets":
                asset_path = str(supplemental)
            else:
                inventory_path = str(supplemental)
    from chainbreaker.storage.persistent import create_job, ensure_organization
    from chainbreaker.ingest.jobs import submit_job
    ensure_organization(DEFAULT_ORGANIZATION_ID, settings=settings)
    job_id = create_job(DEFAULT_ORGANIZATION_ID, json.dumps({"events": str(temp), "assets": asset_path, "inventory": inventory_path}), settings=settings)
    submit_job(job_id, DEFAULT_ORGANIZATION_ID, json.dumps({"events": str(temp), "assets": asset_path, "inventory": inventory_path}), settings=settings)
    return RedirectResponse(f"/jobs/{job_id}", status_code=303)


@router.get("/runs/{run_id}", response_class=HTMLResponse)
async def run_page(request: Request, run_id: str):
    run = RUNS.get(run_id) or latest()
    return templates.TemplateResponse(request=request, name="incident.html", context={"run": run, "graph": evidence_graph_svg(run["events"], run["links"]), "timeline": timeline_svg(run["events"])})


@router.get("/jobs/{job_id}", response_class=HTMLResponse)
async def job_page(request: Request, job_id: str):
    from chainbreaker.storage.persistent import get_job
    job = get_job(job_id, DEFAULT_ORGANIZATION_ID, settings=Settings.load())
    if job is None:
        return templates.TemplateResponse(request=request, name="job.html", context={"job": None}, status_code=404)
    return templates.TemplateResponse(request=request, name="job.html", context={"job": job})


@router.get("/runs/{run_id}/containment", response_class=HTMLResponse)
async def containment_page(request: Request, run_id: str):
    run = RUNS.get(run_id) or latest()
    plan = run["containment"]
    return templates.TemplateResponse(request=request, name="containment.html", context={"run": run, "plan": plan})


@router.get("/runs/{run_id}/evidence", response_class=HTMLResponse)
async def evidence_page(request: Request, run_id: str):
    run = RUNS.get(run_id) or latest()
    return templates.TemplateResponse(request=request, name="evidence.html", context={"run": run, "graph": evidence_graph_svg(run["events"], run["links"])})


@router.get("/runs/{run_id}/report", response_class=HTMLResponse)
async def report_page(request: Request, run_id: str):
    run = RUNS.get(run_id) or latest()
    return templates.TemplateResponse(request=request, name="report.html", context={"run": run, "root": run["tree"].root})


@router.get("/runs/{run_id}/replay", response_class=HTMLResponse)
async def replay_page(request: Request, run_id: str):
    run = RUNS.get(run_id) or latest()
    return templates.TemplateResponse(request=request, name="replay.html", context={"run": run, "replays": run["containment"].replays or {}})


@router.get("/metrics", response_class=HTMLResponse)
async def metrics_page(request: Request):
    run = latest()
    return templates.TemplateResponse(request=request, name="metrics.html", context={"run": run, "metrics": run["metrics"]})
