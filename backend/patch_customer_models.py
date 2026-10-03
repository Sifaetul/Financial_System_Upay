import re

with open("app/models/customer.py", "r") as f:
    content = f.read()

new_imports = """from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Float, Integer, DateTime
from datetime import datetime, UTC
"""
content = re.sub(r'from sqlalchemy.orm import Mapped.*?\nfrom sqlalchemy import String, ForeignKey, Float', new_imports, content, flags=re.DOTALL)

profile_def = """class CustomerProfile(Base, TimestampMixin):
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
    
    customer: Mapped["Customer"] = relationship(back_populates="profiles")"""

segment_def = """class CustomerSegment(Base, TimestampMixin):
    __tablename__ = "customer_segments"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"))
    segment_name: Mapped[str] = mapped_column(String, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    evidence: Mapped[str] = mapped_column(String, nullable=True)
    effective_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    
    customer: Mapped["Customer"] = relationship(back_populates="segments")"""

content = re.sub(r'class CustomerProfile\(Base, TimestampMixin\):.*?(?=class CustomerSegment)', profile_def + "\n\n", content, flags=re.DOTALL)
content = re.sub(r'class CustomerSegment\(Base, TimestampMixin\):.*?(?=class Account)', segment_def + "\n\n", content, flags=re.DOTALL)

with open("app/models/customer.py", "w") as f:
    f.write(content)
