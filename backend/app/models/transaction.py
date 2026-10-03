from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Float, Integer, DateTime, JSON
from datetime import datetime, UTC
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, ForeignKey, DateTime, JSON
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
    merchant_id: Mapped[str] = mapped_column(ForeignKey("merchants.id"), unique=True)
    
    profile_version: Mapped[int] = mapped_column(Integer, default=1)
    observation_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    observation_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    transaction_count: Mapped[int] = mapped_column(Integer, default=0)
    transaction_volume: Mapped[float] = mapped_column(Float, default=0.0)
    
    unique_customer_count: Mapped[int] = mapped_column(Integer, default=0)
    
    average_transaction_amount: Mapped[float] = mapped_column(Float, default=0.0)
    median_transaction_amount: Mapped[float] = mapped_column(Float, default=0.0)
    largest_transaction_amount: Mapped[float] = mapped_column(Float, default=0.0)
    
    successful_transaction_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_transaction_count: Mapped[int] = mapped_column(Integer, default=0)
    reversal_count: Mapped[int] = mapped_column(Integer, default=0)
    refund_count: Mapped[int] = mapped_column(Integer, default=0)
    
    customer_concentration: Mapped[float] = mapped_column(Float, default=0.0)
    data_sufficiency: Mapped[str] = mapped_column(String, default="INSUFFICIENT_DATA")
    last_calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

class Agent(Base, TimestampMixin):
    __tablename__ = "agents"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    identifier: Mapped[str] = mapped_column(String, index=True)

class AgentProfile(Base, TimestampMixin):
    __tablename__ = "agent_profiles"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    agent_id: Mapped[str] = mapped_column(ForeignKey("agents.id"), unique=True)
    
    profile_version: Mapped[int] = mapped_column(Integer, default=1)
    observation_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    observation_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    transaction_count: Mapped[int] = mapped_column(Integer, default=0)
    transaction_volume: Mapped[float] = mapped_column(Float, default=0.0)
    
    unique_customer_count: Mapped[int] = mapped_column(Integer, default=0)
    
    average_transaction_amount: Mapped[float] = mapped_column(Float, default=0.0)
    median_transaction_amount: Mapped[float] = mapped_column(Float, default=0.0)
    largest_transaction_amount: Mapped[float] = mapped_column(Float, default=0.0)
    
    successful_transaction_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_transaction_count: Mapped[int] = mapped_column(Integer, default=0)
    reversal_count: Mapped[int] = mapped_column(Integer, default=0)
    
    customer_concentration: Mapped[float] = mapped_column(Float, default=0.0)
    location_consistency: Mapped[float] = mapped_column(Float, default=0.0)
    data_sufficiency: Mapped[str] = mapped_column(String, default="INSUFFICIENT_DATA")
    last_calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

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
    external_transaction_id: Mapped[str] = mapped_column(String, index=True, nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=True)
    correlation_id: Mapped[str] = mapped_column(String, index=True, nullable=True)
    
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, index=True)
    transaction_type: Mapped[str] = mapped_column(String, index=True)
    channel: Mapped[str] = mapped_column(String, nullable=True)
    
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
    
    schema_version: Mapped[int] = mapped_column(default=1)
    correlation_id: Mapped[str] = mapped_column(String, index=True, nullable=True)
    causation_id: Mapped[str] = mapped_column(String, index=True, nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    transaction: Mapped["Transaction"] = relationship(back_populates="events")
