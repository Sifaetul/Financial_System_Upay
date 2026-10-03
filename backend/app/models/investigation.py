from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Float, Integer, DateTime, JSON, Boolean
from datetime import datetime, UTC
from typing import List

from .base import Base, TimestampMixin, generate_uuid

class AlertCorrelationGroup(Base, TimestampMixin):
    __tablename__ = "alert_correlation_groups"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    group_key: Mapped[str] = mapped_column(String, index=True, unique=True)
    primary_entity_type: Mapped[str] = mapped_column(String)
    primary_entity_id: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String, default="OPEN") # OPEN, CLOSED
    correlation_reason: Mapped[str] = mapped_column(String, nullable=True)
    
    alerts: Mapped[List["Alert"]] = relationship(back_populates="correlation_group")
    case_id: Mapped[str] = mapped_column(ForeignKey("investigation_cases.id"), nullable=True)
    case: Mapped["InvestigationCase"] = relationship(back_populates="correlation_groups")

class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    
    alert_type: Mapped[str] = mapped_column(String, index=True) # e.g. FRAUD_RISK
    severity: Mapped[str] = mapped_column(String) # LOW, MEDIUM, HIGH, CRITICAL
    priority: Mapped[int] = mapped_column(Integer, default=0)
    
    entity_type: Mapped[str] = mapped_column(String, index=True) # CUSTOMER, TRANSACTION
    entity_id: Mapped[str] = mapped_column(String, index=True)
    
    status: Mapped[str] = mapped_column(String, default="NEW") # NEW, ACKNOWLEDGED, IN_REVIEW, ESCALATED, RESOLVED, DISMISSED, CLOSED
    
    deduplication_key: Mapped[str] = mapped_column(String, index=True, unique=True)
    risk_score: Mapped[float] = mapped_column(Float, nullable=True)
    trigger_reason: Mapped[str] = mapped_column(String, nullable=True)
    
    correlation_group_id: Mapped[str] = mapped_column(ForeignKey("alert_correlation_groups.id"), nullable=True)
    correlation_group: Mapped["AlertCorrelationGroup"] = relationship(back_populates="alerts")
    
    case_id: Mapped[str] = mapped_column(ForeignKey("investigation_cases.id"), nullable=True)
    case: Mapped["InvestigationCase"] = relationship(back_populates="alerts")
    
    history: Mapped[List["AlertHistory"]] = relationship(back_populates="alert")

class AlertHistory(Base, TimestampMixin):
    __tablename__ = "alert_history"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    alert_id: Mapped[str] = mapped_column(ForeignKey("alerts.id"))
    
    previous_status: Mapped[str] = mapped_column(String, nullable=True)
    new_status: Mapped[str] = mapped_column(String)
    changed_by: Mapped[str] = mapped_column(String, nullable=True) # user ID
    reason: Mapped[str] = mapped_column(String, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    alert: Mapped["Alert"] = relationship(back_populates="history")

class InvestigationCase(Base, TimestampMixin):
    __tablename__ = "investigation_cases"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    case_number: Mapped[str] = mapped_column(String, unique=True, index=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String, nullable=True)
    
    status: Mapped[str] = mapped_column(String, default="OPEN") # OPEN, IN_REVIEW, ESCALATED, RESOLVED, CLOSED
    priority: Mapped[int] = mapped_column(Integer, default=0)
    severity: Mapped[str] = mapped_column(String, default="MEDIUM")
    
    primary_entity_type: Mapped[str] = mapped_column(String, index=True)
    primary_entity_id: Mapped[str] = mapped_column(String, index=True)
    
    assigned_investigator_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    resolution_type: Mapped[str] = mapped_column(String, nullable=True)
    resolution_reason: Mapped[str] = mapped_column(String, nullable=True)
    
    alerts: Mapped[List["Alert"]] = relationship(back_populates="case")
    correlation_groups: Mapped[List["AlertCorrelationGroup"]] = relationship(back_populates="case")
    evidence: Mapped[List["CaseEvidence"]] = relationship(back_populates="case")
    notes: Mapped[List["CaseNote"]] = relationship(back_populates="case")
    actions: Mapped[List["CaseAction"]] = relationship(back_populates="case")

class CaseEvidence(Base, TimestampMixin):
    __tablename__ = "case_evidence"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(ForeignKey("investigation_cases.id"))
    
    evidence_type: Mapped[str] = mapped_column(String) # TRANSACTION, RISK_SIGNAL, PROFILE
    source_entity_type: Mapped[str] = mapped_column(String)
    source_entity_id: Mapped[str] = mapped_column(String)
    
    relevance: Mapped[str] = mapped_column(String, nullable=True)
    explanation: Mapped[str] = mapped_column(String, nullable=True)
    
    case: Mapped["InvestigationCase"] = relationship(back_populates="evidence")

class CaseNote(Base, TimestampMixin):
    __tablename__ = "case_notes"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(ForeignKey("investigation_cases.id"))
    author_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    
    content: Mapped[str] = mapped_column(String)
    
    case: Mapped["InvestigationCase"] = relationship(back_populates="notes")

class CaseAction(Base, TimestampMixin):
    __tablename__ = "case_actions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(ForeignKey("investigation_cases.id"))
    author_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    
    action_type: Mapped[str] = mapped_column(String) # REVIEW_TRANSACTION, ESCALATE_CASE, RESOLVE_CASE
    details: Mapped[str] = mapped_column(String, nullable=True)
    
    case: Mapped["InvestigationCase"] = relationship(back_populates="actions")
