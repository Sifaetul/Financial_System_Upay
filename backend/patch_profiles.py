import re

with open("app/models/transaction.py", "r") as f:
    content = f.read()

new_imports = """from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Float, Integer, DateTime, JSON
from datetime import datetime, UTC
"""

content = re.sub(r'from sqlalchemy.orm import Mapped.*?\nfrom datetime import datetime, UTC', new_imports, content, flags=re.DOTALL)

merchant_profile_def = """class MerchantProfile(Base, TimestampMixin):
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
    last_calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))"""

agent_profile_def = """class AgentProfile(Base, TimestampMixin):
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
    last_calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))"""

content = re.sub(r'class MerchantProfile\(Base, TimestampMixin\):.*?(?=class Agent\()', merchant_profile_def + "\n\n", content, flags=re.DOTALL)
content = re.sub(r'class AgentProfile\(Base, TimestampMixin\):.*?(?=class Device\()', agent_profile_def + "\n\n", content, flags=re.DOTALL)

with open("app/models/transaction.py", "w") as f:
    f.write(content)
