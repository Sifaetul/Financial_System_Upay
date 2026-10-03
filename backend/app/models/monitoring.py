from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, JSON, Integer, DateTime
from .base import Base, TimestampMixin, generate_uuid
from datetime import datetime, UTC

class MonitoringMetric(Base, TimestampMixin):
    __tablename__ = "monitoring_metrics"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String, index=True)
    metric_type: Mapped[str] = mapped_column(String, index=True) # COUNTER, GAUGE, HISTOGRAM
    value: Mapped[float] = mapped_column(Float)
    dimensions: Mapped[dict] = mapped_column(JSON, nullable=True)
    service: Mapped[str] = mapped_column(String, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True)

class MonitoringAlert(Base, TimestampMixin):
    __tablename__ = "monitoring_alerts"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    condition: Mapped[str] = mapped_column(String)
    metric: Mapped[str] = mapped_column(String)
    observed_value: Mapped[float] = mapped_column(Float)
    threshold: Mapped[float] = mapped_column(Float)
    severity: Mapped[str] = mapped_column(String, index=True) # INFO, WARNING, HIGH, CRITICAL
    status: Mapped[str] = mapped_column(String, index=True, default="ACTIVE")
    affected_component: Mapped[str] = mapped_column(String)

class DataQualityResult(Base, TimestampMixin):
    __tablename__ = "data_quality_results"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    feature: Mapped[str] = mapped_column(String, index=True)
    completeness: Mapped[float] = mapped_column(Float, nullable=True)
    null_rate: Mapped[float] = mapped_column(Float, nullable=True)
    invalid_rate: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String) # HEALTHY, WARNING, DEGRADED, CRITICAL

class DriftResult(Base, TimestampMixin):
    __tablename__ = "drift_results"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    feature: Mapped[str] = mapped_column(String, index=True)
    baseline_window: Mapped[str] = mapped_column(String)
    comparison_window: Mapped[str] = mapped_column(String)
    method: Mapped[str] = mapped_column(String)
    metric_value: Mapped[float] = mapped_column(Float)
    threshold: Mapped[float] = mapped_column(Float)
    severity: Mapped[str] = mapped_column(String)

class GovernanceEvent(Base, TimestampMixin):
    __tablename__ = "governance_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    actor: Mapped[str] = mapped_column(String, index=True)
    entity_type: Mapped[str] = mapped_column(String)
    entity_id: Mapped[str] = mapped_column(String)
    action: Mapped[str] = mapped_column(String)
    old_value: Mapped[dict] = mapped_column(JSON, nullable=True)
    new_value: Mapped[dict] = mapped_column(JSON, nullable=True)
    reason: Mapped[str] = mapped_column(String, nullable=True)

class ModelLineage(Base, TimestampMixin):
    __tablename__ = "model_lineage"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    model_id: Mapped[str] = mapped_column(String, index=True)
    model_version: Mapped[str] = mapped_column(String)
    feature_version: Mapped[str] = mapped_column(String, nullable=True)
    policy_version: Mapped[str] = mapped_column(String, nullable=True)
    prediction: Mapped[str] = mapped_column(String)
    confidence: Mapped[float] = mapped_column(Float, nullable=True)
    correlation_id: Mapped[str] = mapped_column(String, index=True)

class ModelVersion(Base, TimestampMixin):
    __tablename__ = "model_versions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String, index=True)
    version: Mapped[str] = mapped_column(String, index=True)
    task: Mapped[str] = mapped_column(String)
    owner: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="DRAFT", index=True) # DRAFT, APPROVED, ACTIVATED, REJECTED, DEPRECATED
    activation_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    evaluation_metrics: Mapped[dict] = mapped_column(JSON, nullable=True)
