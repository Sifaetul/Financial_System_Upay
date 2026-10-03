from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services.transaction_service import TransactionService
from app.api.deps import get_current_user, require_permissions
from app.models.identity import User
from app.models.transaction import Transaction
from typing import List

router = APIRouter()

@router.post("", response_model=TransactionResponse)
def create_transaction(
    tx_in: TransactionCreate, 
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    x_correlation_id: str = Header(None, alias="X-Correlation-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = TransactionService(db)
    tx = service.process_transaction(tx_in, idempotency_key=idempotency_key, correlation_id=x_correlation_id)
    return tx

@router.get("", response_model=List[TransactionResponse])
def list_transactions(
    skip: int = Query(0, ge=0), 
    limit: int = Query(50, le=100),
    status: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Transaction)
    if status:
        query = query.filter(Transaction.status == status)
    return query.order_by(Transaction.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx
