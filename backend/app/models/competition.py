from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, Integer, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from .base import Base

class RiskEvolutionSnapshot(Base):
    __tablename__ = 'risk_evolution_snapshots'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = Column(String, index=True)
    entity_type = Column(String)  # CUSTOMER, MERCHANT, AGENT
    risk_score = Column(Float)
    snapshot_time = Column(DateTime(timezone=True), default=datetime.utcnow)
    delta_1h = Column(Float)
    delta_24h = Column(Float)
    delta_7d = Column(Float)
    snapshot_metadata = Column(JSON, default=dict)

class DecisionReplay(Base):
    __tablename__ = 'decision_replays'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_evaluation_id = Column(UUID(as_uuid=True), index=True)
    replay_time = Column(DateTime(timezone=True), default=datetime.utcnow)
    replayed_score = Column(Float)
    replayed_signals = Column(JSON, default=list)
    replayed_rules = Column(JSON, default=list)
    divergence = Column(Float) # diff between original and replayed

class SimulationRun(Base):
    __tablename__ = 'simulation_runs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    parameters = Column(JSON, default=dict)
    run_time = Column(DateTime(timezone=True), default=datetime.utcnow)
    results = Column(JSON, default=dict)
    baseline_comparison = Column(JSON, default=dict)

class ThreatSignal(Base):
    __tablename__ = 'threat_signals'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    signal_type = Column(String) # E.g., SUDDEN_ACCELERATION, FAN_IN, NETWORK_EXPANSION
    entity_id = Column(String, index=True)
    entity_type = Column(String)
    severity = Column(String) # HIGH, MEDIUM, LOW
    detected_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    context = Column(JSON, default=dict)

class IntelligenceFusionRecord(Base):
    __tablename__ = 'intelligence_fusion_records'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = Column(String, index=True)
    fusion_time = Column(DateTime(timezone=True), default=datetime.utcnow)
    aggregated_context = Column(JSON, default=dict)
    confidence_score = Column(Float)
    sources = Column(JSON, default=list)

class CompetitionFeedback(Base):
    __tablename__ = 'competition_feedback'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target_id = Column(String, index=True) # Could be alert id, simulation id
    target_type = Column(String)
    feedback_type = Column(String) # FALSE_POSITIVE, TRUE_POSITIVE, NOISE
    comments = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), index=True)
