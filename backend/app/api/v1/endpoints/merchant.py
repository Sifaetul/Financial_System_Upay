from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import require_permissions
from app.models.transaction import Merchant, MerchantProfile
from typing import List, Dict, Any

router = APIRouter()

@router.get("/{merchant_id}/intelligence")
def get_merchant_intelligence(
    merchant_id: str,
    db: Session = Depends(get_db),
    _ = Depends(require_permissions(["manage_transactions"]))
):
    merchant = db.query(Merchant).filter_by(id=merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
        
    profile = db.query(MerchantProfile).filter_by(merchant_id=merchant_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Merchant profile not found")
        
    from app.services.merchant_intelligence import MerchantBehaviorService
    signals = MerchantBehaviorService.evaluate(db, merchant_id)
        
    return {
        "merchant_id": merchant.id,
        "name": merchant.name,
        "category": merchant.category,
        "transaction_count": profile.transaction_count,
        "transaction_volume": profile.transaction_volume,
        "unique_customer_count": profile.unique_customer_count,
        "average_transaction_amount": profile.average_transaction_amount,
        "successful_transaction_count": profile.successful_transaction_count,
        "failed_transaction_count": profile.failed_transaction_count,
        "refund_count": profile.refund_count,
        "data_sufficiency": profile.data_sufficiency,
        "signals": [s.model_dump() for s in signals]
    }
