from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, JSON, DateTime
from .base import Base, TimestampMixin, generate_uuid
from datetime import datetime

class OutboxEvent(Base, TimestampMixin):
    __tablename__ = "outbox_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    event_type: Mapped[str] = mapped_column(String, index=True)
    schema_version: Mapped[int] = mapped_column(default=1)
    aggregate_type: Mapped[str] = mapped_column(String)
    aggregate_id: Mapped[str] = mapped_column(String, index=True)
    correlation_id: Mapped[str] = mapped_column(String, index=True, nullable=True)
    causation_id: Mapped[str] = mapped_column(String, index=True, nullable=True)
    
    payload: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String, index=True, default="PENDING") # PENDING, PUBLISHED, FAILED
    
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    next_retry_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    error_metadata: Mapped[dict] = mapped_column(JSON, nullable=True)

class ProcessedEvent(Base, TimestampMixin):
    # Idempotency for consumers
    __tablename__ = "processed_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    event_id: Mapped[str] = mapped_column(String, index=True)
    consumer_name: Mapped[str] = mapped_column(String, index=True)
    # unique constraint on event_id + consumer_name should be enforced, we'll let SQLAlchemy handle it conceptually, or add UniqueConstraint

class DeadLetterEvent(Base, TimestampMixin):
    __tablename__ = "dead_letter_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    event_id: Mapped[str] = mapped_column(String, index=True)
    event_type: Mapped[str] = mapped_column(String)
    consumer_name: Mapped[str] = mapped_column(String)
    failure_reason: Mapped[str] = mapped_column(String)
    payload: Mapped[dict] = mapped_column(JSON)
