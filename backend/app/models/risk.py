from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, ForeignKey, JSON, Text
from .base import Base, TimestampMixin, generate_uuid
from typing import List

class RiskEvaluation(Base, TimestampMixin):
    __tablename__ = "risk_evaluations"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    transaction_id: Mapped[str] = mapped_column(ForeignKey("transactions.id"), index=True, nullable=True)
    event_id: Mapped[str] = mapped_column(String, nullable=True)
    
    score: Mapped[float] = mapped_column(Float)
    category: Mapped[str] = mapped_column(String)
    decision: Mapped[str] = mapped_column(String)
    
    policy_version: Mapped[str] = mapped_column(String)
    engine_version: Mapped[str] = mapped_column(String)
    
    confidence_summary: Mapped[float] = mapped_column(Float, default=1.0)
    explanation: Mapped[str] = mapped_column(Text)
    
    correlation_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    causation_id: Mapped[str] = mapped_column(String, nullable=True)
    
    signals: Mapped[List["RiskEvaluationSignal"]] = relationship(back_populates="evaluation", cascade="all, delete-orphan")

class RiskEvaluationSignal(Base, TimestampMixin):
    __tablename__ = "risk_evaluation_signals"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("risk_evaluations.id"))
    
    signal_id: Mapped[str] = mapped_column(String)
    signal_type: Mapped[str] = mapped_column(String)
    source: Mapped[str] = mapped_column(String)
    
    raw_value: Mapped[str] = mapped_column(String, nullable=True) # string representation
    normalized_value: Mapped[float] = mapped_column(Float)
    weight: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    reliability: Mapped[float] = mapped_column(Float)
    contribution: Mapped[float] = mapped_column(Float)
    
    explanation: Mapped[str] = mapped_column(Text)
    provenance: Mapped[dict] = mapped_column(JSON)
    
    evaluation: Mapped["RiskEvaluation"] = relationship(back_populates="signals")
