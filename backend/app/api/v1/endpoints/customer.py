from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import require_permissions
from app.services.customer_intelligence import Customer360Service
from typing import List, Dict, Any

router = APIRouter()

@router.get("/{customer_id}/360")
def get_customer_360(
    customer_id: str,
    db: Session = Depends(get_db),
    _ = Depends(require_permissions(["manage_transactions"]))
):
    data = Customer360Service.get_profile(db, customer_id)
    if not data:
        raise HTTPException(status_code=404, detail="Customer not found")
    return data
