from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import require_permissions
from app.models.customer import Customer, FinancialProfile
from typing import List, Dict, Any

router = APIRouter()

@router.get("/{customer_id}/financial")
def get_customer_financial(
    customer_id: str,
    db: Session = Depends(get_db),
    _ = Depends(require_permissions(["manage_transactions"]))
):
    customer = db.query(Customer).filter_by(id=customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    profile = db.query(FinancialProfile).filter_by(customer_id=customer_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Financial profile not found")
        
    from app.services.financial_intelligence import FinancialBehaviorService
    signals = FinancialBehaviorService.evaluate(db, customer_id)
        
    return {
        "customer_id": customer.id,
        "total_inflow": profile.total_inflow,
        "total_outflow": profile.total_outflow,
        "net_cash_flow": profile.net_cash_flow,
        "average_daily_inflow": profile.average_daily_inflow,
        "average_daily_outflow": profile.average_daily_outflow,
        "financial_health_score": profile.financial_health_score,
        "data_sufficiency": profile.data_sufficiency,
        "forecast_data": profile.forecast_data,
        "signals": [s.model_dump() for s in signals]
    }
