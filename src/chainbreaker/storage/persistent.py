from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

from sqlalchemy import select, update

from chainbreaker.domain.models import Event
from chainbreaker.domain.ids import stable_id
from chainbreaker.settings import Settings

from .engine import initialize_schema, session_factory
from .models import AuditEvent, DetectionFinding as StoredFinding, GraphEdge, GraphEdgeEvent, GraphNode, IngestionJob, InvestigationCase, InvestigationReport, Organization, SecurityEvent


DEFAULT_ORGANIZATION_ID = "dev-organization"


def ensure_development_organization(settings: Settings | None = None) -> str:
    initialize_schema(settings)
    factory = session_factory(settings)
    with factory() as session:
        organization = session.get(Organization, DEFAULT_ORGANIZATION_ID)
        if organization is None:
            organization = Organization(id=DEFAULT_ORGANIZATION_ID, name="ChainBreaker Development", retention_policy={"days": 90})
            session.add(organization)
            session.commit()
        return organization.id


def ensure_organization(organization_id: str, *, settings: Settings | None = None) -> str:
    initialize_schema(settings)
    factory = session_factory(settings)
    with factory() as session:
        organization = session.get(Organization, organization_id)
        if organization is None:
            organization = Organization(id=organization_id, name=f"Organization {organization_id}", retention_policy={"days": 90})
            session.add(organization)
            session.commit()
        return organization.id


def create_job(organization_id: str, dataset_reference: str, *, data_source_id: str | None = None, settings: Settings | None = None) -> str:
    factory = session_factory(settings)
    with factory() as session:
        job = IngestionJob(organization_id=organization_id, data_source_id=data_source_id, input_dataset_reference=dataset_reference, status="PENDING")
        session.add(job)
        session.commit()
        return job.id


def get_job(job_id: str, organization_id: str, settings: Settings | None = None) -> IngestionJob | None:
    factory = session_factory(settings)
    with factory() as session:
        return session.scalar(select(IngestionJob).where(IngestionJob.id == job_id, IngestionJob.organization_id == organization_id))


def claim_job(job_id: str, organization_id: str, *, lease_seconds: int = 300, settings: Settings | None = None) -> bool:
    factory = session_factory(settings)
    now = datetime.now(timezone.utc)
    lease = now + timedelta(seconds=lease_seconds)
    with factory() as session:
        result = session.execute(
            update(IngestionJob)
            .where(IngestionJob.id == job_id, IngestionJob.organization_id == organization_id, IngestionJob.status.in_(["PENDING", "RETRYING"]))
            .values(status="RUNNING", started_at=now, worker_lease_until=lease)
        )
        session.commit()
        return result.rowcount == 1


def update_job(job_id: str, organization_id: str, *, status: str | None = None, processed: int | None = None, accepted: int | None = None, rejected: int | None = None, duplicates: int | None = None, progress: float | None = None, error_summary: dict[str, Any] | None = None, settings: Settings | None = None) -> None:
    values: dict[str, Any] = {}
    if status is not None:
        values["status"] = status
        if status in {"SUCCEEDED", "FAILED", "CANCELLED"}:
            values["completed_at"] = datetime.now(timezone.utc)
    for key, value in (("processed_events", processed), ("accepted_events", accepted), ("rejected_events", rejected), ("duplicate_events", duplicates), ("progress", progress), ("error_summary", error_summary)):
        if value is not None:
            values[key] = value
    if not values:
        return
    factory = session_factory(settings)
    with factory() as session:
        if status is not None:
            current = session.scalar(select(IngestionJob.status).where(IngestionJob.id == job_id, IngestionJob.organization_id == organization_id))
            allowed = {"PENDING": {"RUNNING", "CANCELLED"}, "RUNNING": {"SUCCEEDED", "FAILED", "RETRYING", "CANCELLED"}, "RETRYING": {"RUNNING", "CANCELLED"}, "SUCCEEDED": set(), "FAILED": {"RETRYING"}, "CANCELLED": set()}
            if current is None:
                return
            if status != current and status not in allowed.get(current, set()):
                raise ValueError(f"invalid ingestion job transition: {current} -> {status}")
        session.execute(update(IngestionJob).where(IngestionJob.id == job_id, IngestionJob.organization_id == organization_id).values(**values))
        session.commit()


def persist_events(events: Iterable[Event], organization_id: str, job_id: str, *, settings: Settings | None = None) -> tuple[int, int]:
    factory = session_factory(settings)
    accepted = duplicate = 0
    with factory() as session:
        for event in events:
            fingerprint = event.metadata.get("fingerprint") or event.event_id
            existing = session.scalar(select(SecurityEvent.id).where(SecurityEvent.organization_id == organization_id, SecurityEvent.fingerprint == fingerprint))
            if existing:
                duplicate += 1
                continue
            session.add(SecurityEvent(
                id=stable_id("event", organization_id, fingerprint),
                organization_id=organization_id,
                ingestion_job_id=job_id,
                event_timestamp=event.timestamp,
                event_type=event.event_type,
                account_ref=event.account,
                host_ref=event.host,
                ip_ref=event.ip,
                device_ref=event.device_id,
                source_native_id=event.row_id,
                fingerprint=fingerprint,
                attributes={"source": event.source.value, "command": event.command, "domain": event.domain, "peer": event.peer, "topic": event.topic, "session_id": event.session_id, "payload_size": event.payload_size, "success": event.success},
                provenance=event.metadata,
            ))
            accepted += 1
        session.commit()
    return accepted, duplicate


def persist_findings(findings: Iterable[Any], organization_id: str, *, settings: Settings | None = None) -> int:
    factory = session_factory(settings)
    count = 0
    with factory() as session:
        for finding in findings:
            finding_id = getattr(finding, "finding_id", None) or getattr(finding, "id", None)
            if not finding_id:
                continue
            existing = session.get(StoredFinding, finding_id)
            if existing:
                continue
            stage = getattr(getattr(finding, "stage", None), "value", None)
            session.add(StoredFinding(
                id=finding_id,
                organization_id=organization_id,
                detection_type=getattr(finding, "rule_id", getattr(finding, "detection_type", "unknown")),
                severity=getattr(finding, "severity", "unknown"),
                event_ids=[getattr(finding, "event_id")] if getattr(finding, "event_id", None) else [],
                evidence_details={"features": getattr(finding, "features", {}), "stage": stage},
                detector_version="1",
                confidence=None,
                explanation=getattr(finding, "explanation", ""),
            ))
            count += 1
        session.commit()
    return count


def persist_graph(events: Iterable[Event], links: Iterable[Any], organization_id: str, *, case_id: str | None = None, settings: Settings | None = None) -> tuple[int, int]:
    factory = session_factory(settings)
    nodes = edges = 0
    items = list(events)
    event_by_id = {event.event_id: event for event in items}
    with factory() as session:
        for event in items:
            node_id = stable_id("graph-node", organization_id, event.event_id)
            if session.get(GraphNode, node_id) is None:
                session.add(GraphNode(id=node_id, organization_id=organization_id, case_id=case_id, node_type="event", entity_ref=event.event_id, attributes={"event_type": event.event_type, "timestamp": event.timestamp.isoformat(), "source": event.source.value}))
                nodes += 1
        for link in links:
            source_id = stable_id("graph-node", organization_id, link.left_event_id)
            destination_id = stable_id("graph-node", organization_id, link.right_event_id)
            if link.left_event_id not in event_by_id or link.right_event_id not in event_by_id:
                continue
            edge_id = stable_id("graph-edge", organization_id, link.link_id)
            if session.get(GraphEdge, edge_id) is None:
                session.add(GraphEdge(id=edge_id, organization_id=organization_id, case_id=case_id, source_node_id=source_id, destination_node_id=destination_id, relationship_type=link.entity_type, score=link.probability, score_components={"weight": link.weight, "entity_probability": link.entity_probability, "time_decay": link.time_decay, "nat_penalty": link.nat_penalty_applied, "external_ip_boost": link.external_ip_boost_applied}, explanation=link.explanation, assumptions=["shared normalized entity", "bounded temporal window"], limitations=["correlation does not prove causation"], algorithm_version="weighted-link-v2"))
                for event_id in (link.left_event_id, link.right_event_id):
                    session.add(GraphEdgeEvent(edge_id=edge_id, event_id=stable_id("event", organization_id, event_by_id[event_id].metadata.get("fingerprint") or event_id)))
                edges += 1
        session.commit()
    return nodes, edges


def audit(organization_id: str, actor: str, action: str, resource_type: str, resource_id: str | None, outcome: str, metadata: dict[str, Any] | None = None, *, settings: Settings | None = None) -> None:
    factory = session_factory(settings)
    with factory() as session:
        session.add(AuditEvent(organization_id=organization_id, actor=actor, action=action, resource_type=resource_type, resource_id=resource_id, outcome=outcome, metadata_json=metadata or {}))
        session.commit()


def get_report(run_id: str, organization_id: str, *, settings: Settings | None = None) -> dict[str, Any] | None:
    factory = session_factory(settings)
    with factory() as session:
        row = session.scalar(select(InvestigationReport).where(InvestigationReport.id == run_id, InvestigationReport.organization_id == organization_id))
        return row.payload if row else None


def save_report(run_id: str, organization_id: str, payload: dict[str, Any], *, settings: Settings | None = None) -> None:
    factory = session_factory(settings)
    with factory() as session:
        session.merge(InvestigationReport(id=run_id, organization_id=organization_id, payload=payload))
        session.commit()


def list_events(organization_id: str, *, limit: int = 100, offset: int = 0, source_id: str | None = None, settings: Settings | None = None) -> list[SecurityEvent]:
    factory = session_factory(settings)
    with factory() as session:
        query = select(SecurityEvent).where(SecurityEvent.organization_id == organization_id).order_by(SecurityEvent.event_timestamp).limit(limit).offset(offset)
        if source_id:
            query = query.where(SecurityEvent.source_id == source_id)
        return list(session.scalars(query))


def list_findings(organization_id: str, *, limit: int = 100, offset: int = 0, severity: str | None = None, settings: Settings | None = None) -> list[StoredFinding]:
    factory = session_factory(settings)
    with factory() as session:
        query = select(StoredFinding).where(StoredFinding.organization_id == organization_id).order_by(StoredFinding.created_at.desc()).limit(limit).offset(offset)
        if severity:
            query = query.where(StoredFinding.severity == severity)
        return list(session.scalars(query))


def create_case(organization_id: str, title: str, description: str = "", priority: str = "medium", *, settings: Settings | None = None) -> str:
    factory = session_factory(settings)
    with factory() as session:
        case = InvestigationCase(organization_id=organization_id, title=title, description=description, priority=priority)
        session.add(case)
        session.commit()
        return case.id


def list_cases(organization_id: str, *, limit: int = 100, offset: int = 0, settings: Settings | None = None) -> list[InvestigationCase]:
    factory = session_factory(settings)
    with factory() as session:
        query = select(InvestigationCase).where(InvestigationCase.organization_id == organization_id).order_by(InvestigationCase.updated_at.desc()).limit(limit).offset(offset)
        return list(session.scalars(query))


def get_case(case_id: str, organization_id: str, *, settings: Settings | None = None) -> InvestigationCase | None:
    factory = session_factory(settings)
    with factory() as session:
        return session.scalar(select(InvestigationCase).where(InvestigationCase.id == case_id, InvestigationCase.organization_id == organization_id))


def list_jobs(organization_id: str, *, limit: int = 50, offset: int = 0, settings: Settings | None = None) -> list[IngestionJob]:
    factory = session_factory(settings)
    with factory() as session:
        query = select(IngestionJob).where(IngestionJob.organization_id == organization_id).order_by(IngestionJob.created_at.desc()).limit(limit).offset(offset)
        return list(session.scalars(query))


def recover_expired_jobs(organization_id: str, *, settings: Settings | None = None) -> int:
    factory = session_factory(settings)
    now = datetime.now(timezone.utc)
    with factory() as session:
        result = session.execute(
            update(IngestionJob)
            .where(IngestionJob.organization_id == organization_id, IngestionJob.status == "RUNNING", IngestionJob.worker_lease_until.is_not(None), IngestionJob.worker_lease_until < now)
            .values(status="RETRYING", retry_count=IngestionJob.retry_count + 1)
        )
        session.commit()
        return result.rowcount
