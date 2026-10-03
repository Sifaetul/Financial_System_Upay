from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, ForeignKey, JSON, UniqueConstraint, Integer, DateTime
from .base import Base, TimestampMixin, generate_uuid
from typing import List

class Rule(Base, TimestampMixin):
    __tablename__ = "rules"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String, unique=True)
    
    versions: Mapped[List["RuleVersion"]] = relationship(back_populates="rule")

class RuleVersion(Base, TimestampMixin):
    __tablename__ = "rule_versions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    rule_id: Mapped[str] = mapped_column(ForeignKey("rules.id"))
    version: Mapped[int] = mapped_column(default=1)
    configuration: Mapped[dict] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(default=False)
    
    rule: Mapped["Rule"] = relationship(back_populates="versions")

class RiskScore(Base, TimestampMixin):
    __tablename__ = "risk_scores"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    transaction_id: Mapped[str] = mapped_column(ForeignKey("transactions.id"), unique=True)
    final_score: Mapped[float] = mapped_column(Float)
    decision: Mapped[str] = mapped_column(String)

class RiskSignal(Base, TimestampMixin):
    __tablename__ = "risk_signals"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    risk_score_id: Mapped[str] = mapped_column(ForeignKey("risk_scores.id"))
    signal_type: Mapped[str] = mapped_column(String)
    contribution: Mapped[float] = mapped_column(Float)

class FeatureSnapshot(Base, TimestampMixin):
    __tablename__ = "feature_snapshots"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    entity_id: Mapped[str] = mapped_column(String, index=True)
    features: Mapped[dict] = mapped_column(JSON)

class ModelRegistry(Base, TimestampMixin):
    __tablename__ = "model_registry"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String, index=True)
    version: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)

class ModelPrediction(Base, TimestampMixin):
    __tablename__ = "model_predictions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    model_id: Mapped[str] = mapped_column(ForeignKey("model_registry.id"))
    entity_id: Mapped[str] = mapped_column(String, index=True)
    prediction: Mapped[float] = mapped_column(Float)


class GraphNode(Base, TimestampMixin):
    __tablename__ = "graph_nodes"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    node_type: Mapped[str] = mapped_column(String, index=True)
    entity_id: Mapped[str] = mapped_column(String, index=True)
    __table_args__ = (
        UniqueConstraint('node_type', 'entity_id', name='uix_graph_node_type_entity'),
    )


from sqlalchemy import Integer, DateTime
from datetime import datetime, UTC

class GraphEdge(Base, TimestampMixin):
    __tablename__ = "graph_edges"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    source_node_id: Mapped[str] = mapped_column(ForeignKey("graph_nodes.id"))
    target_node_id: Mapped[str] = mapped_column(ForeignKey("graph_nodes.id"))
    relationship_type: Mapped[str] = mapped_column(String, index=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    count: Mapped[int] = mapped_column(Integer, default=1)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    __table_args__ = (
        UniqueConstraint('source_node_id', 'target_node_id', 'relationship_type', name='uix_graph_edge'),
    )

class Forecast(Base, TimestampMixin):
    __tablename__ = "forecasts"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    entity_id: Mapped[str] = mapped_column(String, index=True)
    data: Mapped[dict] = mapped_column(JSON)
