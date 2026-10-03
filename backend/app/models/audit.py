from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON
from .base import Base, TimestampMixin, generate_uuid

class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    actor_id: Mapped[str] = mapped_column(String, index=True)
    action: Mapped[str] = mapped_column(String, index=True)
    resource: Mapped[str] = mapped_column(String)
    metadata_data: Mapped[dict] = mapped_column(JSON, default=dict)

class InvestigatorFeedback(Base, TimestampMixin):
    __tablename__ = "investigator_feedback"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String, index=True)
    is_false_positive: Mapped[bool] = mapped_column()
    notes: Mapped[str] = mapped_column(String)

class SystemEvent(Base, TimestampMixin):
    __tablename__ = "system_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    event_type: Mapped[str] = mapped_column(String, index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String, default="pending", index=True)
