from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Float, Integer, DateTime, JSON
from datetime import datetime, UTC


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
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), unique=True)
    profile_version: Mapped[int] = mapped_column(Integer, default=1)
    
    first_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    transaction_count: Mapped[int] = mapped_column(Integer, default=0)
    transaction_volume: Mapped[float] = mapped_column(Float, default=0.0)
    average_transaction_amount: Mapped[float] = mapped_column(Float, default=0.0)
    
    unique_beneficiary_count: Mapped[int] = mapped_column(Integer, default=0)
    unique_device_count: Mapped[int] = mapped_column(Integer, default=0)
    
    active_days: Mapped[int] = mapped_column(Integer, default=0)
    
    lifecycle_state: Mapped[str] = mapped_column(String, default="NEW")
    behavioral_stability: Mapped[str] = mapped_column(String, default="STABLE")
    engagement_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    customer: Mapped["Customer"] = relationship(back_populates="profiles")

class CustomerSegment(Base, TimestampMixin):
    __tablename__ = "customer_segments"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"))
    segment_name: Mapped[str] = mapped_column(String, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    evidence: Mapped[str] = mapped_column(String, nullable=True)
    effective_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    
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
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), unique=True)
    
    profile_version: Mapped[int] = mapped_column(Integer, default=1)
    observation_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    observation_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    total_inflow: Mapped[float] = mapped_column(Float, default=0.0)
    total_outflow: Mapped[float] = mapped_column(Float, default=0.0)
    net_cash_flow: Mapped[float] = mapped_column(Float, default=0.0)
    
    average_daily_inflow: Mapped[float] = mapped_column(Float, default=0.0)
    average_daily_outflow: Mapped[float] = mapped_column(Float, default=0.0)
    
    inflow_transaction_count: Mapped[int] = mapped_column(Integer, default=0)
    outflow_transaction_count: Mapped[int] = mapped_column(Integer, default=0)
    
    cash_flow_volatility: Mapped[float] = mapped_column(Float, default=0.0)
    financial_stability_score: Mapped[float] = mapped_column(Float, default=0.0)
    liquidity_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    financial_health_score: Mapped[str] = mapped_column(String, default="UNAVAILABLE")
    data_sufficiency: Mapped[str] = mapped_column(String, default="INSUFFICIENT_DATA")
    
    forecast_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    last_calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    
    customer: Mapped["Customer"] = relationship(back_populates="financial_profiles")

