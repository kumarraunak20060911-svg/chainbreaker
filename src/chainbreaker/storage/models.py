from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

JsonType = JSON().with_variant(JSONB, "postgresql")


class Base(DeclarativeBase):
    pass


def new_id() -> str:
    return str(uuid4())


class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    configuration: Mapped[dict[str, Any]] = mapped_column(JsonType, default=dict, nullable=False)
    retention_policy: Mapped[dict[str, Any]] = mapped_column(JsonType, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    users: Mapped[list["User"]] = relationship(back_populates="organization")


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=new_id)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    auth_identity: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(64), nullable=False, default="analyst")
    permissions: Mapped[list[str]] = mapped_column(JsonType, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    organization: Mapped[Organization] = relationship(back_populates="users")
    __table_args__ = (UniqueConstraint("organization_id", "auth_identity", name="uq_user_org_identity"),)


class DataSource(Base):
    __tablename__ = "data_sources"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=new_id)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    configuration: Mapped[dict[str, Any]] = mapped_column(JsonType, default=dict, nullable=False)
    health_status: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    last_successful_ingestion_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    __table_args__ = (Index("ix_data_sources_org_type", "organization_id", "source_type"),)


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=new_id)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    data_source_id: Mapped[str | None] = mapped_column(ForeignKey("data_sources.id", ondelete="SET NULL"))
    input_dataset_reference: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    processed_events: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    accepted_events: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rejected_events: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duplicate_events: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    progress: Mapped[float] = mapped_column(default=0.0, nullable=False)
    error_summary: Mapped[dict[str, Any]] = mapped_column(JsonType, default=dict, nullable=False)
    worker_lease_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (Index("ix_jobs_org_status_created", "organization_id", "status", "created_at"),)


class SecurityEvent(Base):
    __tablename__ = "security_events"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    source_id: Mapped[str | None] = mapped_column(ForeignKey("data_sources.id", ondelete="SET NULL"))
    ingestion_job_id: Mapped[str | None] = mapped_column(ForeignKey("ingestion_jobs.id", ondelete="SET NULL"))
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    account_ref: Mapped[str | None] = mapped_column(String(128), index=True)
    host_ref: Mapped[str | None] = mapped_column(String(128), index=True)
    ip_ref: Mapped[str | None] = mapped_column(String(128), index=True)
    device_ref: Mapped[str | None] = mapped_column(String(128), index=True)
    source_native_id: Mapped[str | None] = mapped_column(String(255))
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(32), nullable=False, default="1")
    attributes: Mapped[dict[str, Any]] = mapped_column(JsonType, default=dict, nullable=False)
    provenance: Mapped[dict[str, Any]] = mapped_column(JsonType, default=dict, nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    __table_args__ = (
        UniqueConstraint("organization_id", "fingerprint", name="uq_event_org_fingerprint"),
        Index("ix_events_org_timestamp", "organization_id", "event_timestamp"),
        Index("ix_events_org_source_timestamp", "organization_id", "source_id", "event_timestamp"),
        Index("ix_events_org_job", "organization_id", "ingestion_job_id"),
    )


class DetectionFinding(Base):
    __tablename__ = "detection_findings"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=new_id)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    detection_type: Mapped[str] = mapped_column(String(128), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    event_ids: Mapped[list[str]] = mapped_column(JsonType, default=list, nullable=False)
    evidence_details: Mapped[dict[str, Any]] = mapped_column(JsonType, default=dict, nullable=False)
    detector_version: Mapped[str] = mapped_column(String(64), nullable=False, default="1")
    confidence: Mapped[float | None] = mapped_column()
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    __table_args__ = (Index("ix_findings_org_severity_created", "organization_id", "severity", "created_at"),)


class InvestigationCase(Base):
    __tablename__ = "investigation_cases"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=new_id)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
    priority: Mapped[str] = mapped_column(String(32), nullable=False, default="medium")
    analyst_notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    disposition: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    __table_args__ = (Index("ix_cases_org_status_updated", "organization_id", "status", "updated_at"),)


class CaseFinding(Base):
    __tablename__ = "case_findings"
    case_id: Mapped[str] = mapped_column(ForeignKey("investigation_cases.id", ondelete="CASCADE"), primary_key=True)
    finding_id: Mapped[str] = mapped_column(ForeignKey("detection_findings.id", ondelete="CASCADE"), primary_key=True)


class GraphNode(Base):
    __tablename__ = "graph_nodes"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    case_id: Mapped[str | None] = mapped_column(ForeignKey("investigation_cases.id", ondelete="CASCADE"))
    node_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_ref: Mapped[str] = mapped_column(String(128), nullable=False)
    attributes: Mapped[dict[str, Any]] = mapped_column(JsonType, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    __table_args__ = (Index("ix_graph_nodes_org_case_type", "organization_id", "case_id", "node_type"),)


class GraphEdge(Base):
    __tablename__ = "graph_edges"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    case_id: Mapped[str | None] = mapped_column(ForeignKey("investigation_cases.id", ondelete="CASCADE"))
    source_node_id: Mapped[str] = mapped_column(ForeignKey("graph_nodes.id", ondelete="CASCADE"), nullable=False)
    destination_node_id: Mapped[str] = mapped_column(ForeignKey("graph_nodes.id", ondelete="CASCADE"), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(64), nullable=False)
    score: Mapped[float] = mapped_column(nullable=False)
    score_components: Mapped[dict[str, Any]] = mapped_column(JsonType, default=dict, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    assumptions: Mapped[list[str]] = mapped_column(JsonType, default=list, nullable=False)
    limitations: Mapped[list[str]] = mapped_column(JsonType, default=list, nullable=False)
    algorithm_version: Mapped[str] = mapped_column(String(64), nullable=False, default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    __table_args__ = (Index("ix_graph_edges_org_case_score", "organization_id", "case_id", "score"),)


class GraphEdgeEvent(Base):
    __tablename__ = "graph_edge_events"
    edge_id: Mapped[str] = mapped_column(ForeignKey("graph_edges.id", ondelete="CASCADE"), primary_key=True)
    event_id: Mapped[str] = mapped_column(ForeignKey("security_events.id", ondelete="CASCADE"), primary_key=True)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=new_id)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(128))
    outcome: Mapped[str] = mapped_column(String(32), nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JsonType, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    __table_args__ = (Index("ix_audit_org_created", "organization_id", "created_at"),)


class InvestigationReport(Base):
    __tablename__ = "investigation_reports"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JsonType, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    __table_args__ = (Index("ix_reports_org_created", "organization_id", "created_at"),)
