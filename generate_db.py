import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content.strip() + "\n")

# Database core
write_file("backend/app/core/database.py", """
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""")

# Base model
write_file("backend/app/models/base.py", """
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime
from datetime import datetime, UTC
import uuid

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

def generate_uuid():
    return str(uuid.uuid4())
""")

# Identity
write_file("backend/app/models/identity.py", """
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, JSON, ForeignKey, Table, Column
from .base import Base, TimestampMixin, generate_uuid
from typing import List

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", String, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", String, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
)

class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(default=True)
    
    roles: Mapped[List["Role"]] = relationship(secondary=user_roles)

class Role(Base, TimestampMixin):
    __tablename__ = "roles"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String, unique=True)
    permissions: Mapped[dict] = mapped_column(JSON, default=dict)
""")

# Customer
write_file("backend/app/models/customer.py", """
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Float
from .base import Base, TimestampMixin, generate_uuid
from typing import List

class Customer(Base, TimestampMixin):
    __tablename__ = "customers"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    identifier: Mapped[str] = mapped_column(String, unique=True, index=True) # Masked/safe ID
    status: Mapped[str] = mapped_column(String, default="active")
    
    accounts: Mapped[List["Account"]] = relationship(back_populates="customer")
    profiles: Mapped[List["CustomerProfile"]] = relationship(back_populates="customer")
    segments: Mapped[List["CustomerSegment"]] = relationship(back_populates="customer")
    financial_profiles: Mapped[List["FinancialProfile"]] = relationship(back_populates="customer")

class CustomerProfile(Base, TimestampMixin):
    __tablename__ = "customer_profiles"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"))
    customer: Mapped["Customer"] = relationship(back_populates="profiles")

class CustomerSegment(Base, TimestampMixin):
    __tablename__ = "customer_segments"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"))
    segment_name: Mapped[str] = mapped_column(String, index=True)
    customer: Mapped["Customer"] = relationship(back_populates="segments")

class Account(Base, TimestampMixin):
    __tablename__ = "accounts"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"))
    account_number_hash: Mapped[str] = mapped_column(String, unique=True, index=True)
    balance: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String, default="USD")
    status: Mapped[str] = mapped_column(String, default="active")
    
    customer: Mapped["Customer"] = relationship(back_populates="accounts")

class FinancialProfile(Base, TimestampMixin):
    __tablename__ = "financial_profiles"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"))
    risk_rating: Mapped[str] = mapped_column(String)
    customer: Mapped["Customer"] = relationship(back_populates="financial_profiles")
""")

# Transaction
write_file("backend/app/models/transaction.py", """
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, ForeignKey, DateTime
from .base import Base, TimestampMixin, generate_uuid
from datetime import datetime
from typing import List

class Merchant(Base, TimestampMixin):
    __tablename__ = "merchants"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String)

class MerchantProfile(Base, TimestampMixin):
    __tablename__ = "merchant_profiles"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    merchant_id: Mapped[str] = mapped_column(ForeignKey("merchants.id"))

class Agent(Base, TimestampMixin):
    __tablename__ = "agents"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    identifier: Mapped[str] = mapped_column(String, index=True)

class AgentProfile(Base, TimestampMixin):
    __tablename__ = "agent_profiles"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    agent_id: Mapped[str] = mapped_column(ForeignKey("agents.id"))

class Device(Base, TimestampMixin):
    __tablename__ = "devices"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    device_hash: Mapped[str] = mapped_column(String, index=True, unique=True)
    platform: Mapped[str] = mapped_column(String, nullable=True)

class Location(Base, TimestampMixin):
    __tablename__ = "locations"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    country: Mapped[str] = mapped_column(String, nullable=True)
    city: Mapped[str] = mapped_column(String, nullable=True)

class Beneficiary(Base, TimestampMixin):
    __tablename__ = "beneficiaries"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    identifier: Mapped[str] = mapped_column(String, index=True)

class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, index=True)
    transaction_type: Mapped[str] = mapped_column(String, index=True)
    
    sender_account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"))
    receiver_account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    
    merchant_id: Mapped[str] = mapped_column(ForeignKey("merchants.id"), nullable=True)
    agent_id: Mapped[str] = mapped_column(ForeignKey("agents.id"), nullable=True)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"), nullable=True)
    location_id: Mapped[str] = mapped_column(ForeignKey("locations.id"), nullable=True)
    beneficiary_id: Mapped[str] = mapped_column(ForeignKey("beneficiaries.id"), nullable=True)

    events: Mapped[List["TransactionEvent"]] = relationship(back_populates="transaction")

class TransactionEvent(Base, TimestampMixin):
    __tablename__ = "transaction_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    transaction_id: Mapped[str] = mapped_column(ForeignKey("transactions.id"))
    event_type: Mapped[str] = mapped_column(String)
    
    transaction: Mapped["Transaction"] = relationship(back_populates="events")
""")

# Intelligence
write_file("backend/app/models/intelligence.py", """
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, ForeignKey, JSON
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

class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    transaction_id: Mapped[str] = mapped_column(ForeignKey("transactions.id"), index=True)
    severity: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String, default="open", index=True)

    cases: Mapped[List["Case"]] = relationship(back_populates="alert")

class Case(Base, TimestampMixin):
    __tablename__ = "cases"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    alert_id: Mapped[str] = mapped_column(ForeignKey("alerts.id"))
    status: Mapped[str] = mapped_column(String, default="open", index=True)
    investigator_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=True)

    alert: Mapped["Alert"] = relationship(back_populates="cases")
    events: Mapped[List["CaseEvent"]] = relationship(back_populates="case_entity")

class CaseEvent(Base, TimestampMixin):
    __tablename__ = "case_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id"))
    action: Mapped[str] = mapped_column(String)
    
    case_entity: Mapped["Case"] = relationship(back_populates="events")

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

class GraphEdge(Base, TimestampMixin):
    __tablename__ = "graph_edges"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    source_node_id: Mapped[str] = mapped_column(ForeignKey("graph_nodes.id"))
    target_node_id: Mapped[str] = mapped_column(ForeignKey("graph_nodes.id"))
    relationship_type: Mapped[str] = mapped_column(String, index=True)

class Forecast(Base, TimestampMixin):
    __tablename__ = "forecasts"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    entity_id: Mapped[str] = mapped_column(String, index=True)
    data: Mapped[dict] = mapped_column(JSON)
""")

# AI
write_file("backend/app/models/ai.py", """
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from pgvector.sqlalchemy import Vector
from .base import Base, TimestampMixin, generate_uuid
from typing import List

class AiDocument(Base, TimestampMixin):
    __tablename__ = "ai_documents"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String)
    
    chunks: Mapped[List["AiChunk"]] = relationship(back_populates="document")

class AiChunk(Base, TimestampMixin):
    __tablename__ = "ai_chunks"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    document_id: Mapped[str] = mapped_column(ForeignKey("ai_documents.id"))
    content: Mapped[str] = mapped_column(String)
    
    # 1536 is standard for OpenAI embeddings, configurable based on architecture
    embedding = mapped_column(Vector(1536))
    
    document: Mapped["AiDocument"] = relationship(back_populates="chunks")
""")

# Audit
write_file("backend/app/models/audit.py", """
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
""")

# Init exports
write_file("backend/app/models/__init__.py", """
from .base import Base
from .identity import User, Role, user_roles
from .customer import Customer, CustomerProfile, CustomerSegment, Account, FinancialProfile
from .transaction import Transaction, TransactionEvent, Merchant, MerchantProfile, Agent, AgentProfile, Device, Location, Beneficiary
from .intelligence import Rule, RuleVersion, Alert, Case, CaseEvent, RiskScore, RiskSignal, FeatureSnapshot, ModelRegistry, ModelPrediction, GraphNode, GraphEdge, Forecast
from .ai import AiDocument, AiChunk
from .audit import AuditLog, InvestigatorFeedback, SystemEvent
""")

# Core Init
write_file("backend/app/__init__.py", "")

print("Models generated.")
