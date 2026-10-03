import re

with open("app/models/customer.py", "r") as f:
    content = f.read()

financial_def = """class FinancialProfile(Base, TimestampMixin):
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
    
    customer: Mapped["Customer"] = relationship(back_populates="financial_profiles")"""

new_imports = """from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Float, Integer, DateTime, JSON
from datetime import datetime, UTC
"""

content = re.sub(r'from sqlalchemy.orm import Mapped.*?\nfrom datetime import datetime, UTC', new_imports, content, flags=re.DOTALL)
content = re.sub(r'class FinancialProfile\(Base, TimestampMixin\):.*?(?=$)', financial_def + "\n", content, flags=re.DOTALL)

with open("app/models/customer.py", "w") as f:
    f.write(content)
